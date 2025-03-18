"""
Enhanced MCPHandler with reconnection support.

This module provides an extended MCPHandler implementation with
automatic reconnection capabilities.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from .mcp_handler import MCPHandler, MCPConnectionError
from .reconnection import RetryConfiguration, with_retries

logger = logging.getLogger(__name__)


class ReconnectingMCPHandler(MCPHandler):
    """
    Enhanced MCPHandler with reconnection support.

    This class extends the standard MCPHandler with automatic reconnection
    capabilities using exponential backoff.
    """

    def __init__(self, retry_config: Optional[RetryConfiguration] = None):
        """
        Initialize the reconnecting MCP handler.

        Args:
            retry_config: Configuration for retry behavior, or None to use defaults
        """
        super().__init__()
        self.retry_config = retry_config or RetryConfiguration(
            max_retries=3,
            initial_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0,
            jitter=True
        )
        self._reconnection_in_progress = {}

    async def connect_server(
        self,
        server_id: str,
        server_url: str,
        transport_type: str = "http_sse",
        request_timeout: float = 60.0
    ) -> bool:
        """
        Connect to an MCP server with automatic reconnection support.

        Args:
            server_id: Unique identifier for the server
            server_url: URL or identifier for the server
            transport_type: Transport type to use ("http_sse" or "command_line")
            request_timeout: Timeout for requests in seconds

        Returns:
            True if connection was successful, False otherwise

        Raises:
            ValueError: If server_id or server_url is empty
            MCPConnectionError: If connection failed after retries
        """
        if not server_id or not server_url:
            raise ValueError("Server ID and URL must be provided")

        log_msg = (
            f"Connecting to MCP server {server_id} at {server_url} "
            f"with reconnection support"
        )
        logger.info(log_msg)

        # Use the retry mechanism for connection
        try:
            result = await with_retries(
                f"Connect to MCP server {server_id}",
                self._connect_server_impl,
                retry_config=self.retry_config,
                retry_exceptions=MCPConnectionError,
                server_id=server_id,
                server_url=server_url,
                transport_type=transport_type,
                request_timeout=request_timeout
            )
            return result
        except MCPConnectionError as e:
            error_msg = (
                f"Failed to connect to MCP server {server_id} after retries: {str(e)}"
            )
            logger.error(error_msg)
            raise

    async def _connect_server_impl(
        self,
        server_id: str,
        server_url: str,
        transport_type: str,
        request_timeout: float
    ) -> bool:
        """
        Implementation of server connection used by the retry mechanism.

        Args:
            server_id: Unique identifier for the server
            server_url: URL or identifier for the server
            transport_type: Transport type to use
            request_timeout: Timeout for requests in seconds

        Returns:
            True if connection was successful

        Raises:
            MCPConnectionError: If connection failed
        """
        return await super().connect_server(
            server_id=server_id,
            server_url=server_url,
            transport_type=transport_type,
            request_timeout=request_timeout
        )

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        cancellation_token: Any = None
    ) -> Dict[str, Any]:
        """
        Execute a tool with automatic retry on connection errors.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            cancellation_token: Token to cancel the operation

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool_name is not found or parameters are invalid
            MCPConnectionError: If connection failed and could not be recovered
            MCPRequestError: If the request failed
            MCPTimeoutError: If the request timed out
        """
        server_id = await self._get_server_for_tool(tool_name)
        if not server_id:
            error_msg = f"Tool {tool_name} is not available on any connected server"
            raise ValueError(error_msg)

        # Only retry on connection errors, not on request errors or timeouts
        try:
            result = await with_retries(
                f"Execute tool {tool_name}",
                self._execute_tool_impl,
                retry_config=self.retry_config,
                retry_exceptions=MCPConnectionError,
                tool_name=tool_name,
                params=params,
                cancellation_token=cancellation_token,
                server_id=server_id
            )
            return result
        except MCPConnectionError as e:
            error_msg = f"Failed to execute tool {tool_name} after retries: {str(e)}"
            logger.error(error_msg)
            raise

    async def _execute_tool_impl(
        self,
        tool_name: str,
        params: Dict[str, Any],
        cancellation_token: Any,
        server_id: str
    ) -> Dict[str, Any]:
        """
        Implementation of tool execution used by the retry mechanism.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            cancellation_token: Token to cancel the operation
            server_id: ID of the server to use

        Returns:
            Tool execution result

        Raises:
            MCPConnectionError: If connection failed
            MCPRequestError: If the request failed
            MCPTimeoutError: If the request timed out
        """
        # Check if we need to reconnect
        if server_id not in self.servers or not self.servers[server_id].is_connected():
            if server_id not in self._reconnection_in_progress:
                self._reconnection_in_progress[server_id] = True
                try:
                    logger.info(f"Automatic reconnection to server {server_id} triggered")
                    server_info = self.server_info.get(server_id, {})
                    server_url = server_info.get("url", "")
                    transport_type = server_info.get("transport_type", "http_sse")
                    request_timeout = server_info.get("request_timeout", 60.0)

                    if not server_url:
                        error_msg = f"Cannot reconnect to server {server_id}: URL not found"
                        raise MCPConnectionError(error_msg)

                    await super().connect_server(
                        server_id=server_id,
                        server_url=server_url,
                        transport_type=transport_type,
                        request_timeout=request_timeout
                    )
                    logger.info(f"Successfully reconnected to server {server_id}")
                finally:
                    self._reconnection_in_progress[server_id] = False
            else:
                # Another reconnection is in progress, wait for it
                for _ in range(10):  # Wait for up to ~1 second
                    reconnection_done = (
                        server_id not in self._reconnection_in_progress or
                        not self._reconnection_in_progress[server_id]
                    )
                    if reconnection_done:
                        break
                    await asyncio.sleep(0.1)

                if server_id not in self.servers or not self.servers[server_id].is_connected():
                    error_msg = f"Server {server_id} is not connected after reconnection attempt"
                    raise MCPConnectionError(error_msg)

        # Now execute the tool
        return await super().execute_tool(tool_name, params, cancellation_token)

    async def list_tools(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        List available tools with retry support.

        Args:
            refresh: Whether to refresh the tool list from servers

        Returns:
            List of available tools
        """
        try:
            result = await with_retries(
                "List MCP tools",
                super().list_tools,
                retry_config=self.retry_config,
                retry_exceptions=MCPConnectionError,
                refresh=refresh
            )
            return result
        except MCPConnectionError as e:
            logger.error(f"Failed to list tools after retries: {str(e)}")
            # Return empty list instead of raising to avoid breaking clients
            return []

    def get_retry_stats(self) -> Dict[str, Any]:
        """
        Get retry statistics.

        Returns:
            Dictionary with retry statistics
        """
        stats = {
            "retry_config": {
                "max_retries": self.retry_config.max_retries,
                "initial_delay": self.retry_config.initial_delay,
                "max_delay": self.retry_config.max_delay,
                "backoff_factor": self.retry_config.backoff_factor,
                "jitter": self.retry_config.jitter
            },
            "reconnection_in_progress": list(
                server_id for server_id, in_progress in self._reconnection_in_progress.items()
                if in_progress
            )
        }

        connection_stats = self.get_connection_stats()
        if connection_stats:
            stats["connection_stats"] = connection_stats

        return stats
