"""
Unit tests for the agent module.

This module contains tests for the Agent class in the agent framework.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.core.agent import Agent
from src.core.mcp import MCPMessage


class TestAgent(unittest.TestCase):
    """Test cases for the Agent class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects for dependencies
        self.mock_llm = MagicMock()
        self.mock_memory = MagicMock()
        self.mock_tools = {
            "calculator": MagicMock(),
            "web_search": MagicMock()
        }

        # Set up mock returns
        self.mock_llm.chat.return_value = {
            "role": "assistant",
            "content": "I'm a helpful assistant."
        }

        self.mock_memory.search.return_value = [
            {
                "content": "Previous conversation content",
                "metadata": {"timestamp": 1234567890}
            }
        ]

        # Create agent with mock dependencies
        self.agent = Agent(
            name="test_agent",
            llm=self.mock_llm,
            memory=self.mock_memory,
            tools=self.mock_tools
        )

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "test_agent")
        self.assertEqual(self.agent.llm, self.mock_llm)
        self.assertEqual(self.agent.memory, self.mock_memory)
        self.assertEqual(self.agent.tools, self.mock_tools)

    def test_process_message(self):
        """Test processing a message."""
        # Process a message
        result = self.agent.process_message("Hello, agent!")

        # Verify message was stored in memory
        self.mock_memory.add.assert_called_with(
            "Hello, agent!",
            {"role": "user", "timestamp": unittest.mock.ANY}
        )

        # Verify LLM was called
        self.assertTrue(self.mock_llm.chat.called)

        # Verify result
        self.assertEqual(result.content, "I'm a helpful assistant.")

    @patch('src.core.agent.MCPHandler')
    def test_process_tool_calls(self, mock_handler_class):
        """Test processing tool calls."""
        # Set up mock for MCPHandler
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        # Set up mock to return a message with tool calls
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "calculator",
                    "arguments": '{"expression": "2+2"}'
                }
            }
        ]

        self.mock_llm.chat.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": tool_calls
        }

        # Set up mock to return final response
        mock_handler.process_message.return_value = MCPMessage(
            role="assistant",
            content="The result is 4."
        )

        # Process a message
        result = self.agent.process_message("Calculate 2+2")

        # Verify handler was created and called
        mock_handler_class.assert_called_with(self.mock_llm, self.mock_tools)
        mock_handler.process_message.assert_called_once()

        # Verify result
        self.assertEqual(result.content, "The result is 4.")

    def test_get_memory(self):
        """Test retrieving memory."""
        # Get memory
        result = self.agent.get_memory("test query", 10)

        # Verify memory.search was called
        self.mock_memory.search.assert_called_with("test query", 10)

        # Verify result
        self.assertEqual(result, self.mock_memory.search.return_value)

    @patch('src.core.agent.datetime')
    def test_create_message_context(self, mock_datetime):
        """Test creating message context."""
        # Set up datetime mock
        mock_datetime.now.return_value.timestamp.return_value = 1234567890

        # Create context
        context = self.agent._create_message_context("Hello")

        # Verify context
        self.assertEqual(context, {"role": "user", "timestamp": 1234567890})


if __name__ == "__main__":
    unittest.main()
