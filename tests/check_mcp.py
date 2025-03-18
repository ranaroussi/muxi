"""
Check the contents of the MCP module.
"""

import mcp
print("MCP module contents:")
print(dir(mcp))

try:
    from mcp import client
    print("\nFound client module:")
    print(dir(client))

    try:
        from mcp.client import MCPClient
        print("\nFound MCPClient class")
    except ImportError as e:
        print(f"\nFailed to import MCPClient: {e}")

except ImportError as e:
    print(f"\nFailed to import client module: {e}")

try:
    from mcp import transport
    print("\nFound transport module:")
    print(dir(transport))

    try:
        from mcp.transport import HTTPSSETransport
        print("\nFound HTTPSSETransport class")
    except ImportError as e:
        print(f"\nFailed to import HTTPSSETransport: {e}")

except ImportError as e:
    print(f"\nFailed to import transport module: {e}")
