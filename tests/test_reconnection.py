"""
Test reconnection functionality of the enhanced MCP handler.

This test module verifies the reconnection capabilities of the
ReconnectingMCPHandler with various failure scenarios.
"""

import asyncio
import json
import logging
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from muxi.core.mcp_handler import MCPConnectionError
from muxi.core.reconnect_mcp_handler import ReconnectingMCPHandler
from muxi.core.reconnection import RetryConfiguration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnstableTransport:
    """Mock transport that simulates connection instability."""

    def __init__(self, failure_pattern=None, max_consecutive_failures=1):
        """
        Initialize the unstable transport.

        Args:
            failure_pattern: List of boolean values indicating success (True)
                            or failure (False) for sequential operations
            max_consecutive_failures: Maximum number of consecutive failures
                                    when not using a pattern
        """
        self.is_connected = False
        self.failure_pattern = failure_pattern or []
        self.max_consecutive_failures = max_consecutive_failures
        self.operation_count = 0
        self.failure_count = 0
        self.consecutive_failures = 0
        self.tool_calls = []

    async def connect(self) -> bool:
        """
        Attempt to connect to the mock server.

        Returns:
            True if connection was successful, False otherwise

        Raises:
            MCPConnectionError: If connection failed
        """
        logger.info("Attempting to connect to mock server")

        # Determine if this operation should fail
        should_fail = self._should_operation_fail()

        if should_fail:
            logger.info("Connection attempt failed (simulated failure)")
            self.is_connected = False
            raise MCPConnectionError("Simulated connection failure")

        logger.info("Connection successful")
        self.is_connected = True
        self.consecutive_failures = 0
        return True

    async def send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the mock server.

        Args:
            data: Request data

        Returns:
            Response data

        Raises:
            MCPConnectionError: If the request failed due to connection issues
        """
        logger.info(f"Attempting to send request: {json.dumps(data)[:50]}...")

        # Check if we're already disconnected
        if not self.is_connected:
            logger.info("Request failed: Not connected")
            raise MCPConnectionError("Not connected")

        # Determine if this operation should fail
        should_fail = self._should_operation_fail()

        if should_fail:
            logger.info("Request failed (simulated failure)")
            self.is_connected = False
            raise MCPConnectionError("Simulated request failure")

        # Record tool call
        if "method" in data and data["method"] == "execute":
            params = data.get("params", {})
            tool_name = params.get("tool", "")
            self.tool_calls.append(tool_name)

        # Return a mock response
        logger.info("Request successful")
        self.consecutive_failures = 0

        if "method" in data:
            method = data["method"]
            if method == "list":
                return {"tools": [{"name": "test_tool", "description": "Test tool"}]}
            elif method == "execute":
                params = data.get("params", {})
                tool = params.get("tool", "")
                return {"result": f"Executed {tool}"}

        return {"success": True}

    async def disconnect(self) -> None:
        """Disconnect from the mock server."""
        logger.info("Disconnecting from mock server")
        self.is_connected = False

    def _should_operation_fail(self) -> bool:
        """
        Determine if the current operation should fail.

        Returns:
            True if the operation should fail, False otherwise
        """
        # Use the failure pattern if available
        if self.failure_pattern and self.operation_count < len(self.failure_pattern):
            should_fail = not self.failure_pattern[self.operation_count]
        else:
            # Otherwise use consecutive failure logic
            should_fail = self.consecutive_failures < self.max_consecutive_failures

        self.operation_count += 1

        if should_fail:
            self.failure_count += 1
            self.consecutive_failures += 1

        return should_fail


class TestReconnection(unittest.TestCase):
    """Test suite for reconnection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Configure a retry configuration with shorter delays for testing
        self.retry_config = RetryConfiguration(
            max_retries=3,
            initial_delay=0.1,
            max_delay=0.5,
            backoff_factor=2.0,
            jitter=False  # Disable jitter for predictable tests
        )

        # Create the reconnecting handler
        self.handler = ReconnectingMCPHandler(retry_config=self.retry_config)

        # Reset transport factory
        self.transport_instance = None
        self.transport_factory_patch = None

    def tearDown(self):
        """Clean up after tests."""
        if self.transport_factory_patch:
            self.transport_factory_patch.stop()

    def _setup_transport_mock(self, failure_pattern=None, max_consecutive_failures=1):
        """
        Set up a mock transport with the specified failure behavior.

        Args:
            failure_pattern: List of boolean values indicating success (True)
                           or failure (False) for sequential operations
            max_consecutive_failures: Maximum number of consecutive failures
                                    when not using a pattern
        """
        self.transport_instance = UnstableTransport(
            failure_pattern=failure_pattern,
            max_consecutive_failures=max_consecutive_failures
        )

        # Mock the transport factory to return our unstable transport
        if self.transport_factory_patch:
            self.transport_factory_patch.stop()

        transport_factory_mock = MagicMock()
        transport_factory_mock.create_transport.return_value = self.transport_instance

        self.transport_factory_patch = patch(
            'muxi.core.mcp_handler.MCPTransportFactory',
            return_value=transport_factory_mock
        )
        self.transport_factory_patch.start()

    async def _test_connect_with_failures(self, failure_pattern):
        """
        Test connection with a specific failure pattern.

        Args:
            failure_pattern: List of boolean values indicating success (True)
                           or failure (False) for sequential operations
        """
        self._setup_transport_mock(failure_pattern=failure_pattern)

        # Attempt to connect
        result = await self.handler.connect_server(
            server_id="test_server",
            server_url="http://localhost:8080",
            transport_type="http_sse"
        )

        self.assertTrue(result)
        self.assertEqual(
            self.transport_instance.operation_count,
            failure_pattern.count(False) + 1
        )

    async def _test_execute_tool_with_reconnection(self, server_connected=True):
        """
        Test executing a tool with automatic reconnection.

        Args:
            server_connected: Whether the server is initially connected
        """
        # Setup: First connection succeeds, then fails on first request, then succeeds
        self._setup_transport_mock(failure_pattern=[True, False, True])

        # Connect to the server
        if server_connected:
            await self.handler.connect_server(
                server_id="test_server",
                server_url="http://localhost:8080",
                transport_type="http_sse"
            )

            # Reset the operation count after initial connection
            self.transport_instance.operation_count = 0
            self.transport_instance.failure_count = 0
        else:
            # Setup server_info but don't actually connect
            self.handler.server_info["test_server"] = {
                "url": "http://localhost:8080",
                "transport_type": "http_sse"
            }

        # Mock the _get_server_for_tool method to return our test server
        with patch.object(
            self.handler, '_get_server_for_tool', return_value="test_server"
        ):
            # Execute a tool that should trigger reconnection
            result = await self.handler.execute_tool(
                tool_name="test_tool",
                params={"param1": "value1"}
            )

        # Verify the results
        self.assertIn("result", result)
        self.assertEqual(result["result"], "Executed test_tool")

        # Check that we had the expected number of operations
        expected_ops = 3 if server_connected else 4  # +1 for connect if not connected
        self.assertEqual(self.transport_instance.operation_count, expected_ops)

        # Check that the tool was called
        self.assertIn("test_tool", self.transport_instance.tool_calls)

    def test_connect_with_retry(self):
        """Test connection with retry on failure."""
        asyncio.run(self._test_connect_with_failures([False, True]))

    def test_connect_with_multiple_retries(self):
        """Test connection with multiple retries before success."""
        asyncio.run(self._test_connect_with_failures([False, False, True]))

    def test_connect_exceeding_max_retries(self):
        """Test connection failing after exceeding maximum retries."""
        self._setup_transport_mock(failure_pattern=[False, False, False, False])

        with self.assertRaises(MCPConnectionError):
            asyncio.run(self.handler.connect_server(
                server_id="test_server",
                server_url="http://localhost:8080",
                transport_type="http_sse"
            ))

    def test_execute_tool_with_reconnection(self):
        """Test executing a tool with reconnection on failure."""
        asyncio.run(self._test_execute_tool_with_reconnection(server_connected=True))

    def test_execute_tool_when_disconnected(self):
        """Test executing a tool when server is disconnected."""
        asyncio.run(self._test_execute_tool_with_reconnection(server_connected=False))

    def test_list_tools_with_retry(self):
        """Test listing tools with retry on failure."""
        # Setup: Connection succeeds, but first list request fails, then succeeds
        self._setup_transport_mock(failure_pattern=[True, False, True])

        # Connect to the server
        asyncio.run(self.handler.connect_server(
            server_id="test_server",
            server_url="http://localhost:8080",
            transport_type="http_sse"
        ))

        # Reset the operation count after initial connection
        self.transport_instance.operation_count = 0
        self.transport_instance.failure_count = 0

        # List tools which should retry once
        tools = asyncio.run(self.handler.list_tools(refresh=True))

        # Verify results
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["name"], "test_tool")

        # Check that we had the expected number of operations
        self.assertEqual(self.transport_instance.operation_count, 3)  # 1 failure + 1 retry

    def test_retry_stats(self):
        """Test getting retry statistics."""
        # Setup and connect
        self._setup_transport_mock(failure_pattern=[False, True])

        asyncio.run(self.handler.connect_server(
            server_id="test_server",
            server_url="http://localhost:8080",
            transport_type="http_sse"
        ))

        # Get stats
        stats = self.handler.get_retry_stats()

        # Verify stats
        self.assertIn("retry_config", stats)
        self.assertEqual(stats["retry_config"]["max_retries"], 3)
        self.assertEqual(stats["retry_config"]["initial_delay"], 0.1)
        self.assertIn("reconnection_in_progress", stats)
        self.assertEqual(len(stats["reconnection_in_progress"]), 0)


if __name__ == "__main__":
    unittest.main()
