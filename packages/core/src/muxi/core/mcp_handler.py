"""
Model Context Protocol (MCP) handler implementation.

This module provides functionality for communicating with MCP servers using the
official ModelContextProtocol Python SDK.

Note on MCP SDK: The MCP Python SDK (from the mcp package) has a different structure than
what was originally expected. Key components we're using:
- mcp.client.session.ClientSession - The main client for MCP communication
- mcp.JSONRPCRequest - For creating JSON-RPC 2.0 requests
- Future work may need custom transport implementations for HTTP+SSE and command-line interfaces
"""

import uuid
from typing import Any, Dict, List, Optional

from loguru import logger
# Update imports based on the actual MCP package structure
from mcp.client.session import ClientSession as MCPClient
from mcp import JSONRPCRequest as SDKRequest

from muxi.core.mcp import MCPMessage, MCPContext
from muxi.models.base import BaseModel


# We need to replace the transport imports with the actual ones
# For now, we'll use mock placeholders until we figure out the correct imports
class HTTPSSETransport:
    """Temporary placeholder for HTTPSSETransport until we figure out the correct import"""
    def __init__(self, url):
        self.url = url


class CommandLineTransport:
    """Temporary placeholder for CommandLineTransport until we figure out the correct import"""
    def __init__(self, command):
        self.command = command


class MCPServerClient:
    """
    Client for communicating with an MCP server.
    """

    def __init__(
        self,
        name: str,
        url_or_command: str,
        transport_type: str = "http_sse",
        credentials: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an MCP server client.

        Args:
            name: The name of the MCP server
            url_or_command: The URL or command to start the MCP server
            transport_type: The type of transport to use
            credentials: Optional credentials for authentication
        """
        self.name = name
        self.url_or_command = url_or_command
        self.transport_type = transport_type
        self.credentials = credentials or {}
        self.client = None
        self.connected = False

    async def connect(self) -> bool:
        """
        Connect to the MCP server.

        Returns:
            bool: True if connection was successful
        """
        try:
            # Create appropriate transport using the SDK
            if self.transport_type == "http_sse":
                transport = HTTPSSETransport(self.url_or_command)
            elif self.transport_type == "command_line":
                transport = CommandLineTransport(self.url_or_command)
            else:
                raise ValueError(f"Unsupported transport type: {self.transport_type}")

            # Create MCP client with transport
            self.client = MCPClient(transport=transport)

            # Connect and initialize
            await self.client.connect()

            # Add credentials if provided
            if self.credentials:
                # The SDK might have a better way to handle credentials, but for now
                # we'll store them to be sent with each request
                pass

            self.connected = True
            logger.info(f"Successfully connected to MCP server: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.name}: {str(e)}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the MCP server.

        Returns:
            bool: True if disconnection was successful
        """
        if not self.client:
            return False

        try:
            await self.client.disconnect()
            self.connected = False
            self.client = None
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {self.name}: {str(e)}")
            return False

    async def send_message(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to the MCP server.

        Args:
            method: The method to call
            params: The parameters for the call

        Returns:
            The response from the server
        """
        if not self.client or not self.connected:
            raise RuntimeError(f"Not connected to MCP server: {self.name}")

        # Merge credentials with parameters
        merged_params = {**params, **self.credentials}

        # Create JSON-RPC request
        request = SDKRequest(
            method=method,
            params=merged_params,
            id=str(uuid.uuid4())
        )

        try:
            # Send request and get response
            response = await self.client.request(request)
            return response.to_dict()
        except Exception as e:
            logger.error(f"Error sending message to MCP server {self.name}: {str(e)}")
            return {"error": f"Communication error: {str(e)}"}

    async def execute_tool(self, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool on the MCP server.

        Args:
            **kwargs: The parameters for the tool

        Returns:
            The result of the tool execution
        """
        # Use the server name as the method
        try:
            # Send to the default MCP tools method for this server
            result = await self.send_message(self.name, kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing tool on MCP server {self.name}: {str(e)}")
            return {"error": f"Tool execution error: {str(e)}"}


class MCPHandler:
    """
    Handles communication with MCP servers using the Model Context Protocol.
    """

    def __init__(self, model: BaseModel):
        """
        Initialize an MCP handler.

        Args:
            model: The language model to use for generating responses.
        """
        self.model = model
        self.mcp_servers = {}  # Map of server_name -> server_config
        self.active_connections = {}  # Map of server_name -> MCPServerClient
        self.context = MCPContext()

    async def connect_mcp_server(
        self,
        name: str,
        url_or_command: str,
        transport_type: str = "http_sse",
        credentials: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: A unique identifier for this MCP server
            url_or_command: The URL or command to start the MCP server
            transport_type: The type of transport to use
            credentials: Optional credentials for authentication

        Returns:
            bool: True if connection was successful
        """
        try:
            # Create MCP client
            client = MCPServerClient(
                name=name,
                url_or_command=url_or_command,
                transport_type=transport_type,
                credentials=credentials,
            )

            # Connect to the server
            success = await client.connect()
            if not success:
                return False

            # Store the connection
            self.active_connections[name] = client

            # Store the configuration
            self.mcp_servers[name] = {
                "url_or_command": url_or_command,
                "transport_type": transport_type,
                "credentials": credentials or {}
            }

            # Register the tool with the context
            tool_definition = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": f"Access to {name} MCP server functionality",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }

            if not hasattr(self.context, "tools"):
                self.context.tools = []

            self.context.tools.append(tool_definition)

            logger.info(f"Successfully connected to MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {str(e)}")
            return False

    async def disconnect_mcp_server(self, name: str) -> bool:
        """
        Gracefully disconnect from an MCP server.

        Args:
            name: The name of the MCP server

        Returns:
            bool: True if disconnection was successful
        """
        if name not in self.active_connections:
            logger.warning(f"Attempted to disconnect from non-existent MCP server: {name}")
            return False

        try:
            client = self.active_connections[name]
            success = await client.disconnect()

            if success:
                del self.active_connections[name]
                # Also remove from the context's tools list
                if hasattr(self.context, "tools"):
                    self.context.tools = [
                        tool for tool in self.context.tools
                        if tool["function"]["name"] != name
                    ]
                return True
            return False
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {name}: {str(e)}")
            return False

    def set_system_message(self, system_message: str) -> None:
        """
        Set the system message for the MCP handler.

        Args:
            system_message: The system message to set
        """
        # Clear existing system messages
        self.context.messages = [m for m in self.context.messages if m.role != "system"]

        # Add new system message
        self.context.add_message(MCPMessage(role="system", content=system_message))

    async def process_message(
        self, message: MCPMessage, context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        Process a message and generate a response.

        Args:
            message: The message to process.
            context: Optional context to use. If None, the handler's context
                will be used.

        Returns:
            The response message.
        """
        # Use provided context or the handler's context
        ctx = context or self.context

        # Add message to context
        ctx.add_message(message)

        # Convert context to a format suitable for the language model
        model_messages = self._context_to_model_messages(ctx)

        # Generate a response
        response_content = await self.model.chat(model_messages)

        # Check if the response contains tool calls
        if isinstance(response_content, dict) and "tool_calls" in response_content:
            # Process tool calls
            tool_calls = response_content.get("tool_calls", [])
            content = response_content.get("content", "")

            # Create a response message with the content (may be empty if the model
            # didn't generate any content alongside the tool calls)
            response = MCPMessage(
                role="assistant",
                content=content,
                tool_calls=tool_calls
            )

            # Add response to context
            ctx.add_message(response)

            # Process each tool call
            for tool_call in tool_calls:
                tool_name = tool_call.tool_name
                tool_id = tool_call.tool_id
                tool_args = tool_call.tool_args

                # Check if we have a connection to this MCP server
                if tool_name in self.active_connections:
                    try:
                        # Execute the tool call on the MCP server
                        client = self.active_connections[tool_name]
                        result = await client.execute_tool(**tool_args)

                        # Create a tool response message
                        tool_response = MCPMessage(
                            role="tool",
                            content=result,
                            name=tool_name,
                            tool_call_id=tool_id
                        )

                        # Add tool response to context
                        ctx.add_message(tool_response)
                    except Exception as e:
                        error_message = f"Error executing tool call {tool_name}: {str(e)}"
                        logger.error(error_message)

                        # Create an error tool response
                        error_response = MCPMessage(
                            role="tool",
                            content={"error": error_message},
                            name=tool_name,
                            tool_call_id=tool_id
                        )

                        # Add error response to context
                        ctx.add_message(error_response)
                else:
                    error_message = f"No connection to MCP server for tool: {tool_name}"
                    logger.error(error_message)

                    # Create an error tool response
                    error_response = MCPMessage(
                        role="tool",
                        content={"error": error_message},
                        name=tool_name,
                        tool_call_id=tool_id
                    )

                    # Add error response to context
                    ctx.add_message(error_response)

            # Now generate a final response that takes into account the tool results
            model_messages = self._context_to_model_messages(ctx)
            final_response_content = await self.model.chat(model_messages)

            # Create the final response message
            final_response = MCPMessage(
                role="assistant",
                content=final_response_content
            )

            # Add final response to context
            ctx.add_message(final_response)

            return final_response
        else:
            # If no tool calls, just return the response
            # Handle both string and dict responses
            if isinstance(response_content, str):
                content = response_content
            elif isinstance(response_content, dict):
                content = response_content.get("content", "")
            else:
                content = str(response_content)

            response = MCPMessage(
                role="assistant",
                content=content
            )

            # Add response to context
            ctx.add_message(response)

            return response

    def _context_to_model_messages(self, context: MCPContext) -> List[Dict[str, Any]]:
        """
        Convert an MCP context to a format suitable for the language model.

        Args:
            context: The MCP context to convert.

        Returns:
            A list of messages in the format expected by the language model.
        """
        model_messages = []

        for message in context.messages:
            model_message = {
                "role": message.role,
                "content": message.content,
            }

            if message.name:
                model_message["name"] = message.name

            if message.context:
                model_message["context"] = message.context

            if message.tool_call_id:
                model_message["tool_call_id"] = message.tool_call_id

            if message.tool_calls:
                model_message["tool_calls"] = message.tool_calls

            model_messages.append(model_message)

        return model_messages

    def add_message(self, message: MCPMessage) -> None:
        """
        Add a message to the context.

        Args:
            message: The message to add
        """
        self.context.add_message(message)

    def clear_context(self) -> None:
        """
        Clear the context.
        """
        self.context = MCPContext()

    def set_context(self, context: MCPContext) -> None:
        """
        Set the context.

        Args:
            context: The context to set.
        """
        self.context = context

    async def get_available_mcp_servers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available MCP servers.

        Returns:
            A list of MCP server descriptions.
        """
        return [
            {
                "name": name,
                "url_or_command": details["url_or_command"],
                "transport_type": details["transport_type"],
                "credentials": details["credentials"],
                "connected": (name in self.active_connections and
                              self.active_connections[name].connected),
            }
            for name, details in self.mcp_servers.items()
        ]
