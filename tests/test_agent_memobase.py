"""
Unit tests for the Agent class with Memobase integration.

This module contains tests for the Agent class with multi-user memory support
via Memobase in the AI Agent Framework.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from src.core.agent import Agent
from src.memory.memobase import Memobase
from src.core.mcp import MCPMessage
from tests.utils.async_test import async_test


class TestAgentWithMemobase(unittest.TestCase):
    """Test cases for the Agent class with Memobase integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects for dependencies
        self.mock_llm = MagicMock()
        self.mock_buffer_memory = MagicMock()
        self.mock_memobase = MagicMock(spec=Memobase)
        self.mock_tools = {
            "calculator": MagicMock(),
            "web_search": MagicMock()
        }

        # Set up mock returns
        self.mock_llm.chat = AsyncMock()
        self.mock_llm.chat.return_value = {
            "role": "assistant",
            "content": "I'm a helpful multi-user assistant."
        }

        self.mock_buffer_memory.search.return_value = [
            {
                "content": "Previous conversation content",
                "metadata": {"timestamp": 1234567890}
            }
        ]

        self.mock_memobase.add = AsyncMock()
        self.mock_memobase.add.return_value = 123  # Return a mock memory ID

        self.mock_memobase.search = AsyncMock()
        self.mock_memobase.search.return_value = [
            {
                "content": "User-specific previous content",
                "metadata": {"user_id": 123, "timestamp": 1234567890},
                "distance": 0.8,
                "source": "memobase",
                "id": 456
            }
        ]

        # Create agent with mock dependencies
        self.agent = Agent(
            name="test_agent",
            llm=self.mock_llm,
            buffer_memory=self.mock_buffer_memory,
            memobase=self.mock_memobase,
            tools=self.mock_tools
        )

    @async_test
    async def test_process_message_with_user_id(self):
        """Test processing a message with user ID."""
        # Process a message with user_id
        result = await self.agent.process_message(
            "Hello, agent!",
            user_id=123
        )

        # Verify message was stored in buffer memory
        self.mock_buffer_memory.add.assert_called_with(
            "Hello, agent!",
            {"role": "user", "timestamp": unittest.mock.ANY}
        )

        # Verify message was stored in memobase with user_id
        self.mock_memobase.add.assert_any_call(
            content="Hello, agent!",
            metadata={"role": "user", "timestamp": unittest.mock.ANY},
            user_id=123
        )

        # Verify LLM was called
        self.assertTrue(self.mock_llm.chat.called)

        # Verify result
        self.assertEqual(result.content, "I'm a helpful assistant.")

        # Verify response was stored in memobase with user_id
        self.mock_memobase.add.assert_any_call(
            content="I'm a helpful assistant.",
            metadata={"role": "assistant", "timestamp": unittest.mock.ANY},
            user_id=123
        )

    @async_test
    async def test_process_message_without_user_id(self):
        """Test processing a message without user ID."""
        # Process a message without user_id
        result = await self.agent.process_message("Hello, agent!")

        # Verify message was stored in buffer memory
        self.mock_buffer_memory.add.assert_called_with(
            "Hello, agent!",
            {"role": "user", "timestamp": unittest.mock.ANY}
        )

        # Verify memobase was NOT used (since user_id is None)
        self.mock_memobase.add.assert_not_called()

        # Verify LLM was called
        self.assertTrue(self.mock_llm.chat.called)

        # Verify result
        self.assertEqual(result.content, "I'm a helpful assistant.")

    @async_test
    @patch('src.core.agent.MCPHandler')
    async def test_process_tool_calls_with_user_id(self, mock_handler_class):
        """Test processing tool calls with user ID."""
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

        # Process a message with user_id
        result = await self.agent.process_message(
            "Calculate 2+2",
            user_id=123
        )

        # Verify handler was created and called
        mock_handler_class.assert_called_with(self.mock_llm, self.mock_tools)
        mock_handler.process_message.assert_called_once()

        # Verify result
        self.assertEqual(result.content, "The result is 4.")

        # Verify response was stored in memobase with user_id
        self.mock_memobase.add.assert_any_call(
            content="The result is 4.",
            metadata={"role": "assistant", "timestamp": unittest.mock.ANY},
            user_id=123
        )

    @async_test
    async def test_search_memory_with_user_id(self):
        """Test searching memory with user ID."""
        # Search memory with user_id
        results = await self.agent.search_memory(
            query="test query",
            k=5,
            user_id=123
        )

        # Verify memobase.search was called with user_id
        self.mock_memobase.search.assert_called_with(
            query="test query",
            limit=5,
            user_id=123
        )

        # Verify result comes from memobase
        self.assertEqual(results[0]["source"], "memobase")
        self.assertEqual(results[0]["content"], "User-specific previous content")
        self.assertEqual(results[0]["metadata"]["user_id"], 123)

    @async_test
    async def test_search_memory_without_user_id(self):
        """Test searching memory without user ID."""
        # Set up mock for LLM embed
        self.mock_llm.embed = AsyncMock()
        self.mock_llm.embed.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Set up mock for buffer memory search
        self.mock_buffer_memory.search.return_value = [
            (0.9, {"input": "Hello", "response": "Hi there", "type": "conversation"})
        ]

        # Search memory without user_id
        results = await self.agent.search_memory(
            query="test query",
            k=5
        )

        # Verify memobase.search was NOT called
        self.mock_memobase.search.assert_not_called()

        # Verify buffer_memory.search was called
        self.mock_buffer_memory.search.assert_called()

        # Verify result comes from buffer
        self.assertEqual(results[0]["source"], "buffer")

    def test_clear_memory_with_user_id(self):
        """Test clearing memory with user ID."""
        # Clear memory with user_id
        self.agent.clear_memory(user_id=123)

        # Verify memobase.clear_user_memory was called with user_id
        self.mock_memobase.clear_user_memory.assert_called_with(123)

        # Verify buffer_memory.clear was NOT called
        self.mock_buffer_memory.clear.assert_not_called()

    def test_clear_memory_without_user_id(self):
        """Test clearing memory without user ID."""
        # Clear memory without user_id
        self.agent.clear_memory()

        # Verify buffer_memory.clear was called
        self.mock_buffer_memory.clear.assert_called_once()

        # Verify memobase.clear_user_memory was NOT called
        self.mock_memobase.clear_user_memory.assert_not_called()

    @async_test
    async def test_chat_with_user_id(self):
        """Test chat with user ID."""
        # Set up mock for process_message
        self.agent.process_message = AsyncMock()
        self.agent.process_message.return_value = MCPMessage(
            role="assistant",
            content="I remember you from before!"
        )

        # Chat with user_id
        response = await self.agent.chat("Hello again", user_id=123)

        # Verify process_message was called with user_id
        self.agent.process_message.assert_called_once_with("Hello again", user_id=123)

        # Verify response
        self.assertEqual(response, "I remember you from before!")

    @async_test
    async def test_chat_without_user_id(self):
        """Test chat without user ID."""
        # Set up mock for process_message
        self.agent.process_message = AsyncMock()
        self.agent.process_message.return_value = MCPMessage(
            role="assistant",
            content="Nice to meet you!"
        )

        # Chat without user_id
        response = await self.agent.chat("Hello")

        # Verify process_message was called without user_id
        self.agent.process_message.assert_called_once_with("Hello", user_id=None)

        # Verify response
        self.assertEqual(response, "Nice to meet you!")


if __name__ == "__main__":
    unittest.main()
