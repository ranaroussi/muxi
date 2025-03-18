"""
Model Context Protocol (MCP) handler implementation.

This module provides functionality for communicating with MCP servers using the
official ModelContextProtocol Python SDK.

Note on MCP SDK: The MCP Python SDK (from the mcp package) is now available on PyPI:
- pip install mcp>=1.4.1
- Main components include client, server, and transport functionality
- HTTP+SSE transport is our primary focus for now
"""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
import asyncio
import httpx
from mcp import JSONRPCRequest

logger = logging.getLogger(__name__)


class HTTPSSETransport:
    """HTTP+SSE transport for MCP servers."""

    def __init__(self, url: str):
        """Initialize with server URL.

        Args:
            url: Base URL of the MCP server
        """
        self.base_url = url
        self.sse_url = url if '/sse' in url else f"{url.rstrip('/')}/sse"
        self.message_url = None
        self.session_id = None
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for SSE
        self.sse_connection = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            # Initialize SSE connection with proper headers
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }

            self.sse_connection = await self.client.stream(
                'GET', self.sse_url, headers=headers, timeout=60.0
            )

            if self.sse_connection.status_code != 200:
                logger.error(f"Failed to connect to SSE endpoint: {self.sse_connection.status_code}")
                return False

            # Process SSE events to get endpoint info
            async for line in self.sse_connection.aiter_lines():
                if line.startswith("event: endpoint") or "endpoint" in line:
                    # Try to extract message URL from endpoint event
                    next_line = await self.sse_connection.aiter_lines().__anext__()
                    if next_line.startswith("data: "):
                        message_path = next_line[6:].strip()

                        # Make sure it's a full URL
                        if message_path.startswith('http'):
                            self.message_url = message_path
                        else:
                            # Handle relative paths
                            server_base = self.base_url.split('/sse')[0]
                            if not message_path.startswith('/'):
                                message_path = '/' + message_path
                            self.message_url = server_base + message_path

                        # Extract session ID from the URL
                        if "?" in self.message_url:
                            query = self.message_url.split("?")[1]
                            params = dict(p.split("=") for p in query.split("&"))

                            if "sessionId" in params:
                                self.session_id = params["sessionId"]
                            elif "session_id" in params:
                                self.session_id = params["session_id"]

                            logger.info(f"Connected to MCP server: {self.message_url}")
                            self.connected = True
                            return True

            logger.error("Failed to extract endpoint information from SSE")
            return False

        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            return False

    async def listen_for_events(self, callback: Callable = None) -> AsyncGenerator:
        """Listen for SSE events."""
        if not self.sse_connection:
            logger.error("Cannot listen for events: No SSE connection")
            return

        try:
            async for line in self.sse_connection.aiter_lines():
                if callback:
                    await callback(line)
                yield line
        except Exception as e:
            logger.error(f"Error listening for SSE events: {str(e)}")

    async def send_request(self, request_obj) -> Dict:
        """Send request to the server."""
        if not self.message_url or not self.session_id:
            raise ValueError("Not connected to MCP server")

        # Convert request to dictionary
        request_data = request_obj.model_dump()

        # Ensure session ID is included
        url = self.message_url
        if "sessionId=" not in url and "session_id=" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}sessionId={self.session_id}"

        try:
            # Send request and handle 202 Accepted (async processing)
            response = await self.client.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 202:
                # Server accepted the request asynchronously
                logger.info(f"Request accepted asynchronously: {request_data['method']}")
                return {"status": "accepted", "request_id": request_data.get("id")}

            elif response.status_code < 300:
                # Server returned immediate result
                return response.json()
            else:
                logger.error(f"Request failed: {response.status_code}")
                raise ValueError(f"Request failed with status {response.status_code}: {response.text}")

        except Exception as e:
            logger.error(f"Error sending request: {str(e)}")
            raise

    async def disconnect(self) -> bool:
        """Disconnect from MCP server."""
        try:
            if self.sse_connection:
                await self.sse_connection.aclose()

            await self.client.aclose()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
            return False


class CommandLineTransport:
    """Temporary placeholder for CommandLineTransport until we figure out the correct import"""
    def __init__(self, command):
        self.command = command


class MCPServerClient:
    """
    Client for a specific MCP server.

    This class manages a connection to an MCP server using the MCP SDK.
    """
    def __init__(
        self,
        name: str,
        url_or_command: str,
        transport_type: str,
        credentials: Dict[str, Any]
    ):
        """
        Initialize an MCP server client.

        Args:
            name: The name of the server (for identification)
            url_or_command: The URL or command to connect to the server
            transport_type: The type of transport to use (http_sse or command_line)
            credentials: Credentials for the server
        """
        self.name = name
        self.url_or_command = url_or_command
        self.transport_type = transport_type
        self.credentials = credentials
        self.client = None
        self.connected = False
        self.transport = None

        # Memory stream setup will be done in the connect method

    async def connect(self) -> bool:
        """
        Connect to the MCP server.

        Returns:
            bool: True if connection was successful
        """
        try:
            # Create transport based on type
            if self.transport_type == "http_sse":
                self.transport = HTTPSSETransport(self.url_or_command)
            elif self.transport_type == "command_line":
                self.transport = CommandLineTransport(self.url_or_command)
            else:
                raise ValueError(f"Unsupported transport type: {self.transport_type}")

            # Connect the transport
            await self.transport.connect()

            # Set up memory streams for the client
            from anyio.streams.memory import (
                MemoryObjectReceiveStream,
                MemoryObjectSendStream
            )

            # Create memory streams for the MCP client communication
            client_send, server_receive = MemoryObjectSendStream(), MemoryObjectReceiveStream()
            client_receive, server_send = MemoryObjectReceiveStream(), MemoryObjectSendStream()

            # Create MCP client with the streams
            self.client = MCPClient(
                read_stream=client_receive,
                write_stream=client_send
            )

            # Start a background task to forward messages between streams and transport
            asyncio.create_task(self._forward_messages(
                client_send=client_send,
                server_receive=server_receive,
                client_receive=client_receive,
                server_send=server_send
            ))

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

    async def _forward_messages(self, client_send, server_receive, client_receive, server_send):
        """
        Forward messages between the memory streams and the transport.
        This creates the bridge between the MCPClient and our transport implementation.
        """
        # Task to forward messages from client to transport
        async def forward_client_to_transport():
            while self.connected:
                try:
                    # Get message from client_send via server_receive
                    message = await server_receive.receive()

                    # Send via transport
                    if hasattr(self.transport, "request"):
                        response = await self.transport.request(message)

                        # Send response back to client
                        await server_send.send(response)
                except Exception as e:
                    logger.error(f"Error forwarding client->transport: {str(e)}")
                    break

        # Start forwarding task
        asyncio.create_task(forward_client_to_transport())

    async def disconnect(self) -> bool:
        """
        Disconnect from the MCP server.

        Returns:
            bool: True if disconnection was successful
        """
        if not self.client:
            return False

        try:
            if self.transport:
                await self.transport.disconnect()

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
            jsonrpc="2.0",
            id=str(uuid.uuid4())
        )

        try:
            # Send request directly to transport for simplicity
            if self.transport and hasattr(self.transport, "request"):
                response = await self.transport.request(request)
                return response
            else:
                # Fall back to using the client if transport doesn't have request method
                response = await self.client.request(method, merged_params)
                if hasattr(response, "model_dump"):
                    return response.model_dump()
                return response
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
    Handler for Model Context Protocol (MCP) communication.

    This class manages connections to MCP servers and provides methods for
    working with them from the agent.
    """

    def __init__(self, model: BaseModel):
        """
        Initialize the MCP handler.

        Args:
            model: The model to use for context handling
        """
        self.model = model
        self.active_connections = {}  # Maps server_name -> MCPServerClient

    async def connect_server(
        self,
        name: str,
        url_or_command: str,
        transport_type: str = "http_sse",
        credentials: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: A unique name for this server
            url_or_command: The URL or command to connect to the server
            transport_type: The type of transport to use (http_sse or command_line)
            credentials: Optional credentials for authentication

        Returns:
            bool: True if connection was successful
        """
        if name in self.active_connections:
            logger.warning(f"Already connected to MCP server: {name}")
            return True

        try:
            # Create client
            client = MCPServerClient(
                name=name,
                url_or_command=url_or_command,
                transport_type=transport_type,
                credentials=credentials or {},
            )

            # Connect
            success = await client.connect()
            if success:
                self.active_connections[name] = client
                logger.info(f"Connected to MCP server: {name}")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {name}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to MCP server {name}: {str(e)}")
            return False

    async def disconnect_server(self, name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            name: The name of the server to disconnect from

        Returns:
            bool: True if disconnection was successful
        """
        if name not in self.active_connections:
            logger.warning(f"Not connected to MCP server: {name}")
            return False

        try:
            client = self.active_connections[name]
            success = await client.disconnect()
            if success:
                del self.active_connections[name]
                logger.info(f"Disconnected from MCP server: {name}")
                return True
            else:
                logger.error(f"Failed to disconnect from MCP server: {name}")
                return False
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {name}: {str(e)}")
            return False

    async def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process a message through an MCP server.

        This method will:
        1. Detect if the message contains MCP tool calls
        2. Execute those tool calls on the appropriate MCP server
        3. Update the message with the results

        Args:
            message: The message potentially containing MCP tool calls

        Returns:
            The processed message with tool call results
        """
        logger.debug(f"Processing message through MCP: {message}")

        # Check if we have any connections
        if not self.active_connections:
            logger.warning("No active MCP connections")
            return message

        # For now, a simple implementation that just forwards the message to the model
        # without MCP processing
        try:
            result = await self.model.chat(message.model_dump())
            return MCPMessage(**result)
        except Exception as e:
            logger.error(f"Error processing message through MCP: {str(e)}")
            return message

    async def execute_tool(
        self, server_name: str, tool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool on an MCP server.

        Args:
            server_name: The name of the server to execute the tool on
            tool_name: The name of the tool to execute
            params: Parameters for the tool execution

        Returns:
            The result of the tool execution
        """
        if server_name not in self.active_connections:
            raise ValueError(f"Not connected to MCP server: {server_name}")

        client = self.active_connections[server_name]
        return await client.execute_tool(name=tool_name, arguments=params)

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List tools available on an MCP server.

        Args:
            server_name: The name of the server to list tools for

        Returns:
            A list of available tools
        """
        if server_name not in self.active_connections:
            raise ValueError(f"Not connected to MCP server: {server_name}")

        client = self.active_connections[server_name]
        return await client.send_message(method="listTools", params={})
