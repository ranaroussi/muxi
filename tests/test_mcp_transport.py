#!/usr/bin/env python3
"""
Test for the MCP transport implementation.
This test creates an HTTPSSETransport and uses it with an MCPClient
to connect to an MCP server.
"""

import asyncio
import uuid
from typing import Any, Dict

import httpx
from loguru import logger
from mcp.client.session import ClientSession as MCPClient
from mcp import JSONRPCRequest

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg), level="DEBUG")


class SimpleHTTPTransport:
    """
    Simple HTTP transport for MCP servers.

    This implementation focuses on HTTP communication without SSE.
    """
    def __init__(self, url: str):
        """
        Initialize the transport.

        Args:
            url: The MCP server URL
        """
        self.url = url.rstrip('/')  # Remove trailing slash if present
        self.http_client = None
        self.connected = False

    async def connect(self) -> None:
        """Connect to the MCP server."""
        logger.info(f"Connecting to {self.url}")
        self.http_client = httpx.AsyncClient()
        self.connected = True

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.http_client:
            await self.http_client.aclose()
        self.connected = False
        logger.info("Disconnected from MCP server")

    async def request(self, request_obj: Any) -> Dict[str, Any]:
        """
        Send a request to the server.

        Args:
            request_obj: The request object

        Returns:
            The server response
        """
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")

        # Convert request to dictionary if needed
        if hasattr(request_obj, "model_dump"):
            request_data = request_obj.model_dump()
        else:
            request_data = request_obj

        logger.debug(f"Sending request: {request_data}")

        try:
            response = await self.http_client.post(
                self.url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f"Received response: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Error during request: {str(e)}")
            raise


async def test_mcp_client():
    """Test the MCP client with a custom transport."""
    url = "https://router.mcp.so/sse/4ertmsm8erwh60"

    # Create transport
    transport = SimpleHTTPTransport(url)

    try:
        # Create client with transport
        client = MCPClient(transport=transport)

        # Connect
        await client.connect()
        logger.info("Connected to MCP server")

        # Create and send a ping request
        request = JSONRPCRequest(
            method="ping",
            params={},
            jsonrpc="2.0",
            id=str(uuid.uuid4())
        )

        # Send request
        response = await client.request(request)
        logger.info(f"Ping response: {response}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")

    finally:
        # Disconnect
        if 'client' in locals():
            await client.disconnect()
            logger.info("Disconnected from MCP server")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
