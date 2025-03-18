"""
Simple test to verify imports work correctly.
"""

import os
import sys

# Add the project root to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Add the package paths to the system path
package_path = os.path.join(project_root, "packages", "core", "src")
sys.path.insert(0, package_path)

print(f"Python path: {sys.path}")
print(f"Looking for MCP in: {package_path}")

try:
    import mcp
    print(f"Found MCP module at: {mcp.__file__}")
except ImportError as e:
    print(f"Failed to import MCP: {e}")

try:
    from muxi.core.mcp import MCPMessage  # noqa: F401
    print("Successfully imported MCPMessage")
except ImportError as e:
    print(f"Failed to import MCPMessage: {e}")

try:
    from muxi.core.mcp_handler import MCPHandler  # noqa: F401
    print("Successfully imported MCPHandler")
except ImportError as e:
    print(f"Failed to import MCPHandler: {e}")

try:
    from mcp.client.session import ClientSession  # noqa: F401
    print("Successfully imported ClientSession from mcp.client.session")
except ImportError as e:
    print(f"Failed to import ClientSession: {e}")

print("Import test complete")
