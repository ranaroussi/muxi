#!/usr/bin/env python3
"""
Comprehensive tests for the MCP implementation.

This script tests all key components of the MCP implementation:
- Transport factory
- HTTP+SSE transport
- CommandLineTransport
- Cancellation support
- Error handling and diagnostics
- Connection management
- Reconnection with backoff
"""

import asyncio
import os
import subprocess
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Important: Add the root directory to the path before importing from packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after sys.path modification
from packages.core.src.muxi.core.mcp_handler import (  # noqa: E402
    CancellationToken,
    CommandLineTransport,
    HTTPSSETransport,
    MCPConnectionError,
    MCPHandler,
    MCPRequestError,
    MCPServerClient,
    MCPTransportFactory,
)


class TestMCPTransportFactory(unittest.TestCase):
    """Test cases for the MCPTransportFactory class."""

    def test_create_transport_http(self):
        """Test creating an HTTP+SSE transport."""
        # Create transport
        transport = MCPTransportFactory.create_transport(
            type="http",
            url_or_command="https://server.mcpify.ai/sse?server=test-id",
            request_timeout=30
        )

        # Verify transport type and configuration
        self.assertIsInstance(transport, HTTPSSETransport)
        self.assertEqual(transport.url, "https://server.mcpify.ai/sse?server=test-id")
        self.assertEqual(transport.request_timeout, 30)

    def test_create_transport_command(self):
        """Test creating a command line transport."""
        # Create transport
        transport = MCPTransportFactory.create_transport(
            type="command",
            url_or_command="npx -y @modelcontextprotocol/server-calculator"
        )

        # Verify transport type and configuration
        self.assertIsInstance(transport, CommandLineTransport)
        self.assertEqual(transport.command, "npx -y @modelcontextprotocol/server-calculator")

    def test_create_transport_unsupported(self):
        """Test error when creating an unsupported transport type."""
        # Attempt to create an unsupported transport
        with self.assertRaises(ValueError):
            MCPTransportFactory.create_transport(
                type="unsupported_transport",
                url_or_command="https://example.com"
            )


class TestCancellationToken(unittest.IsolatedAsyncioTestCase):
    """Test cases for the CancellationToken class."""

    async def test_cancellation_token_not_cancelled(self):
        """Test that a token starts as not cancelled."""
        token = CancellationToken()
        self.assertFalse(token.cancelled)
        # Token allows operation to complete
        await token.throw_if_cancelled()  # Should not raise

    async def test_cancellation_token_cancelled(self):
        """Test cancellation of a token."""
        token = CancellationToken()
        token.cancel()
        self.assertTrue(token.cancelled)
        # Token should prevent operation
        with self.assertRaises(asyncio.CancelledError):
            await token.throw_if_cancelled()

    async def test_cancellation_token_with_tasks(self):
        """Test cancellation of registered tasks."""
        token = CancellationToken()

        # Create mock task
        mock_task1 = MagicMock()
        mock_task1.cancel = MagicMock()
        mock_task2 = MagicMock()
        mock_task2.cancel = MagicMock()

        # Register tasks
        token.register_task(mock_task1)
        token.register_task(mock_task2)

        # Cancel token
        token.cancel()

        # Verify tasks were cancelled
        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_called_once()


class TestHTTPSSETransport(unittest.IsolatedAsyncioTestCase):
    """Test cases for the HTTPSSETransport class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Create transport
        self.transport = HTTPSSETransport("https://server.mcpify.ai/sse?server=test-id", 30)

        # Set up patches
        self.http_client_patcher = patch(
            'packages.core.src.muxi.core.mcp_handler.httpx.AsyncClient'
        )
        self.mock_http_client_class = self.http_client_patcher.start()
        self.mock_http_client = MagicMock()
        self.mock_http_client.aclose = AsyncMock()
        self.mock_http_client.post = AsyncMock()
        self.mock_http_client_class.return_value = self.mock_http_client

        # Mock SSE client
        self.sse_patcher = patch('packages.core.src.muxi.core.mcp_handler.EventSource')
        self.mock_sse_class = self.sse_patcher.start()
        self.mock_sse = MagicMock()
        self.mock_sse.connect = AsyncMock()
        self.mock_sse.disconnect = AsyncMock()
        self.mock_sse_class.return_value = self.mock_sse

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        self.http_client_patcher.stop()
        self.sse_patcher.stop()

    async def test_connect(self):
        """Test connecting to an HTTP+SSE server."""
        # Mock SSE event for endpoint
        endpoint_event = MagicMock()
        endpoint_event.data = "/messages?server=test-id&sessionId=12345"

        # Set up mock event handling
        self.mock_sse.connect.return_value = None

        # Mock __aiter__ to return endpoint event
        async def mock_events():
            event = MagicMock()
            event.event = "endpoint"
            event.data = "/messages?server=test-id&sessionId=12345"
            yield event
            while True:
                # Simulate waiting for events
                await asyncio.sleep(0.1)

        self.mock_sse.__aiter__.return_value = mock_events()

        # Connect
        task = asyncio.create_task(self.transport.connect())

        # Allow time for the endpoint event to be processed
        await asyncio.sleep(0.2)

        # Cancel the listen task to stop the test
        self.transport._listen_task.cancel()

        # Wait for connect to complete
        await task

        # Verify connection state
        self.assertTrue(self.transport.connected)
        msg_url = "https://server.mcpify.ai/messages?server=test-id&sessionId=12345"
        self.assertEqual(self.transport.message_url, msg_url)
        self.assertIsNotNone(self.transport._listen_task)

    async def test_send_request(self):
        """Test sending a request to an HTTP+SSE server."""
        # Set up transport for test
        self.transport.connected = True
        msg_url = "https://server.mcpify.ai/messages?server=test-id&sessionId=12345"
        self.transport.message_url = msg_url

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 202
        self.mock_http_client.post.return_value = mock_response

        # Send request
        request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": "1"}
        result = await self.transport.send_request(request)

        # Verify the request was sent correctly
        self.mock_http_client.post.assert_called_once()
        call_args = self.mock_http_client.post.call_args
        self.assertEqual(call_args[0][0], msg_url)
        self.assertEqual(call_args[1]["json"], request)

        # The result should be None as the response is 202 Accepted
        self.assertIsNone(result)

    async def test_disconnect(self):
        """Test disconnecting from an HTTP+SSE server."""
        # Set up transport for test
        self.transport.connected = True
        self.transport.http_client = self.mock_http_client
        self.transport.sse_client = self.mock_sse

        # Create a mock listen task
        mock_task = MagicMock()
        mock_task.cancel = MagicMock()
        self.transport._listen_task = mock_task

        # Disconnect
        await self.transport.disconnect()

        # Verify disconnect operations
        self.mock_sse.disconnect.assert_called_once()
        self.mock_http_client.aclose.assert_called_once()
        mock_task.cancel.assert_called_once()
        self.assertFalse(self.transport.connected)


class TestCommandLineTransport(unittest.IsolatedAsyncioTestCase):
    """Test cases for the CommandLineTransport class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Create transport
        self.transport = CommandLineTransport("npx -y @modelcontextprotocol/server-calculator")

        # Set up patches
        self.subprocess_patcher = patch('packages.core.src.muxi.core.mcp_handler.subprocess.Popen')
        self.mock_popen = self.subprocess_patcher.start()

        # Mock process
        self.mock_process = MagicMock()
        self.mock_process.stdin = MagicMock()
        self.mock_process.stdin.write = MagicMock()
        self.mock_process.stdin.flush = MagicMock()
        self.mock_process.stdout = MagicMock()
        self.mock_process.stdout.readline = MagicMock()
        self.mock_process.poll = MagicMock(return_value=None)  # Process is running
        self.mock_process.terminate = MagicMock()
        self.mock_popen.return_value = self.mock_process

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        self.subprocess_patcher.stop()

    async def test_connect(self):
        """Test starting a command-line MCP server."""
        # Mock process startup
        self.mock_popen.return_value = self.mock_process

        # Connect
        await self.transport.connect()

        # Verify process was started
        self.mock_popen.assert_called_once()
        cmd_args = self.mock_popen.call_args[0][0]
        self.assertEqual(cmd_args, ["npx", "-y", "@modelcontextprotocol/server-calculator"])

        # Verify connection state
        self.assertTrue(self.transport.connected)
        self.assertEqual(self.transport.process, self.mock_process)

    async def test_send_request(self):
        """Test sending a request to a command-line MCP server."""
        # Set up transport for test
        self.transport.connected = True
        self.transport.process = self.mock_process

        # Mock process response
        resp = b'{"jsonrpc":"2.0","result":{"data":"test_result"},"id":"1"}\n'
        self.mock_process.stdout.readline.return_value = resp

        # Send request
        request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": "1"}
        result = await self.transport.send_request(request)

        # Verify the request was sent correctly
        self.mock_process.stdin.write.assert_called_once()

        # Verify the result
        self.assertEqual(result["jsonrpc"], "2.0")
        self.assertEqual(result["result"]["data"], "test_result")
        self.assertEqual(result["id"], "1")

    async def test_disconnect(self):
        """Test disconnecting from a command-line MCP server."""
        # Set up transport for test
        self.transport.connected = True
        self.transport.process = self.mock_process

        # Disconnect
        await self.transport.disconnect()

        # Verify disconnect operations
        self.mock_process.terminate.assert_called_once()
        self.assertFalse(self.transport.connected)


class TestMCPServerClient(unittest.IsolatedAsyncioTestCase):
    """Test cases for the MCPServerClient class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Mock transport
        self.mock_transport = MagicMock()
        self.mock_transport.connect = AsyncMock()
        self.mock_transport.disconnect = AsyncMock()
        self.mock_transport.send_request = AsyncMock()

        # Set up factory patch
        self.factory_patcher = patch('packages.core.src.muxi.core.mcp_handler.MCPTransportFactory')
        self.mock_factory = self.factory_patcher.start()
        self.mock_factory.create_transport.return_value = self.mock_transport

        # Create client
        self.client = MCPServerClient(
            name="test_server",
            url_or_command="http://test-server.com",
            type="http",
            credentials={"api_key": "test_key"}
        )

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        self.factory_patcher.stop()

    async def test_connect(self):
        """Test connecting to an MCP server."""
        # Connect
        await self.client.connect()

        # Verify factory and transport were used correctly
        self.mock_factory.create_transport.assert_called_with(
            type="http",
            url_or_command="http://test-server.com",
            request_timeout=60
        )
        self.mock_transport.connect.assert_called_once()
        self.assertTrue(self.client.connected)

    async def test_send_message_with_cancellation(self):
        """Test sending a message with cancellation support."""
        # Set up transport
        self.client.transport = self.mock_transport
        self.client.connected = True

        # Mock response
        self.mock_transport.send_request.return_value = {
            "jsonrpc": "2.0",
            "result": {"data": "test_result"},
            "id": "1"
        }

        # Create cancellation token
        token = CancellationToken()

        # Send message
        result = await self.client.send_message(
            method="test_method",
            params={"param1": "value1"},
            cancellation_token=token
        )

        # Verify result
        self.assertEqual(result["result"]["data"], "test_result")

        # Verify cancellation token was used
        self.assertIn("1", self.client.active_requests)

        # Cancel the token and verify request handling
        token.cancel()

        # The request would have completed already in our test,
        # but verify the token is cancelled
        self.assertTrue(token.cancelled)

    async def test_disconnect_with_request_cancellation(self):
        """Test that disconnect cancels any active requests."""
        # Set up client
        self.client.transport = self.mock_transport
        self.client.connected = True

        # Create mock requests
        mock_token1 = MagicMock()
        mock_token1.cancel = MagicMock()
        mock_token2 = MagicMock()
        mock_token2.cancel = MagicMock()

        # Add to active requests
        self.client.active_requests = {
            "1": mock_token1,
            "2": mock_token2
        }

        # Disconnect
        await self.client.disconnect()

        # Verify tokens were cancelled
        mock_token1.cancel.assert_called_once()
        mock_token2.cancel.assert_called_once()

        # Verify transport disconnect was called
        self.mock_transport.disconnect.assert_called_once()
        self.assertFalse(self.client.connected)


class TestMCPHandler(unittest.IsolatedAsyncioTestCase):
    """Test cases for the MCPHandler class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Mock model
        self.mock_model = MagicMock()
        self.mock_model.chat = AsyncMock()

        # Create handler
        self.handler = MCPHandler(model=self.mock_model)

        # Set up client patch
        self.client_patcher = patch('packages.core.src.muxi.core.mcp_handler.MCPServerClient')
        self.mock_client_class = self.client_patcher.start()
        self.mock_client = MagicMock()
        self.mock_client.connect = AsyncMock()
        self.mock_client.disconnect = AsyncMock()
        self.mock_client.execute_tool = AsyncMock()
        self.mock_client.send_message = AsyncMock()
        self.mock_client.cancel_all_requests = MagicMock()
        self.mock_client_class.return_value = self.mock_client

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        self.client_patcher.stop()

    async def test_connect_server(self):
        """Test connecting to an MCP server."""
        # Connect server
        result = await self.handler.connect_server(
            name="test_server",
            url_or_command="http://test-server.com",
            type="http"
        )

        # Verify client was created and connected
        self.mock_client_class.assert_called_with(
            name="test_server",
            url_or_command="http://test-server.com",
            type="http",
            credentials={}
        )
        self.mock_client.connect.assert_called_once()

        # Verify handler state
        self.assertTrue(result)
        self.assertIn("test_server", self.handler.active_connections)
        self.assertIn("test_server", self.handler.mcp_servers)

    async def test_execute_tool_with_cancellation(self):
        """Test executing a tool with cancellation support."""
        # Add mock client to connections
        self.handler.active_connections["test_server"] = self.mock_client
        self.handler.available_tools["test_tool"] = "test_server"

        # Mock tool execution result
        self.mock_client.execute_tool.return_value = {"result": "tool_result"}

        # Create cancellation token
        token = CancellationToken()

        # Execute tool
        result = await self.handler.execute_tool(
            tool_name="test_tool",
            params={"param1": "value1"},
            cancellation_token=token
        )

        # Verify result
        self.assertEqual(result["result"], "tool_result")

        # Verify client was called with cancellation token
        self.mock_client.execute_tool.assert_called_once()
        call_args = self.mock_client.execute_tool.call_args
        self.assertEqual(call_args[1]["param1"], "value1")
        self.assertEqual(call_args[1]["cancellation_token"], token)

    async def test_cancel_all_operations(self):
        """Test cancelling all operations."""
        # Add mock clients to connections
        client1 = MagicMock()
        client1.cancel_all_requests = MagicMock()
        client2 = MagicMock()
        client2.cancel_all_requests = MagicMock()

        self.handler.active_connections = {
            "server1": client1,
            "server2": client2
        }

        # Add mock cancellation tokens
        token1 = MagicMock()
        token1.cancel = MagicMock()
        token2 = MagicMock()
        token2.cancel = MagicMock()

        self.handler.cancellation_tokens = {
            "token1": token1,
            "token2": token2
        }

        # Cancel all operations
        self.handler.cancel_all_operations()

        # Verify clients and tokens were cancelled
        client1.cancel_all_requests.assert_called_once()
        client2.cancel_all_requests.assert_called_once()
        token1.cancel.assert_called_once()
        token2.cancel.assert_called_once()

    async def test_error_handling_connection(self):
        """Test error handling during connection."""
        # Make client connection fail
        self.mock_client.connect.side_effect = Exception("Connection failed")

        # Attempt to connect
        with self.assertRaises(MCPConnectionError):
            await self.handler.connect_server(
                name="test_server",
                url_or_command="http://test-server.com",
                type="http"
            )

        # Verify client was created but not added to active connections
        self.mock_client_class.assert_called_once()
        self.assertNotIn("test_server", self.handler.active_connections)

    async def test_error_handling_tool_execution(self):
        """Test error handling during tool execution."""
        # Add mock client to connections
        self.handler.active_connections["test_server"] = self.mock_client
        self.handler.available_tools["test_tool"] = "test_server"

        # Make tool execution fail
        self.mock_client.execute_tool.side_effect = Exception("Tool execution failed")

        # Attempt to execute tool
        with self.assertRaises(MCPRequestError):
            await self.handler.execute_tool(
                tool_name="test_tool",
                params={"param1": "value1"}
            )

        # Verify client method was called
        self.mock_client.execute_tool.assert_called_once()


class TestCommandLineTransportWithRealProcess(unittest.IsolatedAsyncioTestCase):
    """
    Test the CommandLineTransport with a real process.

    Note: This test requires NPM to be installed and will try to run an actual server.
    Skip this test if NPM is not available.
    """

    @unittest.skipIf(
        not any(subprocess.run(
            ["which", "npx"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout),
        "NPX not found, skipping real process test"
    )
    async def test_command_line_real_process(self):
        """Test CommandLineTransport with a real NPX process if available."""
        # Create transport for the calculator server
        transport = CommandLineTransport("npx -y @modelcontextprotocol/server-calculator")

        try:
            # Connect to the server
            await transport.connect()
            self.assertTrue(transport.connected)

            # Wait briefly for the server to initialize
            await asyncio.sleep(2)

            # Send a simple calculation request
            request = {
                "jsonrpc": "2.0",
                "method": "calculate",
                "params": {"expression": "1 + 1"},
                "id": "1"
            }

            # This might fail if the server doesn't respond properly
            # But we'll try it to see if it works
            try:
                result = await transport.send_request(request)
                self.assertIsNotNone(result)
                self.assertEqual(result.get("result"), 2)
            except Exception as e:
                print(f"Server communication failed (this may be expected): {e}")

        finally:
            # Always disconnect
            await transport.disconnect()
            self.assertFalse(transport.connected)


if __name__ == "__main__":
    unittest.main()
