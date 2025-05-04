# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Reconnecting MCP Handler - Robust MCP Connectivity
# Description:  MCP Handler with automatic connection recovery capabilities
# Role:         Provides resilient tool execution with automatic reconnection
# Usage:        Used when reliability for MCP connections is required
# Author:       Muxi Framework Team
#
# The Reconnecting MCP Handler extends the standard MCP Handler with automatic
# reconnection capabilities for enhanced resilience. Key features include:
#
# 1. Automatic Recovery
#    - Transparent reconnection on connection failures
#    - Configurable retry policies with exponential backoff
#    - Graceful degradation on persistent failures
#
# 2. Connection Management
#    - Automatic reconnection before tool execution
#    - Connection state tracking
#    - Comprehensive retry statistics
#
# 3. Fault Tolerance
#    - Server failure handling
#    - Network interruption recovery
#    - Request timeout management
#
# This implementation is designed for production environments where network
# reliability is critical, providing a robust interface for MCP tool execution
# that can recover from transient connectivity issues.
# =============================================================================

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger

from muxi.core.mcp.handler import MCPHandler, MCPConnectionError
from muxi.core.reconnection import RetryConfiguration, with_retries


class ReconnectingMCPHandler(MCPHandler):
    """
    Enhanced MCPHandler with reconnection support.

    This class extends the standard MCPHandler with automatic reconnection
    capabilities using exponential backoff. It transparently handles connection
    failures and retries operations without requiring client code changes.
    """

    def __init__(self, model, retry_config: Optional[RetryConfiguration] = None):
        """
        Initialize the reconnecting MCP handler.

        Args:
            model: The LLM model to use for processing
            retry_config: Configuration for retry behavior, or None to use defaults
        """
        super().__init__(model=model)
        self.retry_config = retry_config or RetryConfiguration(
            max_retries=3, initial_delay=1.0, max_delay=30.0, backoff_factor=2.0, jitter=True
        )
        self._reconnection_in_progress = {}

    async def connect_server(
        self,
        name: str,
        url: Optional[str] = None,
        command: Optional[str] = None,
        credentials: Optional[Dict[str, Any]] = None,
        request_timeout: float = 60.0,
    ) -> bool:
        """
        Connect to an MCP server with automatic reconnection support.

        This method enhances the standard connect_server method with retry
        capabilities, automatically attempting to reconnect if the initial
        connection fails.

        Args:
            name: Unique identifier for the server
            url: URL for the HTTP+SSE server
            command: Command line for local MCP server
            credentials: Optional credentials for authentication
            request_timeout: Timeout for requests in seconds

        Returns:
            True if connection was successful, False otherwise

        Raises:
            ValueError: If name is empty or both url and command are missing
            MCPConnectionError: If connection failed after retries
        """
        if not name:
            raise ValueError("Server name must be provided")

        if not url and not command:
            raise ValueError("Either url or command must be provided")

        server_url = url or command

        log_msg = f"Connecting to MCP server {name} at {server_url} " f"with reconnection support"
        logger.info(log_msg)

        # Use the retry mechanism for connection
        try:
            result = await with_retries(
                f"Connect to MCP server {name}",
                self._connect_server_impl,
                retry_config=self.retry_config,
                retry_exceptions=MCPConnectionError,
                name=name,
                url=url,
                command=command,
                credentials=credentials,
                request_timeout=request_timeout,
            )
            return result
        except MCPConnectionError as e:
            error_msg = f"Failed to connect to MCP server {name} after retries: {str(e)}"
            logger.error(error_msg)
            raise

    async def _connect_server_impl(
        self,
        name: str,
        url: Optional[str] = None,
        command: Optional[str] = None,
        credentials: Optional[Dict[str, Any]] = None,
        request_timeout: float = 60.0,
    ) -> bool:
        """
        Implementation of server connection used by the retry mechanism.

        This internal method is called by the retry mechanism to attempt
        connection to the server. It directly delegates to the parent class's
        connect_server method.

        Args:
            name: Unique identifier for the server
            url: URL for the HTTP+SSE server
            command: Command line for local MCP server
            credentials: Optional credentials for authentication
            request_timeout: Timeout for requests in seconds

        Returns:
            True if connection was successful

        Raises:
            MCPConnectionError: If connection failed
        """
        return await super().connect_server(
            name=name,
            url=url,
            command=command,
            credentials=credentials,
            request_timeout=request_timeout,
        )

    async def execute_tool(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any],
        cancellation_token: Any = None,
    ) -> Dict[str, Any]:
        """
        Execute a tool with automatic retry on connection errors.

        This method enhances the standard execute_tool method with automatic
        reconnection and retry capabilities, ensuring that transient connection
        issues don't cause tool execution failures.

        Args:
            server_name: Name of the server to execute the tool on
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
        if not server_name:
            server_name = await self._get_server_for_tool(tool_name)
            if not server_name:
                error_msg = f"Tool {tool_name} is not available on any connected server"
                raise ValueError(error_msg)

        # Only retry on connection errors, not on request errors or timeouts
        try:
            result = await with_retries(
                f"Execute tool {tool_name}",
                self._execute_tool_impl,
                retry_config=self.retry_config,
                retry_exceptions=MCPConnectionError,
                server_name=server_name,
                tool_name=tool_name,
                params=params,
                cancellation_token=cancellation_token,
            )
            return result
        except MCPConnectionError as e:
            error_msg = f"Failed to execute tool {tool_name} after retries: {str(e)}"
            logger.error(error_msg)
            raise

    async def _execute_tool_impl(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any],
        cancellation_token: Any,
    ) -> Dict[str, Any]:
        """
        Implementation of tool execution used by the retry mechanism.

        This internal method is called by the retry mechanism to attempt
        execution of a tool. It includes automatic reconnection logic if
        the server is disconnected.

        Args:
            server_name: Name of the server to use
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            cancellation_token: Token to cancel the operation

        Returns:
            Tool execution result

        Raises:
            MCPConnectionError: If connection failed
            MCPRequestError: If the request failed
            MCPTimeoutError: If the request timed out
        """
        # Check if we need to reconnect
        if (
            server_name not in self.active_connections
            or not self.active_connections[server_name].connected
        ):
            if server_name not in self._reconnection_in_progress:
                self._reconnection_in_progress[server_name] = True
                try:
                    logger.info(f"Automatic reconnection to server {server_name} triggered")
                    server_info = self.server_info.get(server_name, {})
                    url = server_info.get("url")
                    command = server_info.get("command")
                    credentials = server_info.get("credentials")
                    request_timeout = server_info.get("request_timeout", 60.0)

                    if not url and not command:
                        error_msg = (
                            f"Cannot reconnect to server {server_name}: "
                            f"URL or command not found"
                        )
                        raise MCPConnectionError(error_msg)

                    await super().connect_server(
                        name=server_name,
                        url=url,
                        command=command,
                        credentials=credentials,
                        request_timeout=request_timeout,
                    )
                    logger.info(f"Successfully reconnected to server {server_name}")
                finally:
                    self._reconnection_in_progress[server_name] = False
            else:
                # Another reconnection is in progress, wait for it
                for _ in range(10):  # Wait for up to ~1 second
                    reconnection_done = (
                        server_name not in self._reconnection_in_progress
                        or not self._reconnection_in_progress[server_name]
                    )
                    if reconnection_done:
                        break
                    await asyncio.sleep(0.1)

                if (
                    server_name not in self.active_connections
                    or not self.active_connections[server_name].connected
                ):
                    error_msg = (
                        f"Server {server_name} is not connected " f"after reconnection attempt"
                    )
                    raise MCPConnectionError(error_msg)

        # Now execute the tool
        return await super().execute_tool(server_name, tool_name, params, cancellation_token)

    async def list_tools(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        List available tools with retry support.

        This method enhances the standard list_tools method with automatic
        retry capabilities, ensuring that tool discovery succeeds even with
        transient connection issues.

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
                refresh=refresh,
            )
            return result
        except MCPConnectionError as e:
            logger.error(f"Failed to list tools after retries: {str(e)}")
            # Return empty list instead of raising to avoid breaking clients
            return []

    def get_retry_stats(self) -> Dict[str, Any]:
        """
        Get retry statistics.

        This method provides diagnostic information about retry operations
        and reconnection status, useful for monitoring and debugging.

        Returns:
            Dictionary with retry statistics including retry configuration
            and current reconnection status
        """
        stats = {
            "retry_config": {
                "max_retries": self.retry_config.max_retries,
                "initial_delay": self.retry_config.initial_delay,
                "max_delay": self.retry_config.max_delay,
                "backoff_factor": self.retry_config.backoff_factor,
                "jitter": self.retry_config.jitter,
            },
            "reconnection_in_progress": list(
                server_id
                for server_id, in_progress in self._reconnection_in_progress.items()
                if in_progress
            ),
        }

        connection_stats = self.get_connection_stats()
        if connection_stats:
            stats["connection_stats"] = connection_stats

        return stats
