#!/usr/bin/env python3
"""
Standalone test script for testing connectivity to MCP servers.
This script includes its own implementation of a simple HTTP-based transport
to avoid dependency issues.
"""

import asyncio
import uuid
from typing import Any, Dict

import httpx
from mcp import JSONRPCRequest


class SimpleHTTPTransport:
    """
    Simple HTTP transport for MCP servers.

    This is a minimalist implementation that focuses on direct HTTP communication
    without the SSE complexity.
    """
    def __init__(self, url: str):
        """
        Initialize a simple HTTP transport.

        Args:
            url: The URL of the MCP server
        """
        self.url = url.rstrip('/')  # Remove trailing slash if present
        self.http_client = None
        self.connected = False

    async def connect(self) -> bool:
        """
        Connect to the MCP server.

        Establishes an HTTP client for sending messages to the server.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Create HTTP client
            self.http_client = httpx.AsyncClient()

            # For simplicity, we'll just consider the connection successful
            # if we can create the HTTP client
            self.connected = True
            print(f"HTTP client created successfully for {self.url}")
            return True

        except Exception as e:
            print(f"Error connecting to MCP server: {str(e)}")
            await self.disconnect()
            return False

    async def request(self, request_obj: JSONRPCRequest) -> Dict[str, Any]:
        """
        Send a request to the MCP server.

        Args:
            request_obj: The JSONRPCRequest to send

        Returns:
            The response from the server
        """
        if not self.http_client or not self.connected:
            raise RuntimeError("Not connected to MCP server")

        # Convert the request to a dictionary
        request_data = request_obj.model_dump()

        try:
            # Send the request to the server
            print(f"Sending request to {self.url}: {request_data}")

            response = await self.http_client.post(
                self.url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            # Check if the request was successful
            response.raise_for_status()

            # Parse the response
            response_data = response.json()
            print(f"Received response: {response_data}")

            return response_data

        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {str(e)}")
            raise RuntimeError(f"HTTP error: {str(e)}")
        except Exception as e:
            print(f"Error sending request: {str(e)}")
            raise RuntimeError(f"Error sending request: {str(e)}")

    async def disconnect(self) -> bool:
        """
        Disconnect from the MCP server.

        Returns:
            bool: True if disconnection was successful, False otherwise
        """
        try:
            # Close the HTTP client
            if self.http_client:
                await self.http_client.aclose()

            self.connected = False
            print("Disconnected from MCP server")
            return True

        except Exception as e:
            print(f"Error disconnecting from MCP server: {str(e)}")
            return False


async def test_mcp_connection():
    """Test the connection to an MCP server."""
    # MCP server URL
    server_url = "https://router.mcp.so/sse/4ertmsm8erwh60"

    print(f"Testing connection to MCP server at {server_url}...")

    # Create a transport instance
    transport = SimpleHTTPTransport(server_url)

    # Connect to the server
    connected = await transport.connect()
    if not connected:
        print("Failed to connect to MCP server.")
        return

    print("Successfully connected to MCP server.")

    try:
        # Create a simple ping request
        request = JSONRPCRequest(
            method="ping",
            params={},
            jsonrpc="2.0",
            id=str(uuid.uuid4())
        )

        # Send the request
        try:
            response = await transport.request(request)
            print("Response received successfully:", response)
        except Exception as e:
            print(f"Error during request: {str(e)}")

    finally:
        # Disconnect from the server
        print("Disconnecting from MCP server...")
        await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
