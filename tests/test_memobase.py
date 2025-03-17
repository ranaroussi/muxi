"""
Unit tests for the Memobase module.

This module contains tests for the Memobase class in the MUXI Framework.
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from muxi.server.memory.long_term import LongTermMemory
from muxi.server.memory.memobase import Memobase
from tests.utils.async_test import async_test


class TestMemobase(unittest.TestCase):
    """Test cases for the Memobase class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LongTermMemory
        self.mock_long_term_memory = MagicMock(spec=LongTermMemory)

        # Set up mock returns
        self.mock_long_term_memory.add.return_value = 123  # Return a mock memory ID
        self.mock_long_term_memory.search.return_value = [
            (0.8, {"id": 1, "text": "Test memory", "meta_data": {"user_id": 123}}),
            (0.7, {"id": 2, "text": "Another test", "meta_data": {"user_id": 123}}),
        ]
        self.mock_long_term_memory.get_recent_memories.return_value = [
            {
                "id": 1,
                "text": "Test memory",
                "meta_data": {"user_id": 123},
                "created_at": time.time(),
            },
            {
                "id": 2,
                "text": "Another test",
                "meta_data": {"user_id": 123},
                "created_at": time.time(),
            },
        ]

        # Create Memobase with mock LongTermMemory
        self.memobase = Memobase(long_term_memory=self.mock_long_term_memory, default_user_id=0)

    @async_test
    @patch("asyncio.to_thread")
    async def test_add(self, mock_to_thread):
        """Test adding content to Memobase."""
        # Set up mock for asyncio.to_thread
        mock_to_thread.return_value = 123  # Return a mock memory ID

        # Add content
        memory_id = await self.memobase.add(
            content="Test content", metadata={"type": "test"}, user_id=123
        )

        # Verify asyncio.to_thread was called with the right arguments
        mock_to_thread.assert_called_once()
        args, kwargs = mock_to_thread.call_args
        self.assertEqual(args[0], self.mock_long_term_memory.add)

        # Verify the collection name is correct
        self.assertEqual(kwargs.get("collection"), "user_123")

        # Verify the metadata has user_id
        self.assertEqual(kwargs.get("metadata").get("user_id"), 123)
        self.assertEqual(kwargs.get("metadata").get("type"), "test")

        # Verify the content is correct
        self.assertEqual(kwargs.get("text"), "Test content")

        # Verify the returned memory ID
        self.assertEqual(memory_id, 123)

    @async_test
    @patch("asyncio.to_thread")
    async def test_add_default_user(self, mock_to_thread):
        """Test adding content with default user ID."""
        # Set up mock for asyncio.to_thread
        mock_to_thread.return_value = 123  # Return a mock memory ID

        # Add content without specifying user_id
        await self.memobase.add(content="Test content", metadata={"type": "test"})

        # Verify the collection name is correct
        args, kwargs = mock_to_thread.call_args
        self.assertEqual(kwargs.get("collection"), "user_0")

        # Verify the metadata has default user_id
        self.assertEqual(kwargs.get("metadata").get("user_id"), 0)

    @async_test
    @patch("asyncio.to_thread")
    async def test_search(self, mock_to_thread):
        """Test searching in Memobase."""
        # Set up mock for asyncio.to_thread
        mock_to_thread.return_value = [
            (0.8, {"id": 1, "text": "Test memory", "meta_data": {"user_id": 123}}),
            (0.7, {"id": 2, "text": "Another test", "meta_data": {"user_id": 123}}),
        ]

        # Search for content
        results = await self.memobase.search(query="test", limit=5, user_id=123)

        # Verify asyncio.to_thread was called with the right arguments
        mock_to_thread.assert_called_once()
        args, kwargs = mock_to_thread.call_args
        self.assertEqual(args[0], self.mock_long_term_memory.search)

        # Verify the collection name is correct
        self.assertEqual(kwargs.get("collection"), "user_123")

        # Verify the filter includes user_id
        self.assertEqual(kwargs.get("filter_metadata").get("user_id"), 123)

        # Verify the query and limit are correct
        self.assertEqual(kwargs.get("query"), "test")
        self.assertEqual(kwargs.get("k"), 5)

        # Verify the results format
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "Test memory")
        self.assertEqual(results[0]["source"], "memobase")
        self.assertEqual(results[0]["distance"], 0.8)
        self.assertEqual(results[0]["metadata"]["user_id"], 123)

    @async_test
    @patch("asyncio.to_thread")
    async def test_search_with_additional_filter(self, mock_to_thread):
        """Test searching with additional filter."""
        # Set up mock for asyncio.to_thread
        mock_to_thread.return_value = [
            (
                0.8,
                {
                    "id": 1,
                    "text": "Test memory",
                    "meta_data": {"user_id": 123, "type": "note"},
                },
            )
        ]

        # Search with additional filter
        await self.memobase.search(query="test", user_id=123, additional_filter={"type": "note"})

        # Verify the filter includes both user_id and additional filter
        args, kwargs = mock_to_thread.call_args
        self.assertEqual(kwargs.get("filter_metadata").get("user_id"), 123)
        self.assertEqual(kwargs.get("filter_metadata").get("type"), "note")

    def test_clear_user_memory(self):
        """Test clearing a user's memory."""
        # Clear memory
        self.memobase.clear_user_memory(user_id=123)

        # Verify delete_collection was called
        self.mock_long_term_memory.delete_collection.assert_called_with("user_123")

        # Verify create_collection was called
        self.mock_long_term_memory.create_collection.assert_called_with(
            "user_123", "Memory collection for user 123"
        )

    def test_clear_default_user_memory(self):
        """Test clearing default user's memory."""
        # Clear memory without specifying user_id
        self.memobase.clear_user_memory()

        # Verify operations used default user_id
        self.mock_long_term_memory.delete_collection.assert_called_with("user_0")
        self.mock_long_term_memory.create_collection.assert_called_with(
            "user_0", "Memory collection for user 0"
        )

    def test_get_user_memories(self):
        """Test getting all memories for a user."""
        # Get memories
        memories = self.memobase.get_user_memories(user_id=123, limit=10, sort_by="created_at")

        # Verify get_recent_memories was called with the right arguments
        self.mock_long_term_memory.get_recent_memories.assert_called_with(
            collection="user_123", limit=10
        )

        # Verify the results format
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0]["content"], "Test memory")
        self.assertEqual(memories[0]["metadata"]["user_id"], 123)


if __name__ == "__main__":
    unittest.main()
