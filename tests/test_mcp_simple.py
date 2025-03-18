#!/usr/bin/env python3
"""
Simple standalone test for MCP server connectivity.
"""

import asyncio
import uuid
import httpx
from mcp import JSONRPCRequest


class SimpleHttpTransport:
    """Simple HTTP transport for testing MCP connectivity."""

    def __init__(self, url):
        self.url = url
        self.client = None

    async def connect(self):
        """Connect to the server."""
        self.client = httpx.AsyncClient()
        return True

    async def send_request(self, method, params=None):
        """Send a JSON-RPC request."""
        if params is None:
            params = {}

        request = JSONRPCRequest(
            method=method,
            params=params,
            jsonrpc="2.0",
            id=str(uuid.uuid4())
        )

        # Convert to dictionary
        request_data = request.model_dump()
        print(f"Sending request: {request_data}")

        # Send the request
        response = await self.client.post(
            self.url,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Check for errors
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            return None

        # Parse response
        try:
            response_data = response.json()
            print(f"Received response: {response_data}")
            return response_data
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None

    async def disconnect(self):
        """Disconnect from the server."""
        if self.client:
            await self.client.aclose()
            self.client = None
        return True


async def test_mcp_connectivity():
    """Test basic connectivity to an MCP server."""
    # Server URL
    url = "https://router.mcp.so/sse/4ertmsm8erwh60"

    # Create transport
    transport = SimpleHttpTransport(url)

    try:
        # Connect
        await transport.connect()
        print(f"Connected to {url}")

        # Send ping request
        print("\nTesting ping...")
        response = await transport.send_request("ping")
        if response:
            print("Ping successful!")
        else:
            print("Ping failed.")

        # Try to list tools if ping succeeded
        if response:
            print("\nListing tools...")
            tools_response = await transport.send_request("listTools")
            if tools_response:
                print("Tool listing successful!")
                if "result" in tools_response:
                    tools = tools_response.get("result", [])
                    print(f"Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool.get('name')}: {tool.get('description')}")
            else:
                print("Tool listing failed.")

    except Exception as e:
        print(f"Error during test: {e}")

    finally:
        # Disconnect
        await transport.disconnect()
        print("Disconnected from server")


if __name__ == "__main__":
    asyncio.run(test_mcp_connectivity())
