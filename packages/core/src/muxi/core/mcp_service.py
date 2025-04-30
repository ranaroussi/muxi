"""
Centralized MCP Handler Service for MUXI Framework.

This module provides a centralized service for handling MCP (Model Context Protocol)
communications between Agents and MCP Servers.
"""

import asyncio
from typing import Any, Dict, List, Optional
from loguru import logger

from muxi.core.mcp_handler import MCPHandler
from muxi.models.base import BaseModel


class MCPService:
    """
    Centralized service for handling MCP communications.

    This service manages connections to MCP servers and handles
    the protocol details for all agent communications.
    """

    _instance = None

    @classmethod
    def get_instance(cls, **kwargs) -> 'MCPService':
        """
        Get the singleton instance of the MCP Service.

        Args:
            **kwargs: Arguments to pass to the constructor if creating a new instance

        Returns:
            The singleton instance of MCPService
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the MCP Service."""
        self.handlers: Dict[str, Any] = {}  # Maps server_id to handler instances
        self.connections: Dict[str, Any] = {}  # Connection state for MCP servers
        self.tool_registry: Dict[str, Dict[str, Any]] = {}  # Registry of available tools
        self.locks = {}  # Locks for concurrent access to handlers

    async def register_mcp_server(
        self,
        server_id: str,
        url: Optional[str] = None,
        command: Optional[str] = None,
        credentials: Optional[Dict[str, Any]] = None,
        model: Optional[BaseModel] = None,
        request_timeout: int = 60
    ) -> str:
        """
        Register an MCP server with the service.

        Args:
            server_id: Unique identifier for the MCP server
            url: URL for HTTP/SSE MCP servers
            command: Command for command-line MCP servers
            credentials: Optional credentials for authentication
            model: Optional model to use for this MCP handler
            request_timeout: Timeout in seconds for requests to this server

        Returns:
            The server_id of the registered server
        """
        # Create lock for this handler
        self.locks[server_id] = asyncio.Lock()

        # Initialize the handler
        async with self.locks[server_id]:
            try:
                # Create and initialize the MCP handler
                handler = MCPHandler(model=model)

                # Set up connection with the transport factory
                # This establishes actual connection to the server
                server_name = server_id.replace("-", "_").lower()

                # Connect to the server using the appropriate transport
                await handler.connect_server(
                    name=server_name,
                    url=url,
                    command=command,
                    credentials=credentials,
                    request_timeout=request_timeout  # Pass the timeout parameter
                )

                # Store the handler
                self.handlers[server_id] = handler
                self.connections[server_id] = {
                    "status": "connected",
                    "url": url,
                    "command": command,
                    "credentials": credentials,
                    "server_name": server_name,
                    "request_timeout": request_timeout
                }

                # Discover available tools
                try:
                    tools = await handler.list_tools(server_name)
                    self.tool_registry[server_id] = {
                        tool.get("name", f"unknown_{i}"): tool
                        for i, tool in enumerate(tools)
                    }
                    logger.info(
                        f"Discovered {len(tools)} tools from MCP server: {server_id}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Unable to discover tools from MCP server {server_id}: {str(e)}"
                    )
                    self.tool_registry[server_id] = {}

                logger.info(f"Registered MCP server: {server_id}")
                return server_id

            except Exception as e:
                # Clean up if something went wrong
                if server_id in self.locks:
                    del self.locks[server_id]
                logger.error(f"Failed to register MCP server {server_id}: {str(e)}")
                raise

    async def invoke_tool(
        self,
        server_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        request_timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Invoke a tool on an MCP server.

        Args:
            server_id: The ID of the server to use
            tool_name: The name of the tool to invoke
            parameters: The parameters to pass to the tool
            request_timeout: Optional timeout override for this specific request

        Returns:
            The result of the tool invocation
        """
        if server_id not in self.handlers:
            raise ValueError(f"Unknown MCP server: {server_id}")

        handler = self.handlers[server_id]
        server_name = self.connections[server_id]["server_name"]

        # Acquire lock for this handler to prevent concurrent issues
        async with self.locks[server_id]:
            try:
                # Use request timeout from parameters,
                # or fall back to the one saved during server registration
                default_timeout = self.connections[server_id].get("request_timeout", 60)  # noqa: E501
                timeout = request_timeout if request_timeout is not None else default_timeout

                # Check if we need to temporarily modify the timeout
                restore_timeout = False
                original_timeout = None

                if (request_timeout is not None and server_name in handler.active_connections):
                    client = handler.active_connections[server_name]
                    if client.request_timeout != request_timeout:
                        # Store original timeout to restore later
                        original_timeout = client.request_timeout
                        client.request_timeout = timeout
                        restore_timeout = True

                # Process the tool call through the handler directly to the server
                result = await handler.execute_tool(
                    server_name=server_name,
                    tool_name=tool_name,
                    params=parameters,
                    cancellation_token=None
                )
                return {"result": result, "status": "success"}

            except Exception as e:
                logger.error(f"Error invoking tool {tool_name} on server {server_id}: {str(e)}")
                return {"error": str(e), "status": "error"}
            finally:
                # Restore the original timeout if we changed it
                if restore_timeout and server_name in handler.active_connections:
                    handler.active_connections[server_name].request_timeout = original_timeout

    async def list_tools(self, server_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List available tools from MCP servers.

        Args:
            server_id: Optional server ID to list tools from a specific server

        Returns:
            Dictionary mapping server IDs to lists of available tools
        """
        result = {}

        if server_id:
            # List tools from specific server
            if server_id not in self.handlers:
                raise ValueError(f"Unknown MCP server: {server_id}")

            handler = self.handlers[server_id]
            server_name = self.connections[server_id]["server_name"]

            try:
                tools = await handler.list_tools(server_name)
                result[server_id] = tools

                # Update the tool registry
                self.tool_registry[server_id] = {
                    tool.get("name", f"unknown_{i}"): tool
                    for i, tool in enumerate(tools)
                }
            except Exception as e:
                logger.error(f"Error listing tools from server {server_id}: {str(e)}")
                result[server_id] = []

        else:
            # List tools from all servers
            for sid, handler in self.handlers.items():
                server_name = self.connections[sid]["server_name"]
                try:
                    tools = await handler.list_tools(server_name)
                    result[sid] = tools

                    # Update the tool registry
                    self.tool_registry[sid] = {
                        tool.get("name", f"unknown_{i}"): tool
                        for i, tool in enumerate(tools)
                    }
                except Exception as e:
                    logger.error(f"Error listing tools from server {sid}: {str(e)}")
                    result[sid] = []

        return result

    async def disconnect_server(self, server_id: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            server_id: The ID of the server to disconnect

        Returns:
            True if disconnection was successful
        """
        if server_id not in self.handlers:
            return False

        async with self.locks[server_id]:
            try:
                handler = self.handlers[server_id]
                server_name = self.connections[server_id]["server_name"]

                # Disconnect from the server
                await handler.disconnect_server(server_name)

                # Remove from registry
                del self.handlers[server_id]
                del self.connections[server_id]
                del self.locks[server_id]
                if server_id in self.tool_registry:
                    del self.tool_registry[server_id]

                logger.info(f"Disconnected from MCP server: {server_id}")
                return True

            except Exception as e:
                logger.error(f"Error disconnecting from MCP server {server_id}: {str(e)}")
                return False
