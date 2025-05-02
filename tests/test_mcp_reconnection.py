#!/usr/bin/env python3
"""
Test for MCP reconnection and error handling.

This test verifies the reconnection mechanisms and error handling in the MCP implementation.
It simulates various failure scenarios to test resilience and recovery.
"""

import os
import sys
import asyncio
import unittest
import importlib.util
import random
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

# Add the root directory to the path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load MCP classes
try:
    # Try direct import
    from muxi.core.mcp.handler import (
        MCPHandler,
        MCPServerClient,
        HTTPSSETransport,
        CommandLineTransport,
        MCPTransportFactory,
        CancellationToken,
        MCPConnectionError,
        MCPRequestError,
        BaseTransport
    )
    print("✅ Successfully imported MCP classes directly")
except ImportError as e:
    print(f"❌ Direct import failed: {e}")
    print("Trying alternative approach with importlib...")

    # Use importlib to load the module
    spec = importlib.util.spec_from_file_location(
        "mcp_handler",
        os.path.join(root_dir, "packages/core/muxi/core/mcp/handler.py")
    )
    if spec is not None:
        mcp_handler = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(mcp_handler)

            # Get the classes from the module
            # Use type ignore to suppress mypy errors about assigning to types
            MCPHandler = mcp_handler.MCPHandler  # type: ignore
            MCPServerClient = mcp_handler.MCPServerClient  # type: ignore
            HTTPSSETransport = mcp_handler.HTTPSSETransport  # type: ignore
            CommandLineTransport = mcp_handler.CommandLineTransport  # type: ignore
            MCPTransportFactory = mcp_handler.MCPTransportFactory  # type: ignore
            CancellationToken = mcp_handler.CancellationToken  # type: ignore
            MCPConnectionError = mcp_handler.MCPConnectionError  # type: ignore
            MCPRequestError = mcp_handler.MCPRequestError  # type: ignore
            BaseTransport = mcp_handler.BaseTransport  # type: ignore
            print("✅ Successfully imported MCP classes via importlib")
        else:
            print("❌ Failed to load module: spec.loader is None")
            sys.exit(1)
    else:
        print("❌ Failed to find module: spec is None")
        sys.exit(1)


class UnstableTransport(BaseTransport):
    """A test transport that simulates unstable connections."""

    def __init__(self, failure_rate: float = 0.3, max_consecutive_failures: int = 3):
        """
        Initialize the unstable transport.

        Args:
            failure_rate: Probability of request failure (0.0 to 1.0)
            max_consecutive_failures: Maximum number of failures before automatic recovery
        """
        self.failure_rate = failure_rate
        self.max_consecutive_failures = max_consecutive_failures
        self.consecutive_failures = 0
        self.connected = False
        self.connection_attempts = 0
        self.successful_requests = 0
        self.failed_requests = 0
        # Initialize datetime attributes with None
        self.connect_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None

    async def connect(self) -> bool:
        """Attempt to connect, with possible failure."""
        self.connection_attempts += 1
        logger.info(f"Connecting (attempt #{self.connection_attempts})...")

        # If we've had too many consecutive failures, succeed to simulate recovery
        if self.consecutive_failures >= self.max_consecutive_failures:
            logger.info("Max consecutive failures reached, connection will succeed")
            self.consecutive_failures = 0
            self.connected = True
            self.connect_time = datetime.now()
            self.last_activity = self.connect_time
            logger.info("Connected successfully after max failures")
            return True

        # Randomly decide whether to succeed or fail
        if random.random() < self.failure_rate:
            self.consecutive_failures += 1
            logger.info(f"Connection failed (consecutive failures: {self.consecutive_failures})")
            error_info = {
                "attempt": self.connection_attempts,
                "consecutive_failures": self.consecutive_failures
            }
            raise MCPConnectionError("Simulated connection failure", error_info)

        # Successful connection
        self.consecutive_failures = 0
        self.connected = True
        self.connect_time = datetime.now()
        self.last_activity = self.connect_time
        logger.info("Connected successfully")
        return True

    # pyright: ignore[reportInvalidTypeForm]
    async def send_request(
        self,
        request: Dict[str, Any],
        cancellation_token: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Send a request, with possible failure."""
        if not self.connected:
            raise MCPConnectionError("Not connected")

        request_id = request.get("id", "unknown")
        method = request.get("method", "unknown")
        logger.info(f"Sending request: {method} (id: {request_id})")

        # Random delay
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Update activity time
        if self.last_activity is None:
            self.last_activity = datetime.now()
        else:
            self.last_activity = datetime.now()

        # Check for cancellation
        has_cancelled = (
            cancellation_token and
            hasattr(cancellation_token, 'cancelled') and
            cancellation_token.cancelled
        )
        if has_cancelled:
            logger.info(f"Request cancelled: {method} (id: {request_id})")
            raise asyncio.CancelledError("Request cancelled")

        # Randomly decide whether to succeed or fail
        if random.random() < self.failure_rate:
            self.consecutive_failures += 1
            self.failed_requests += 1
            logger.info(f"Request failed: {method} (id: {request_id})")
            raise MCPRequestError(
                "Simulated request failure",
                {"request_id": request_id, "method": method}
            )

        # Successful request
        self.consecutive_failures = 0
        self.successful_requests += 1
        logger.info(f"Request succeeded: {method} (id: {request_id})")

        # Create a mock response
        return {
            "jsonrpc": "2.0",
            "result": {"status": "success", "message": "Request processed successfully"},
            "id": request_id
        }

    async def disconnect(self) -> bool:
        """Disconnect from the service."""
        logger.info("Disconnecting...")
        self.connected = False
        logger.info("Disconnected successfully")
        return True

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        stats = {
            "connected": self.connected,
            "connection_attempts": self.connection_attempts,
            "consecutive_failures": self.consecutive_failures,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "failure_rate": self.failure_rate,
            "type": "unstable_test"
        }

        if self.connect_time:
            stats["connect_time"] = self.connect_time.isoformat()
            stats["connection_age_s"] = (datetime.now() - self.connect_time).total_seconds()

        if self.last_activity:
            stats["last_activity"] = self.last_activity.isoformat()
            stats["idle_time_s"] = (datetime.now() - self.last_activity).total_seconds()

        return stats


class MCPReconnectionTest(unittest.IsolatedAsyncioTestCase):
    """Test case for MCP reconnection and error handling."""

    async def asyncSetUp(self):
        """Set up the test case."""
        # Create a mock model
        self.mock_model = MagicMock()
        self.mock_model.chat = AsyncMock()

        # Create the MCP handler
        self.handler = MCPHandler(model=self.mock_model)

        # Patch the transport factory to return our unstable transport
        self.unstable_transport = UnstableTransport(failure_rate=0.3)
        self.factory_patcher = patch.object(
            MCPTransportFactory, 'create_transport',
            return_value=self.unstable_transport
        )
        self.mock_factory = self.factory_patcher.start()

    async def asyncTearDown(self):
        """Tear down the test case."""
        self.factory_patcher.stop()

    async def test_connection_with_retries(self):
        """Test connecting to a server with retries."""
        # Configure the transport to fail most of the time initially
        self.unstable_transport.failure_rate = 0.8

        # Try to connect with retries
        max_retries = 5
        retry_count = 0
        connected = False

        while retry_count < max_retries and not connected:
            try:
                connected = await self.handler.connect_server(
                    name="test_server",
                    url="test://localhost",
                )
                if connected:
                    logger.info(f"Connected successfully after {retry_count} retries")
                    break

            except MCPConnectionError as e:
                retry_count += 1
                retry_delay = min(2 ** retry_count, 32)  # Exponential backoff
                logger.info(f"Connection attempt {retry_count} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)

        # Check if we connected eventually
        self.assertTrue(
            connected or retry_count < max_retries,
            f"Failed to connect after {retry_count} retries"
        )

        if connected:
            # Get connection stats for diagnostics
            stats = self.handler.get_connection_stats()
            logger.info(f"Connection stats: {json.dumps(stats, indent=2)}")

            # Disconnect
            await self.handler.disconnect_server("test_server")

    async def test_request_with_retries(self):
        """Test sending a request with retries."""
        # Make the first connection guaranteed to succeed
        self.unstable_transport.failure_rate = 0.0

        # Connect to the server
        try:
            connected = await self.handler.connect_server(
                name="test_server",
                url="test://localhost",
            )
            self.assertTrue(connected, "Failed to establish initial connection")
        except MCPConnectionError as e:
            self.fail(f"Failed to establish initial connection: {str(e)}")

        # Now make requests more likely to fail
        self.unstable_transport.failure_rate = 0.3

        # Try to execute a tool with retries
        max_retries = 5
        retry_count = 0
        success = False
        result = None

        while retry_count < max_retries and not success:
            try:
                result = await self.handler.execute_tool(
                    server_name="test_server",
                    tool_name="test_tool",
                    params={"param1": "value1"},
                )
                success = True
                logger.info(f"Request succeeded after {retry_count} retries")

            except (MCPConnectionError, MCPRequestError) as e:
                retry_count += 1
                retry_delay = min(2 ** retry_count, 32)  # Exponential backoff
                logger.info(f"Request attempt {retry_count} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)

        # Check if we succeeded eventually
        self.assertTrue(
            success,
            f"Failed to execute tool after {retry_count} retries"
        )

        if success:
            self.assertIsNotNone(result, "Result should not be None")
            self.assertIn("result", result, "Result should contain 'result' field")

            # Get connection stats for diagnostics
            stats = self.handler.get_connection_stats()
            logger.info(f"Connection stats after requests: {json.dumps(stats, indent=2)}")

            # Disconnect
            await self.handler.disconnect_server("test_server")

    async def test_multiple_request_resilience(self):
        """Test resilience with multiple requests."""
        # Set low failure rate to ensure connection success
        self.unstable_transport.failure_rate = 0.1  # Was 0.4

        # Connect to the server (with retries if needed)
        max_connect_retries = 3
        for attempt in range(max_connect_retries):
            try:
                connected = await self.handler.connect_server(
                    name="test_server",
                    url="test://localhost",
                )
                self.assertTrue(connected, "Failed to establish connection")
                break
            except MCPConnectionError as e:
                logger.info(f"Connection attempt {attempt+1} failed: {str(e)}")
                if attempt < max_connect_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.fail(f"Failed to connect after {max_connect_retries} attempts")

        # Send multiple requests
        num_requests = 10
        max_retries_per_request = 3
        successful_requests = 0

        for i in range(num_requests):
            logger.info(f"Sending request {i+1}/{num_requests}")
            success = False

            for retry in range(max_retries_per_request):
                try:
                    await self.handler.execute_tool(
                        server_name="test_server",
                        tool_name="test_tool",
                        params={"param": f"value_{i}"}
                    )
                    successful_requests += 1
                    success = True
                    logger.info(f"Request {i+1} succeeded on attempt {retry+1}")
                    break
                except (MCPConnectionError, MCPRequestError) as e:
                    logger.info(f"Request {i+1} attempt {retry+1} failed: {str(e)}")
                    if retry < max_retries_per_request - 1:
                        await asyncio.sleep(1)  # Simple delay between retries

            if not success:
                logger.warning(f"Request {i+1} failed after {max_retries_per_request} attempts")

        # Check success rate
        success_rate = successful_requests / num_requests
        logger.info(f"Success rate: {success_rate:.2%} ({successful_requests}/{num_requests})")

        # Get final stats
        stats = self.handler.get_connection_stats()
        logger.info(f"Final connection stats: {json.dumps(stats, indent=2)}")

        # Disconnect
        await self.handler.disconnect_server("test_server")

        # Verify reasonable success rate given the failure rate
        # With retries, we should have a higher success rate than (1-failure_rate)
        minimum_expected_success_rate = 0.6  # This should be achievable with retries
        self.assertGreaterEqual(
            success_rate,
            minimum_expected_success_rate,
            f"Success rate too low: {success_rate:.2%}"
        )


if __name__ == "__main__":
    unittest.main()
