"""
Tests for the MCPHandler class.

This module contains tests for the MCPHandler class that uses the official MCP SDK.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Fix imports to use absolute imports from the packages structure
from packages.core.src.muxi.core.mcp import MCPMessage
from packages.core.src.muxi.core.mcp_handler import (
    MCPHandler,
    MCPServerClient
)


class TestMCPServerClient(unittest.IsolatedAsyncioTestCase):
    """Test cases for the MCPServerClient class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Create mock MCP client
        self.mock_client = MagicMock()
        self.mock_client.connect = AsyncMock(return_value=None)
        self.mock_client.disconnect = AsyncMock(return_value=None)
        self.mock_client.request = AsyncMock()

        # Create client and inject mock
        self.client = MCPServerClient(
            name="test_server",
            url_or_command="http://test-server.com",
            type="http",
            credentials={"api_key": "test_key"}
        )
        self.client.client = self.mock_client
        self.client.connected = True

    async def test_send_message(self):
        """Test sending a message to an MCP server."""
        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "jsonrpc": "2.0",
            "result": {"data": "test_result"},
            "id": "1"
        }
        self.mock_client.request.return_value = mock_response

        # Send message
        result = await self.client.send_message(
            method="test_method",
            params={"param1": "value1"}
        )

        # Verify result
        self.assertEqual(result["result"]["data"], "test_result")

        # Verify credentials were merged with params
        self.mock_client.request.assert_called_once()
        request_arg = self.mock_client.request.call_args[0][0]
        self.assertEqual(request_arg.method, "test_method")
        self.assertEqual(request_arg.params["param1"], "value1")
        self.assertEqual(request_arg.params["api_key"], "test_key")

    async def test_execute_tool(self):
        """Test executing a tool on an MCP server."""
        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "jsonrpc": "2.0",
            "result": {"data": "tool_result"},
            "id": "1"
        }
        self.mock_client.request.return_value = mock_response

        # Execute tool
        result = await self.client.execute_tool(param1="value1", param2="value2")

        # Verify result
        self.assertEqual(result["result"]["data"], "tool_result")

        # Verify the tool method is the server name
        self.mock_client.request.assert_called_once()
        request_arg = self.mock_client.request.call_args[0][0]
        self.assertEqual(request_arg.method, "test_server")
        self.assertEqual(request_arg.params["param1"], "value1")
        self.assertEqual(request_arg.params["param2"], "value2")
        self.assertEqual(request_arg.params["api_key"], "test_key")


class TestMCPHandler(unittest.IsolatedAsyncioTestCase):
    """Test cases for the MCPHandler class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Mock model
        self.mock_model = MagicMock()
        self.mock_model.chat = AsyncMock()

        # Create handler with mock model
        self.handler = MCPHandler(model=self.mock_model)

        # Set up patches
        self.transport_patcher = patch('packages.core.src.muxi.core.mcp_handler.HTTPSSETransport')
        self.mock_transport_class = self.transport_patcher.start()

        self.client_patcher = patch('packages.core.src.muxi.core.mcp_handler.MCPClient')
        self.mock_client_class = self.client_patcher.start()

        # Set up mocks
        self.mock_transport = MagicMock()
        self.mock_transport_class.return_value = self.mock_transport

        self.mock_client = MagicMock()
        self.mock_client.connect = AsyncMock()
        self.mock_client.disconnect = AsyncMock()
        self.mock_client_class.return_value = self.mock_client

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        self.transport_patcher.stop()
        self.client_patcher.stop()

    async def test_connect_mcp_server(self):
        """Test connecting to an MCP server."""
        # Set up client connect to succeed
        self.mock_client.connect.return_value = None

        # Connect to server
        result = await self.handler.connect_mcp_server(
            name="test_server",
            url_or_command="http://test-server.com",
            type="http",
            credentials={"api_key": "test_key"}
        )

        # Verify result and state
        self.assertTrue(result)
        self.assertIn("test_server", self.handler.active_connections)
        self.assertIn("test_server", self.handler.mcp_servers)

        # Verify transport was created with correct parameters
        self.mock_transport_class.assert_called_with("http://test-server.com")
        self.mock_client_class.assert_called_with(transport=self.mock_transport)
        self.mock_client.connect.assert_called_once()

    async def test_process_message(self):
        """Test processing a message with no tool calls."""
        # Mock model response
        self.mock_model.chat.return_value = "I'm a helpful assistant."

        # Create test message
        message = MCPMessage(role="user", content="Hello")

        # Process message
        response = await self.handler.process_message(message)

        # Verify response
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "I'm a helpful assistant.")

        # Verify model was called with correct messages
        self.mock_model.chat.assert_called_once()
        model_messages = self.mock_model.chat.call_args[0][0]
        self.assertEqual(len(model_messages), 1)
        self.assertEqual(model_messages[0]["role"], "user")
        self.assertEqual(model_messages[0]["content"], "Hello")

    async def test_process_message_with_tool_calls(self):
        """Test processing a message with tool calls."""
        # Create a mock MCP server client
        mock_server_client = MagicMock()
        mock_server_client.execute_tool = AsyncMock(return_value={"result": "tool_result"})

        # Add it to the handler
        self.handler.active_connections["test_tool"] = mock_server_client

        # Mock model responses
        self.mock_model.chat.side_effect = [
            {
                "content": "I'll help you with that.",
                "tool_calls": [
                    {
                        "tool_name": "test_tool",
                        "tool_id": "call_1",
                        "tool_args": {"param1": "value1"}
                    }
                ]
            },
            "Here's the result: tool_result"
        ]

        # Create test message
        message = MCPMessage(role="user", content="Use the tool please")

        # Process message
        response = await self.handler.process_message(message)

        # Verify response
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "Here's the result: tool_result")

        # Verify tool was called
        mock_server_client.execute_tool.assert_called_once_with(param1="value1")

        # Verify model was called twice (once for initial response, once for final response)
        self.assertEqual(self.mock_model.chat.call_count, 2)


if __name__ == "__main__":
    unittest.main()
