"""
Test for the HTTP+SSE transport implementation.

This test verifies that our HTTPSSETransport class can connect to a real MCP server
and send/receive messages using HTTP+SSE.
"""

import asyncio
import uuid
import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import directly from the file
from packages.core.src.muxi.core.mcp_handler import HTTPSSETransport
from mcp import JSONRPCRequest


async def test_httpsse_transport():
    """Test the HTTP+SSE transport with a real MCP server."""
    # MCP server URL provided by the user
    server_url = "https://router.mcp.so/sse/4ertmsm8erwh60"

    print(f"Connecting to MCP server at {server_url}...")

    # Create a transport instance
    transport = HTTPSSETransport(server_url)

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

        print(f"Sending request: {request.model_dump()}")

        # Send the request
        try:
            response = await transport.request(request)
            print(f"Received response: {response}")
        except Exception as e:
            print(f"Error during request: {str(e)}")

    finally:
        # Disconnect from the server
        print("Disconnecting from MCP server...")
        await transport.disconnect()
        print("Disconnected.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_httpsse_transport())
