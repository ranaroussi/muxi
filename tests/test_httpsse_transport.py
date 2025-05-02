"""
Test for the HTTP+SSE transport implementation.

This test verifies that our HTTPSSETransport class can connect to a real MCP server
and send/receive messages using HTTP+SSE.
"""

import asyncio
import os
import sys
import uuid
import pytest

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Now import modules that require the path to be set up
from mcp import JSONRPCRequest  # noqa: E402
from muxi.core.mcp.handler import HTTPSSETransport  # noqa: E402


@pytest.mark.skip(reason="This test requires a real MCP server and the URL is invalid or outdated")
async def test_httpsse_transport():
    """Test the HTTP+SSE transport with a real MCP server."""
    # MCP server URL provided by the user
    server_url = "https://router.mcp.so/sse/4ertmsm8erwh60"

    print(f"Connecting to MCP server at {server_url}...")

    # Create a transport instance
    transport = HTTPSSETransport(server_url)

    try:
        # Connect to the server
        connected = await transport.connect()
        assert connected is True, "Failed to connect to MCP server"
        print("Successfully connected to MCP server.")

        # Create a simple ping request
        request = JSONRPCRequest(
            method="ping",
            params={},
            jsonrpc="2.0",
            id=str(uuid.uuid4())
        )

        print(f"Sending request: {request.model_dump()}")

        # Send the request
        response = await transport.send_request(request.model_dump())
        print(f"Received response: {response}")
        assert "result" in response, "Expected result in response"

    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}")

    finally:
        # Disconnect from the server
        print("Disconnecting from MCP server...")
        await transport.disconnect()
        print("Disconnected.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_httpsse_transport())
