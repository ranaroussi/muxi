"""
Test Model Context Protocol

This module contains tests for the MCP implementation in the muxi framework.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from src.core.mcp import MCPContext, MCPHandler, MCPMessage


class TestMCPMessage(unittest.TestCase):
    """Test cases for the MCPMessage class."""

    def test_create_message(self):
        """Test creating a message."""
        message = MCPMessage(role="user", content="Hello")
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
        self.assertIsNone(message.name)
        self.assertEqual(message.context, {})

    def test_create_tool_message(self):
        """Test creating a message with tool information."""
        message = MCPMessage(
            role="user", content="", name="calculator", context={"input": {"expression": "2+2"}}
        )

        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "")
        self.assertEqual(message.name, "calculator")
        self.assertEqual(message.context["input"], {"expression": "2+2"})

    def test_create_tool_result_message(self):
        """Test creating a tool result message."""
        message = MCPMessage(role="tool", content={"result": "4"}, name="calculator")

        self.assertEqual(message.role, "tool")
        self.assertEqual(message.content, {"result": "4"})
        self.assertEqual(message.name, "calculator")

    def test_to_dict(self):
        """Test converting a message to a dictionary."""
        message = MCPMessage(role="user", content="Hello", name="John")

        message_dict = message.to_dict()
        self.assertEqual(message_dict["role"], "user")
        self.assertEqual(message_dict["content"], "Hello")
        self.assertEqual(message_dict["name"], "John")

    def test_from_dict(self):
        """Test creating a message from a dictionary."""
        message_dict = {
            "role": "assistant",
            "content": "Hello, how can I help?",
            "name": "AI",
            "context": {"timestamp": 1234567890},
        }

        message = MCPMessage.from_dict(message_dict)
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.content, "Hello, how can I help?")
        self.assertEqual(message.name, "AI")
        self.assertEqual(message.context["timestamp"], 1234567890)


class TestMCPContext(unittest.TestCase):
    """Test cases for the MCPContext class."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = MCPContext()

    def test_add_message(self):
        """Test adding a message to the context."""
        self.context.add_message(MCPMessage(role="user", content="Hello"))
        self.context.add_message(MCPMessage(role="assistant", content="Hi there"))

        self.assertEqual(len(self.context.messages), 2)
        self.assertEqual(self.context.messages[0].role, "user")
        self.assertEqual(self.context.messages[1].role, "assistant")

    def test_to_dict(self):
        """Test converting the context to a dictionary."""
        self.context.add_message(MCPMessage(role="user", content="Hello"))
        self.context.metadata = {"session_id": "12345"}

        result = self.context.to_dict()
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["role"], "user")
        self.assertEqual(result["metadata"]["session_id"], "12345")


class TestMCPHandler(unittest.TestCase):
    """Test cases for the MCPHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock()

        # Mock the LLM to return a sample response
        async def mock_async_chat(*args, **kwargs):
            return {"choices": [{"message": {"content": "Sample response", "role": "assistant"}}]}

        self.mock_model.chat = AsyncMock(side_effect=mock_async_chat)

        # Mock tool handler
        async def mock_tool_handler(*args, **kwargs):
            return {"status": "success", "result": "42"}

        mock_handler = AsyncMock(side_effect=mock_tool_handler)
        self.tool_handlers = {"calculator": mock_handler}

        self.handler = MCPHandler(self.mock_model, self.tool_handlers)

    def test_process_message(self):
        """Test processing a regular message."""
        result = asyncio.run(
            self.handler.process_message(MCPMessage(role="user", content="How can you help me?"))
        )

        # Verify result
        self.assertEqual(result.role, "assistant")
        self.assertEqual(
            result.content,
            {"choices": [{"message": {"content": "Sample response", "role": "assistant"}}]},
        )

    def test_process_tool_call(self):
        """Test processing a tool call."""
        result = asyncio.run(
            self.handler.process_tool_call(
                "calculator",
                {"expression": "2+2"},
            )
        )

        # Verify result
        self.assertEqual(result.role, "tool")
        self.assertEqual(result.content, {"status": "success", "result": "42"})
        self.assertEqual(result.name, "calculator")

    def test_process_invalid_tool_call(self):
        """Test processing an invalid tool call."""
        result = asyncio.run(
            self.handler.process_tool_call(
                "nonexistent_tool",
                {"param": "value"},
            )
        )

        # Verify result
        self.assertEqual(result.role, "tool")
        self.assertIn("error", result.content)
        self.assertEqual(result.name, "nonexistent_tool")

    def test_register_tool_handler(self):
        """Test registering a tool handler."""
        mock_handler = MagicMock()
        self.handler.register_tool_handler("new_tool", mock_handler)

        self.assertIn("new_tool", self.handler.tool_handlers)
        self.assertEqual(self.handler.tool_handlers["new_tool"], mock_handler)

    def test_clear_context(self):
        """Test clearing the context."""
        # Add a message to the context
        self.handler.context.add_message(MCPMessage(role="user", content="Hello"))
        self.assertEqual(len(self.handler.context.messages), 1)

        # Clear the context
        self.handler.clear_context()
        self.assertEqual(len(self.handler.context.messages), 0)

    def test_set_context(self):
        """Test setting the context."""
        new_context = MCPContext()
        new_context.add_message(MCPMessage(role="user", content="Hello"))

        self.handler.set_context(new_context)
        self.assertEqual(len(self.handler.context.messages), 1)
        self.assertEqual(self.handler.context.messages[0].content, "Hello")


if __name__ == "__main__":
    unittest.main()
