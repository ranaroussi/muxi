"""
Check the mcp.shared module structure.
"""

try:
    import mcp.shared
    print("Found mcp.shared module")
    print("Contents:", dir(mcp.shared))

    try:
        from mcp.shared import types
        print("\nFound mcp.shared.types module")
        print("Contents:", dir(types))
    except ImportError as e:
        print(f"\nFailed to import mcp.shared.types: {e}")
except ImportError as e:
    print(f"Failed to import mcp.shared: {e}")

try:
    from mcp import shared
    print("\nImported mcp.shared directly")
    print("Contents:", dir(shared))
except ImportError as e:
    print(f"\nFailed to import shared directly: {e}")

print("\nChecking JSON-RPC related classes in mcp module...")
json_rpc_classes = [name for name in dir(mcp) if "JSONRPC" in name]
print("JSON-RPC classes:", json_rpc_classes)
