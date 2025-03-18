#!/usr/bin/env python3
"""
Direct test of the CommandLineTransport with a real MCP server.

This script tests:
1. Starting an MCP server via command line (npx)
2. Connecting to the server
3. Executing a tool call
4. Verifying the response
5. Gracefully disconnecting

Requirements:
- Node.js and NPM must be installed
- Internet connection to download the server package
"""

import sys
import os
import asyncio
import json
import importlib.util
from datetime import datetime

# Add the project root to the path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Load the mcp_handler module
try:
    # First try direct import
    from packages.core.src.muxi.core.mcp_handler import (
        CommandLineTransport,
        CancellationToken
    )
    print("✅ Successfully imported classes directly")
except ImportError as e:
    print(f"❌ Direct import failed: {e}")
    print("Trying alternative approach with importlib...")

    # Use importlib to load the module
    spec = importlib.util.spec_from_file_location(
        "mcp_handler",
        os.path.join(root_dir, "packages/core/src/muxi/core/mcp_handler.py")
    )
    mcp_handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_handler)

    # Get the classes we need
    CommandLineTransport = mcp_handler.CommandLineTransport
    CancellationToken = mcp_handler.CancellationToken
    print("✅ Successfully imported classes via importlib")


async def test_brave_search_server():
    """Test the CommandLineTransport with a real Brave Search server."""
    print(f"Starting test at {datetime.now()}")

    # Create the transport for the brave search server
    command = "npx -y @modelcontextprotocol/server-brave-search"
    print(f"Starting server with command: {command}")
    transport = CommandLineTransport(command)

    try:
        # Connect to the server (starts the process)
        print("Connecting to the Brave Search server...")
        await transport.connect()
        print(f"Connected: {transport.connected}")

        # Wait longer for the server to initialize
        print("Waiting for server initialization...")
        await asyncio.sleep(5)

        # Perform a search
        request = {
            "jsonrpc": "2.0",
            "method": "search",
            "params": {"query": "what is the Model Context Protocol"},
            "id": "1"
        }

        print(f"Sending request: {json.dumps(request)}")
        result = await transport.send_request(request)
        print(f"Received result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")

        # Verify the result structure
        if isinstance(result, dict) and "result" in result:
            print("✅ Test passed: Received valid search results")
            # Check how many results we got
            if isinstance(result["result"], list):
                print(f"✅ Received {len(result['result'])} search results")
            elif isinstance(result["result"], dict) and "web" in result["result"]:
                print(f"✅ Received search results with {len(result['result']['web'])} web items")
        else:
            print(f"❌ Test failed: Did not receive expected result structure")

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Disconnect (stops the process)
        print("Disconnecting from the server...")
        await transport.disconnect()
        print(f"Disconnected: {not transport.connected}")

    print(f"Test completed at {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(test_brave_search_server())
