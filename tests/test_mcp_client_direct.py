#!/usr/bin/env python3
"""
Direct MCP client test using the SDK's client.
"""

import asyncio
from mcp.client.session import ClientSession as MCPClient


async def test_direct_client():
    """Test connecting to an MCP server using the SDK client directly."""
    url = "https://router.mcp.so/sse/4ertmsm8erwh60"
    print(f"Connecting to MCP server at {url}...")

    # Create client
    client = MCPClient()

    try:
        # Connect to server
        await client.connect(url)
        print("Connected successfully")

        # Send ping request
        response = await client.request("ping")
        print(f"Ping response: {response}")

    except Exception as e:
        print(f"Error connecting to MCP server: {str(e)}")

    finally:
        # Disconnect
        try:
            await client.disconnect()
            print("Disconnected")
        except Exception as e:
            print(f"Error disconnecting: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_direct_client())
