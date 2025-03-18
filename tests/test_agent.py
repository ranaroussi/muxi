"""
Test Agent class

This module contains tests for the Agent class in the muxi framework.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from muxi.core.agent import Agent
from muxi.core.mcp import MCPMessage


class TestAgent(unittest.TestCase):
    """Test cases for the Agent class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects for dependencies
        self.mock_model = MagicMock()
        self.mock_memory = MagicMock()

        # Set up mock returns
        self.mock_model.chat = AsyncMock()
        self.mock_model.chat.return_value = {
            "role": "assistant",
            "content": "I'm a helpful assistant.",
        }

        self.mock_memory.search.return_value = [
            {"content": "Previous conversation content", "metadata": {"timestamp": 1234567890}}
        ]

        # Create agent with mock dependencies
        self.agent = Agent(
            name="test_agent", model=self.mock_model, memory=self.mock_memory
        )

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "test_agent")
        self.assertEqual(self.agent.model, self.mock_model)
        self.assertEqual(self.agent.memory, self.mock_memory)

    def test_process_message(self):
        """Test processing a message."""
        # Process a message asynchronously
        result = asyncio.run(self.agent.process_message("Hello, agent!"))

        # Verify message was stored in memory
        self.mock_memory.add.assert_called_with(
            "Hello, agent!", {"role": "user", "timestamp": unittest.mock.ANY}
        )

        # Verify LLM was called
        self.assertTrue(self.mock_model.chat.called)

        # Verify result
        self.assertEqual(result.content, "I'm a helpful assistant.")

    @patch("muxi.core.agent.MCPHandler")
    def test_process_mcp_server_calls(self, mock_handler_class):
        """Test processing MCP server calls."""
        # Set up mock for MCPHandler
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        # Force replacement of the agent's MCPHandler with our mock
        self.agent.mcp_handler = mock_handler

        # Set up mock to return a message with tool calls
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {"name": "calculator", "arguments": '{"expression": "2+2"}'},
            }
        ]

        self.mock_model.chat.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": tool_calls,
        }

        # Set up mock to return final response
        response = MCPMessage(role="assistant", content="The result is 4.")
        mock_future = AsyncMock()
        mock_future.return_value = response
        mock_handler.process_message = mock_future

        # Process a message asynchronously
        result = asyncio.run(self.agent.process_message("Calculate 2+2"))

        # Verify handler was called
        self.assertTrue(mock_handler.process_message.called)

        # Verify result
        self.assertEqual(result, response)

    def test_get_memory(self):
        """Test retrieving memory."""
        # Get memory
        result = self.agent.get_memory("test query", 10)

        # Verify memory.search was called
        self.mock_memory.search.assert_called_with("test query", 10)

        # Verify result
        self.assertEqual(result, self.mock_memory.search.return_value)

    @patch("muxi.core.agent.datetime")
    def test_create_message_context(self, mock_datetime):
        """Test creating message context."""
        # Set up datetime mock
        mock_datetime.now.return_value.timestamp.return_value = 1234567890

        # Create context
        context = self.agent._create_message_context("Hello")

        # Verify context
        self.assertEqual(context, {"role": "user", "timestamp": 1234567890})

    # Convert this to a regular test that calls asyncio.run
    def test_connect_mcp_server(self):
        """Test connecting to an MCP server."""
        # Mock the _handle_mcp_server_call method
        self.agent._handle_mcp_server_call = AsyncMock()

        # Run the connect_mcp_server method with asyncio.run
        asyncio.run(self.agent.connect_mcp_server(
            name="calculator",
            url="http://localhost:5001",
            credentials={"api_key": "test_key"}
        ))

        # Verify MCP server was registered
        self.assertIn("calculator", self.agent.mcp_servers)
        server_info = self.agent.mcp_servers["calculator"]
        self.assertEqual(server_info["url"], "http://localhost:5001")
        self.assertEqual(server_info["credentials"], {"api_key": "test_key"})


if __name__ == "__main__":
    unittest.main()
