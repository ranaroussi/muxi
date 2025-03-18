#!/usr/bin/env python3
"""
Updated MCP Transport implementation based on successful mcpify.ai connection.
This is intended as a reference implementation that we can integrate into the main code later.
"""

import logging
import uuid
import asyncio
import httpx
from typing import Dict, Any, Callable, AsyncGenerator, Optional


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

            logger.info(f"Connecting to SSE endpoint: {self.sse_url}")

            # Use the stream context manager properly
            async with self.client.stream(
                'GET', self.sse_url, headers=headers, timeout=60.0
            ) as response:
                self.sse_connection = response

                if response.status_code != 200:
                    logger.error(
                        f"Failed to connect to SSE endpoint: {response.status_code}"
                    )
                    return False

                logger.info(f"SSE connection established: {response.status_code}")

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
                            found_endpoint = True
                            break

                # If we found the endpoint info, we're connected
                if found_endpoint:
                    return True

                # If we got here without finding an endpoint, the connection failed
                logger.error("Failed to extract endpoint information from SSE")
                return False

        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def listen_for_events(self, callback: Optional[Callable] = None) -> AsyncGenerator:
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

    async def send_request(self, request_obj: Any) -> Dict[str, Any]:
        """Send request to the server.

        Args:
            request_obj: A request object with model_dump() method or a dictionary

        Returns:
            Dict containing the response or status information
        """
        if not self.message_url or not self.session_id:
            raise ValueError("Not connected to MCP server")

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
        logger.info(f"Sending request to {url}: {method_name}")

        try:
            # Send request and handle 202 Accepted (async processing)
            response = await self.client.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            logger.info(f"Response status: {response.status_code}")

            if response.status_code == 202:
                # Server accepted the request asynchronously
                logger.info(f"Request accepted asynchronously: {method_name}")
                return {"status": "accepted", "request_id": request_data.get("id")}

            elif response.status_code < 300:
                # Server returned immediate result
                try:
                    return response.json()
                except Exception:
                    resp_text = response.text[:100] + "..." if len(response.text) > 100 else response.text
                    logger.warning(
                        f"Non-JSON response with status {response.status_code}: {resp_text}"
                    )
                    return {"status": "success", "response": response.text}
            else:
                logger.error(f"Request failed: {response.status_code}")
                raise ValueError(
                    f"Request failed with status {response.status_code}: {response.text}"
                )

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
            logger.info("Disconnected from MCP server")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
            return False


async def test_mcp_server():
    """Test the updated HTTPSSETransport with the mcpify.ai server."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    server_url = "https://server.mcpify.ai/sse?server=6ebcc255-021f-443b-9be3-02233ee4ea41"
    transport = HTTPSSETransport(server_url)

    try:
        print("Connecting to MCP server...")
        connected = await transport.connect()

        if not connected:
            print("Failed to connect to MCP server")
            return

        print(f"Successfully connected to MCP server")
        print(f"Message URL: {transport.message_url}")
        print(f"Session ID: {transport.session_id}")

        # Try sending a ping request
        print("\nSending ping request...")
        ping_request = {
            "jsonrpc": "2.0",
            "method": "ping",
            "params": {},
            "id": str(uuid.uuid4())
        }

        try:
            ping_response = await transport.send_request(ping_request)
            print(f"Ping response: {ping_response}")
        except Exception as e:
            print(f"Error sending ping: {str(e)}")

        # Try sending a weather request
        print("\nSending weather request...")
        weather_request = {
            "jsonrpc": "2.0",
            "method": "get_current_weather",
            "params": {
                "location": "San Francisco",
                "apiKey": "sample_key"  # This is a placeholder
            },
            "id": str(uuid.uuid4())
        }

        try:
            weather_response = await transport.send_request(weather_request)
            print(f"Weather response: {weather_response}")
        except Exception as e:
            print(f"Error sending weather request: {str(e)}")

    finally:
        # Disconnect
        print("\nDisconnecting from MCP server...")
        await transport.disconnect()
        print("Done")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
