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
import uuid
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
import asyncio
import httpx
import time
from datetime import datetime
from mcp import JSONRPCRequest

from loguru import logger


class MCPError(Exception):
    """Base exception class for MCP-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(f"{message}" + (f": {json.dumps(details)}" if details else ""))


class MCPConnectionError(MCPError):
    """Exception raised for connection-related errors."""
    pass


class MCPRequestError(MCPError):
    """Exception raised for errors when making requests to MCP servers."""
    pass


class MCPTimeoutError(MCPError):
    """Exception raised when MCP operations time out."""
    pass


class MCPCancelledError(MCPError):
    """Exception raised when an MCP operation is cancelled."""
    pass


class CancellationToken:
    """A token that can be used to cancel async operations."""

    def __init__(self):
        self.cancelled = False
        self._tasks = set()

    def cancel(self):
        """Mark the token as cancelled and cancel all registered tasks."""
        self.cancelled = True
        for task in self._tasks:
            if not task.done():
                task.cancel()

    def register(self, task):
        """Register a task to be cancelled when this token is cancelled."""
        self._tasks.add(task)

    def unregister(self, task):
        """Unregister a task."""
        if task in self._tasks:
            self._tasks.remove(task)

    def throw_if_cancelled(self):
        """Throw an exception if this token has been cancelled."""
        if self.cancelled:
            raise MCPCancelledError("Operation was cancelled", {
                "timestamp": datetime.now().isoformat()
            })


class BaseTransport:
    """Base class for all MCP transport implementations."""

    async def connect(self) -> bool:
        """Connect to the MCP server."""
        raise NotImplementedError("Subclasses must implement connect()")

    async def send_request(self, request_obj: Any) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        raise NotImplementedError("Subclasses must implement send_request()")

    async def disconnect(self) -> bool:
        """Disconnect from the MCP server."""
        raise NotImplementedError("Subclasses must implement disconnect()")


class HTTPSSETransport(BaseTransport):
    """HTTP+SSE transport for MCP servers."""

    def __init__(self, url: str, request_timeout: int = 60):
        """Initialize with server URL.

        Args:
            url: Base URL of the MCP server
            request_timeout: Timeout for requests in seconds
        """
        self.base_url = url
        self.sse_url = url if '/sse' in url else f"{url.rstrip('/')}/sse"
        self.message_url = None
        self.session_id = None
        self.client = httpx.AsyncClient(timeout=request_timeout)
        self.sse_connection = None
        self.connected = False
        self.request_timeout = request_timeout
        self.connect_time = None
        self.last_activity = None

    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            # Initialize SSE connection with proper headers
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }

            start_time = time.time()
            logger.info(f"Connecting to SSE endpoint: {self.sse_url}")

            # Use the stream context manager properly
            async with self.client.stream(
                'GET', self.sse_url, headers=headers, timeout=self.request_timeout
            ) as response:
                self.sse_connection = response
                connection_time = time.time() - start_time

                if response.status_code != 200:
                    error_details = {
                        "status_code": response.status_code,
                        "url": self.sse_url,
                        "headers": dict(response.headers),
                        "connection_time_s": connection_time,
                        "timestamp": datetime.now().isoformat()
                    }
                    logger.error(f"Failed to connect to SSE endpoint: {response.status_code}")
                    raise MCPConnectionError(
                        f"Failed to connect to SSE endpoint (status {response.status_code})",
                        error_details
                    )

                logger.info(
                    f"SSE connection established: {response.status_code} in {connection_time:.2f}s"
                )

                # Process SSE events to get endpoint info
                found_endpoint = False
                async for line in response.aiter_lines():
                    logger.debug(f"SSE event: {line}")

                    if line.startswith("event: endpoint"):
                        # Next line should contain the data
                        continue

                    if line.startswith("data:") and self.message_url is None:
                        message_path = line[5:].strip()
                        logger.info(f"Found endpoint data: {message_path}")

                        # Make sure it's a full URL
                        if message_path.startswith('http'):
                            self.message_url = message_path
                        else:
                            # Handle relative paths
                            server_base = self.base_url
                            if '/sse' in server_base:
                                server_base = server_base.split('/sse')[0]
                            else:
                                server_base = server_base.rstrip('/')

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
                            logger.info(f"Session ID: {self.session_id}")
                            self.connected = True
                            self.connect_time = datetime.now()
                            self.last_activity = self.connect_time
                            found_endpoint = True
                            break

                # If we found the endpoint info, we're connected
                if found_endpoint:
                    return True

                # If we got here without finding an endpoint, the connection failed
                error_details = {
                    "url": self.sse_url,
                    "status_code": response.status_code,
                    "connection_time_s": connection_time,
                    "timestamp": datetime.now().isoformat()
                }
                logger.error("Failed to extract endpoint information from SSE")
                raise MCPConnectionError(
                    "Failed to extract endpoint information from SSE stream",
                    error_details
                )

        except httpx.TimeoutException as e:
            error_details = {
                "url": self.sse_url,
                "timeout_seconds": self.request_timeout,
                "error_type": "timeout",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Timeout connecting to MCP server: {str(e)}")
            raise MCPTimeoutError("Connection to SSE endpoint timed out", error_details) from e

        except asyncio.CancelledError:
            logger.info("SSE connection attempt was cancelled")
            raise MCPCancelledError("SSE connection attempt was cancelled", {
                "url": self.sse_url,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            error_details = {
                "url": self.sse_url,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error connecting to MCP server: {str(e)}")
            raise MCPConnectionError("Error connecting to MCP server", error_details) from e

    async def listen_for_events(
            self,
            callback: Optional[Callable] = None,
            cancellation_token: Optional[CancellationToken] = None
    ) -> AsyncGenerator:
        """Listen for SSE events."""
        if not self.sse_connection:
            logger.error("Cannot listen for events: No SSE connection")
            return

        try:
            async for line in self.sse_connection.aiter_lines():
                if cancellation_token:
                    cancellation_token.throw_if_cancelled()

                self.last_activity = datetime.now()
                if callback:
                    await callback(line)
                yield line
        except asyncio.CancelledError:
            logger.info("SSE event listener was cancelled")
            raise MCPCancelledError("SSE event listener was cancelled", {
                "url": self.sse_url,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            error_details = {
                "url": self.sse_url,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error listening for SSE events: {str(e)}")
            raise MCPConnectionError("Error listening for SSE events", error_details) from e

    async def send_request(
            self,
            request_obj: Any,
            cancellation_token: Optional[CancellationToken] = None
    ) -> Dict[str, Any]:
        """Send request to the server.

        Args:
            request_obj: A request object with model_dump() method or a dictionary
            cancellation_token: Optional token to cancel the operation

        Returns:
            Dict containing the response or status information
        """
        if not self.message_url or not self.session_id:
            raise MCPConnectionError("Not connected to MCP server", {
                "message_url_exists": self.message_url is not None,
                "session_id_exists": self.session_id is not None,
                "timestamp": datetime.now().isoformat()
            })

        # Convert request to dictionary
        if hasattr(request_obj, "model_dump"):
            request_data = request_obj.model_dump()
        else:
            request_data = request_obj

        # Ensure session ID is included
        url = self.message_url
        if "sessionId=" not in url and "session_id=" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}sessionId={self.session_id}"

        method_name = request_data.get('method', 'unknown')
        request_id = request_data.get('id', str(uuid.uuid4()))
        logger.info(f"Sending request to {url}: {method_name} (id: {request_id})")

        try:
            if cancellation_token:
                cancellation_token.throw_if_cancelled()

            start_time = time.time()

            # Send request and handle 202 Accepted (async processing)
            response = await self.client.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            request_time = time.time() - start_time
            self.last_activity = datetime.now()

            logger.info(f"Response status: {response.status_code} in {request_time:.2f}s")

            if response.status_code == 202:
                # Server accepted the request asynchronously
                logger.info(f"Request accepted asynchronously: {method_name} (id: {request_id})")
                return {
                    "status": "accepted",
                    "request_id": request_id,
                    "method": method_name,
                    "request_time_s": request_time
                }

            elif response.status_code < 300:
                # Server returned immediate result
                try:
                    return response.json()
                except Exception:
                    resp_text = (
                        response.text[:100] + "..." if len(response.text) > 100
                        else response.text
                    )
                    logger.warning(
                        f"Non-JSON response with status {response.status_code}: {resp_text}"
                    )
                    return {
                        "status": "success",
                        "response": response.text,
                        "request_id": request_id,
                        "method": method_name,
                        "request_time_s": request_time
                    }
            else:
                error_details = {
                    "status_code": response.status_code,
                    "url": url,
                    "method": method_name,
                    "request_id": request_id,
                    "response_text": response.text[:500],
                    "request_time_s": request_time,
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"Request failed: {response.status_code}")
                raise MCPRequestError(
                    f"Request failed with status {response.status_code}",
                    error_details
                )

        except httpx.TimeoutException as e:
            error_details = {
                "url": url,
                "method": method_name,
                "request_id": request_id,
                "timeout_seconds": self.request_timeout,
                "error_type": "timeout",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Request timed out: {str(e)}")
            raise MCPTimeoutError("Request timed out", error_details) from e

        except asyncio.CancelledError:
            logger.info(f"Request was cancelled: {method_name} (id: {request_id})")
            raise MCPCancelledError("Request was cancelled", {
                "url": url,
                "method": method_name,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            if isinstance(e, MCPError):
                raise

            error_details = {
                "url": url,
                "method": method_name,
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error sending request: {str(e)}")
            raise MCPRequestError("Error sending request", error_details) from e

    async def disconnect(self) -> bool:
        """Disconnect from MCP server."""
        try:
            if self.sse_connection:
                await self.sse_connection.aclose()

            await self.client.aclose()
            self.connected = False
            logger.info("Disconnected from MCP server")
            return True
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error disconnecting: {str(e)}")
            raise MCPConnectionError("Error disconnecting from MCP server", error_details) from e

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about this connection."""
        stats = {
            "connected": self.connected,
            "type": "http",
            "base_url": self.base_url,
            "session_id": self.session_id,
            "current_time": datetime.now().isoformat()
        }

        if self.connect_time:
            stats["connect_time"] = self.connect_time.isoformat()
            stats["connection_age_s"] = (datetime.now() - self.connect_time).total_seconds()

        if self.last_activity:
            stats["last_activity"] = self.last_activity.isoformat()
            stats["idle_time_s"] = (datetime.now() - self.last_activity).total_seconds()

        return stats


class CommandLineTransport(BaseTransport):
    """Command-line transport for MCP servers."""

    def __init__(self, command: str):
        """Initialize with command to start the server.

        Args:
            command: Command to start the server process
        """
        self.command = command
        self.process = None
        self.stdin = None
        self.stdout = None
        self.connected = False
        self.connect_time = None
        self.last_activity = None
        self.session_id = str(uuid.uuid4())  # Generate a unique session ID

    async def connect(self) -> bool:
        """Start the server process and establish connection."""
        try:
            logger.info(f"Starting MCP server process: {self.command}")
            start_time = time.time()

            # Start the process
            self.process = await asyncio.create_subprocess_shell(
                self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            connection_time = time.time() - start_time

            if self.process:
                self.stdin = self.process.stdin
                self.stdout = self.process.stdout
                self.connected = True
                self.connect_time = datetime.now()
                self.last_activity = self.connect_time

                logger.info(
                    f"MCP server process started with PID {self.process.pid} "
                    f"in {connection_time:.2f}s"
                )
                return True
            else:
                error_details = {
                    "command": self.command,
                    "connection_time_s": connection_time,
                    "timestamp": datetime.now().isoformat()
                }
                logger.error("Failed to start MCP server process")
                raise MCPConnectionError("Failed to start MCP server process", error_details)

        except asyncio.CancelledError:
            logger.info("Process start was cancelled")
            raise MCPCancelledError("Process start was cancelled", {
                "command": self.command,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            error_details = {
                "command": self.command,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error starting MCP server process: {str(e)}")
            raise MCPConnectionError("Error starting MCP server process", error_details) from e

    async def send_request(
            self,
            request_obj: Any,
            cancellation_token: Optional[CancellationToken] = None
    ) -> Dict[str, Any]:
        """Send a request to the MCP server process.

        Args:
            request_obj: A request object with model_dump() method or a dictionary
            cancellation_token: Optional token to cancel the operation

        Returns:
            Dict containing the response
        """
        if not self.connected or not self.stdin or not self.stdout:
            raise MCPConnectionError("Not connected to MCP server process", {
                "connected": self.connected,
                "stdin_exists": self.stdin is not None,
                "stdout_exists": self.stdout is not None,
                "timestamp": datetime.now().isoformat()
            })

        # Convert request to dictionary
        if hasattr(request_obj, "model_dump"):
            request_data = request_obj.model_dump()
        else:
            request_data = request_obj

        method_name = request_data.get('method', 'unknown')
        request_id = request_data.get('id', str(uuid.uuid4()))
        logger.info(f"Sending request to process: {method_name} (id: {request_id})")

        try:
            if cancellation_token:
                cancellation_token.throw_if_cancelled()

            start_time = time.time()

            # Send request to process stdin
            request_json = json.dumps(request_data) + "\n"
            self.stdin.write(request_json.encode())
            await self.stdin.drain()

            # Read response from process stdout
            response_line = await self.stdout.readline()

            request_time = time.time() - start_time
            self.last_activity = datetime.now()

            logger.info(f"Received response in {request_time:.2f}s")

            if not response_line:
                error_details = {
                    "method": method_name,
                    "request_id": request_id,
                    "request_time_s": request_time,
                    "timestamp": datetime.now().isoformat()
                }
                logger.error("Empty response from MCP server process")
                raise MCPRequestError("Empty response from MCP server process", error_details)

            try:
                response_data = json.loads(response_line.decode())
                return response_data
            except json.JSONDecodeError as e:
                response_text = (
                    response_line.decode()[:100] + "..."
                    if len(response_line) > 100 else response_line.decode()
                )
                error_details = {
                    "method": method_name,
                    "request_id": request_id,
                    "response_text": response_text,
                    "request_time_s": request_time,
                    "error_type": "json_decode_error",
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"Invalid JSON response: {str(e)}")
                raise MCPRequestError(
                    "Invalid JSON response from MCP server process",
                    error_details
                ) from e

        except asyncio.CancelledError:
            logger.info(f"Request was cancelled: {method_name} (id: {request_id})")
            raise MCPCancelledError("Request was cancelled", {
                "method": method_name,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            if isinstance(e, MCPError):
                raise

            error_details = {
                "method": method_name,
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error sending request: {str(e)}")
            raise MCPRequestError(
                "Error sending request to MCP server process",
                error_details
            ) from e

    async def disconnect(self) -> bool:
        """Terminate the server process."""
        try:
            if self.process:
                # Close stdin to signal end of input
                if self.stdin:
                    self.stdin.close()

                # Terminate process if it's still running
                if self.process.returncode is None:
                    logger.info(f"Terminating MCP server process (PID {self.process.pid})")
                    self.process.terminate()

                    # Wait for process to terminate
                    try:
                        await asyncio.wait_for(self.process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        logger.warning(
                            f"Process didn't terminate, killing it (PID {self.process.pid})"
                        )
                        self.process.kill()

                # Reset state
                self.process = None
                self.stdin = None
                self.stdout = None
                self.connected = False

                logger.info("Disconnected from MCP server process")
                return True

            return True  # Already disconnected

        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error disconnecting from MCP server process: {str(e)}")
            raise MCPConnectionError(
                "Error disconnecting from MCP server process",
                error_details
            ) from e

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about this connection."""
        stats = {
            "connected": self.connected,
            "type": "command",
            "command": self.command,
            "session_id": self.session_id,
            "current_time": datetime.now().isoformat()
        }

        if self.process:
            stats["pid"] = self.process.pid
            stats["returncode"] = self.process.returncode

        if self.connect_time:
            stats["connect_time"] = self.connect_time.isoformat()
            stats["connection_age_s"] = (datetime.now() - self.connect_time).total_seconds()

        if self.last_activity:
            stats["last_activity"] = self.last_activity.isoformat()
            stats["idle_time_s"] = (datetime.now() - self.last_activity).total_seconds()

        return stats


class MCPTransportFactory:
    """Factory class for creating MCP transport instances."""

    @staticmethod
    def create_transport(
        url: Optional[str] = None,
        command: Optional[str] = None,
        **kwargs
    ) -> BaseTransport:
        """Create a transport instance based on parameters.

        Args:
            url: URL for HTTP-based MCP servers
            command: Command for command-line based MCP servers
            **kwargs: Additional parameters for transport initialization

        Returns:
            An instance of BaseTransport

        Raises:
            ValueError: If neither url nor command is provided, or if both are provided
        """
        logger.info("Creating transport based on provided parameters")

        if url is not None and command is not None:
            raise ValueError(
                "Cannot provide both url and command. "
                "Use url for HTTP servers and command for command-line servers."
            )

        if url is None and command is None:
            raise ValueError("Must provide either url or command.")

        if url is not None:
            request_timeout = kwargs.get('request_timeout', 60)
            return HTTPSSETransport(url, request_timeout)
        else:  # command is not None
            return CommandLineTransport(command)

    @staticmethod
    def supports_parameters(
        url: Optional[str] = None,
        command: Optional[str] = None
    ) -> bool:
        """Check if the provided parameters are supported.

        Args:
            url: URL for HTTP-based MCP servers
            command: Command for command-line based MCP servers

        Returns:
            True if parameters are supported, False otherwise
        """
        if url is not None and command is not None:
            return False
        if url is None and command is None:
            return False
        return True


class MCPServerClient:
    """
    Client for a specific MCP server.

    This class manages a connection to an MCP server using the MCP SDK.
    """
    def __init__(
        self,
        name: str,
        url: Optional[str] = None,
        command: Optional[str] = None,
        credentials: Optional[Dict[str, Any]] = None,
        request_timeout: int = 60
    ):
        """
        Initialize an MCP server client.

        Args:
            name: The name of the server (for identification)
            url: The URL for HTTP-based MCP servers
            command: The command for command-line MCP servers
            credentials: Credentials for the server (optional)
            request_timeout: Timeout for requests in seconds
        """
        self.name = name
        self.url = url
        self.command = command
        self.credentials = credentials or {}
        self.client = None
        self.connected = False
        self.transport = None
        self.request_timeout = request_timeout
        self.active_requests = {}  # Map of request_id -> CancellationToken

    async def connect(self) -> bool:
        """
        Connect to the MCP server.

        Returns:
            bool: True if connection was successful

        Raises:
            MCPConnectionError: If connection fails
        """
        try:
            # Create transport using factory
            self.transport = MCPTransportFactory.create_transport(
                url=self.url,
                command=self.command,
                request_timeout=self.request_timeout
            )

            # Connect the transport
            await self.transport.connect()

            # If we get here, the connection was successful
            # (otherwise an exception would have been raised)
            self.connected = True

            transport_type = "http" if self.url else "command"
            logger.info(
                f"Successfully connected to MCP server '{self.name}' "
                f"using {transport_type} transport"
            )

            return True

        except Exception as e:
            error_details = {
                "server_name": self.name,
                "url": self.url,
                "command": self.command,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            if isinstance(e, MCPError):
                # Propagate MCP errors with additional context
                e.details.update({"server_name": self.name})
                raise

            logger.error(f"Failed to connect to MCP server '{self.name}': {str(e)}")
            raise MCPConnectionError(
                f"Failed to connect to MCP server '{self.name}'",
                error_details
            ) from e

    async def disconnect(self) -> bool:
        """
        Disconnect from the MCP server.

        Returns:
            bool: True if disconnection was successful
        """
        try:
            # Cancel any active requests
            for request_id, token in self.active_requests.items():
                logger.info(f"Cancelling request {request_id} during disconnect")
                token.cancel()

            self.active_requests.clear()

            if self.transport:
                await self.transport.disconnect()

            self.connected = False
            self.transport = None
            logger.info(f"Disconnected from MCP server '{self.name}'")

            return True

        except Exception as e:
            error_details = {
                "server_name": self.name,
                "url": self.url,
                "command": self.command,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            if isinstance(e, MCPError):
                # Propagate MCP errors with additional context
                e.details.update({"server_name": self.name})
                raise

            logger.error(f"Error disconnecting from MCP server '{self.name}': {str(e)}")
            raise MCPConnectionError(
                f"Error disconnecting from MCP server '{self.name}'",
                error_details
            ) from e

    async def send_message(
            self,
            method: str,
            params: Dict[str, Any],
            cancellation_token: Optional[CancellationToken] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the MCP server.

        Args:
            method: The method to call
            params: The parameters to pass to the method
            cancellation_token: Optional token to cancel the operation

        Returns:
            Dict[str, Any]: The response from the server

        Raises:
            MCPConnectionError: If not connected to an MCP server
            MCPRequestError: If the request fails
            MCPTimeoutError: If the request times out
            MCPCancelledError: If the request is cancelled
        """
        if not self.connected or not self.transport:
            raise MCPConnectionError(f"Not connected to MCP server '{self.name}'", {
                "server_name": self.name,
                "connected": self.connected,
                "transport_exists": self.transport is not None
            })

        # Create a new request ID
        request_id = str(uuid.uuid4())

        # Create a new cancellation token if one wasn't provided
        own_token = cancellation_token is None
        if own_token:
            cancellation_token = CancellationToken()

        # Create the request object
        request = JSONRPCRequest(
            jsonrpc="2.0",
            method=method,
            params=params,
            id=request_id
        )

        try:
            # Track the request
            self.active_requests[request_id] = cancellation_token

            # Add credentials if provided
            if self.credentials and params is not None:
                # Merge credentials with params
                for key, value in self.credentials.items():
                    if key not in params:
                        request.params[key] = value

            # Send the request
            logger.info(f"Sending message to MCP server '{self.name}': {method} (id: {request_id})")
            # Convert the request to a dict for the transport
            request_dict = request.model_dump()
            response = await self.transport.send_request(request_dict, cancellation_token)

            return response

        except Exception as e:
            error_details = {
                "server_name": self.name,
                "method": method,
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            if isinstance(e, MCPError):
                # Propagate MCP errors with additional context
                e.details.update({"server_name": self.name})
                raise

            logger.error(f"Error sending message to MCP server '{self.name}': {str(e)}")
            raise MCPRequestError(
                f"Error sending message to MCP server '{self.name}'",
                error_details
            ) from e

        finally:
            # Clean up
            if request_id in self.active_requests:
                del self.active_requests[request_id]

    async def execute_tool(
            self,
            tool_name: str,
            params: Dict[str, Any],
            cancellation_token: Optional[CancellationToken] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool on the MCP server.

        Args:
            tool_name: The name of the tool to execute
            params: The parameters to pass to the tool
            cancellation_token: Optional token to cancel the operation

        Returns:
            Dict[str, Any]: The result of the tool execution
        """
        return await self.send_message(tool_name, params, cancellation_token)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about this connection."""
        stats = {
            "server_name": self.name,
            "connected": self.connected,
            "url": self.url,
            "command": self.command,
            "active_requests": len(self.active_requests),
            "current_time": datetime.now().isoformat()
        }

        # Add transport-specific stats if available
        if self.transport and hasattr(self.transport, "get_connection_stats"):
            transport_stats = self.transport.get_connection_stats()
            stats.update(transport_stats)

        return stats

    def cancel_all_requests(self) -> int:
        """Cancel all active requests.

        Returns:
            int: Number of requests cancelled
        """
        count = len(self.active_requests)

        for request_id, token in self.active_requests.items():
            logger.info(f"Cancelling request {request_id}")
            token.cancel()

        self.active_requests.clear()
        return count


class MCPHandler:
    """
    Handler for Model Context Protocol (MCP) servers.

    This class manages connections to MCP servers and handles message processing.
    """

    def __init__(self, model):
        """
        Initialize the MCP handler.

        Args:
            model: The model used for extracting tool calls
        """
        self.model = model
        self.active_connections = {}  # Map of server_name -> MCPServerClient
        self.available_tools = {}  # Map of tool_name -> server_name
        self.cancellation_tokens = {}  # Map of operation_id -> CancellationToken

    async def connect_server(
        self,
        name: str,
        url: Optional[str] = None,
        command: Optional[str] = None,
        credentials: Optional[Dict[str, Any]] = None,
        request_timeout: int = 60
    ) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: The name of the server (for identification)
            url: The URL for HTTP-based MCP servers
            command: The command for command-line MCP servers
            credentials: Credentials for the server (optional)
            request_timeout: Timeout for requests in seconds

        Returns:
            bool: True if connection was successful

        Raises:
            MCPConnectionError: If connection fails
            ValueError: If neither url nor command is provided, or if both are provided
        """
        # Check if we're already connected to this server
        if name in self.active_connections:
            logger.warning(f"Already connected to MCP server '{name}', disconnecting first")
            await self.disconnect_server(name)

        # Check if parameters are supported
        if not MCPTransportFactory.supports_parameters(url=url, command=command):
            if url is not None and command is not None:
                raise ValueError(
                    "Cannot provide both url and command. "
                    "Use url for HTTP servers and command for command-line servers."
                )
            else:  # url is None and command is None
                raise ValueError("Must provide either url or command.")

        try:
            # Create a new client
            client = MCPServerClient(
                name=name,
                url=url,
                command=command,
                credentials=credentials,
                request_timeout=request_timeout
            )

            # Connect the client
            await client.connect()

            # Store the client
            self.active_connections[name] = client

            logger.info(f"Connected to MCP server '{name}'")
            return True

        except Exception as e:
            error_details = {
                "server_name": name,
                "url": url,
                "command": command,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            if isinstance(e, MCPError):
                # Just propagate MCP errors
                raise

            logger.error(f"Failed to connect to MCP server '{name}': {str(e)}")
            raise MCPConnectionError(
                f"Failed to connect to MCP server '{name}'",
                error_details
            ) from e

    async def disconnect_server(self, name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            name: The name of the server to disconnect from

        Returns:
            bool: True if disconnection was successful
        """
        if name not in self.active_connections:
            logger.warning(f"Not connected to MCP server '{name}'")
            return False

        try:
            # Get the client
            client = self.active_connections[name]

            # Disconnect the client
            await client.disconnect()

            # Remove from active connections
            del self.active_connections[name]

            logger.info(f"Disconnected from MCP server '{name}'")
            return True

        except Exception as e:
            error_details = {
                "server_name": name,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            if isinstance(e, MCPError):
                # Just propagate MCP errors
                raise

            logger.error(f"Error disconnecting from MCP server '{name}': {str(e)}")
            raise MCPConnectionError(
                f"Error disconnecting from MCP server '{name}'",
                error_details
            ) from e

    async def process_message(
            self,
            message: Dict[str, Any],
            cancellation_token: Optional[CancellationToken] = None
    ) -> Dict[str, Any]:
        """
        Process a message that may contain tool calls to MCP servers.

        Args:
            message: The message to process
            cancellation_token: Optional token to cancel the operation

        Returns:
            Dict[str, Any]: The processed message
        """
        # If message doesn't contain tool calls, just return it
        if "tool_calls" not in message.get("content", {}):
            return message

        # Create a new cancellation token if one wasn't provided
        operation_id = str(uuid.uuid4())
        own_token = cancellation_token is None
        if own_token:
            cancellation_token = CancellationToken()
            self.cancellation_tokens[operation_id] = cancellation_token

        try:
            # Get the tool calls
            tool_calls = message["content"]["tool_calls"]

            # Process each tool call
            for tool_call in tool_calls:
                try:
                    if cancellation_token:
                        cancellation_token.throw_if_cancelled()

                    # Extract tool details
                    tool_name = tool_call.get("name", "")
                    tool_params = tool_call.get("parameters", {})

                    # Find the server for this tool
                    server_name = self._get_server_for_tool(tool_name)
                    if not server_name:
                        logger.warning(f"No server registered for tool '{tool_name}'")
                        tool_call["output"] = {
                            "error": f"No server registered for tool '{tool_name}'"
                        }
                        continue

                    # Execute the tool
                    logger.info(f"Executing tool '{tool_name}' on server '{server_name}'")
                    result = await self.execute_tool(
                        server_name,
                        tool_name,
                        tool_params,
                        cancellation_token
                    )

                    # Store the result
                    tool_call["output"] = result

                except Exception as e:
                    error_details = {
                        "tool_name": tool_name if 'tool_name' in locals() else "unknown",
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }

                    logger.error(f"Error executing tool call: {str(e)}")
                    tool_call["output"] = {"error": str(e), "details": error_details}

            return message

        finally:
            # Clean up
            if own_token and operation_id in self.cancellation_tokens:
                del self.cancellation_tokens[operation_id]

    async def execute_tool(
            self,
            server_name: str,
            tool_name: str,
            params: Dict[str, Any],
            cancellation_token: Optional[CancellationToken] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool on an MCP server.

        Args:
            server_name: The name of the server to execute the tool on
            tool_name: The name of the tool to execute
            params: The parameters to pass to the tool
            cancellation_token: Optional token to cancel the operation

        Returns:
            Dict[str, Any]: The result of the tool execution

        Raises:
            MCPConnectionError: If not connected to the specified server
        """
        if server_name not in self.active_connections:
            raise MCPConnectionError(f"Not connected to MCP server '{server_name}'")

        client = self.active_connections[server_name]
        return await client.execute_tool(tool_name, params, cancellation_token)

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List tools available on an MCP server.

        Args:
            server_name: The name of the server to list tools for

        Returns:
            List[Dict[str, Any]]: The list of available tools
        """
        if server_name not in self.active_connections:
            raise MCPConnectionError(f"Not connected to MCP server '{server_name}'")

        client = self.active_connections[server_name]

        # The 'list_tools' method is a standard MCP method
        try:
            result = await client.send_message("list_tools", {})
            return result.get("result", [])
        except Exception as e:
            logger.error(f"Error listing tools from server '{server_name}': {str(e)}")
            raise

    def _get_server_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Get the server name for a tool.

        Args:
            tool_name: The name of the tool

        Returns:
            str: The name of the server for this tool, or None if not found
        """
        # First check if we have a mapping for this tool
        if tool_name in self.available_tools:
            return self.available_tools[tool_name]

        # Otherwise, assume the tool is on a server with the same name
        if tool_name in self.active_connections:
            return tool_name

        # As a fallback, check if any server name is a prefix of the tool name
        for server_name in self.active_connections:
            if tool_name.startswith(f"{server_name}."):
                return server_name

        return None

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about all connections."""
        stats = {
            "active_connections": len(self.active_connections),
            "registered_tools": len(self.available_tools),
            "active_operations": len(self.cancellation_tokens),
            "current_time": datetime.now().isoformat(),
            "connections": {}
        }

        # Add stats for each connection
        for name, client in self.active_connections.items():
            if hasattr(client, "get_connection_stats"):
                stats["connections"][name] = client.get_connection_stats()
            else:
                stats["connections"][name] = {"connected": client.connected}

        return stats

    def cancel_all_operations(self) -> int:
        """Cancel all active operations.

        Returns:
            int: Number of operations cancelled
        """
        count = len(self.cancellation_tokens)

        for operation_id, token in self.cancellation_tokens.items():
            logger.info(f"Cancelling operation {operation_id}")
            token.cancel()

        self.cancellation_tokens.clear()

        # Also cancel operations in each client
        for name, client in self.active_connections.items():
            if hasattr(client, "cancel_all_requests"):
                client_count = client.cancel_all_requests()
                logger.info(f"Cancelled {client_count} requests in client '{name}'")
                count += client_count

        return count
