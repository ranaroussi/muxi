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
        from mcp.client import MCPClient  # type: ignore
        print("\nFound MCPClient class")
        print(f"MCPClient info: {MCPClient.__module__}.{MCPClient.__name__}")
    except ImportError as e:
        print(f"\nFailed to import MCPClient: {e}")
    except AttributeError:
        print("\nMCPClient attribute does not exist in mcp.client")

except ImportError as e:
    print(f"\nFailed to import client module: {e}")

# Use a type ignore comment to prevent mypy error about the missing module
try:
    from mcp import transport  # type: ignore
    print("\nFound transport module:")
    print(dir(transport))

    try:
        from mcp.transport import HTTPSSETransport  # type: ignore
        print("\nFound HTTPSSETransport class")
        print(f"HTTPSSETransport info: {HTTPSSETransport.__module__}.{HTTPSSETransport.__name__}")
    except ImportError as e:
        print(f"\nFailed to import HTTPSSETransport: {e}")
    except AttributeError:
        print("\nHTTPSSETransport attribute does not exist in mcp.transport")

except ImportError as e:
    print(f"\nFailed to import transport module: {e}")
