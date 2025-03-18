"""
Simplified tests for the MCPHandler class.
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Add package path
package_path = os.path.join(project_root, "packages", "core", "src")
sys.path.insert(0, package_path)

# Import the handler directly from the file
from muxi.core.mcp_handler import MCPHandler


class SimpleModel:
    """A simplified model class for testing."""

    async def chat(self, messages):
        """Simulate a chat response."""
        return "This is a test response"


class TestMCPHandler(unittest.IsolatedAsyncioTestCase):
    """Simple test case for the MCPHandler class."""

    async def test_handler_creation(self):
        """Test creating the handler."""
        model = SimpleModel()
        handler = MCPHandler(model=model)
        self.assertIsNotNone(handler)
        self.assertEqual(handler.model, model)
        print("MCPHandler instance created successfully!")


if __name__ == "__main__":
    unittest.main()
