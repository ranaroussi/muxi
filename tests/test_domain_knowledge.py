"""
Unit tests for the domain knowledge functionality in Memobase.

This module tests the domain knowledge methods added to the Memobase class.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase
from tests.utils.async_test import async_test


class TestDomainKnowledge(unittest.TestCase):
    """Test cases for the domain knowledge functionality in Memobase."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LongTermMemory
        self.mock_long_term_memory = MagicMock(spec=LongTermMemory)

        # Set up mock returns for add
        self.mock_long_term_memory.add.return_value = "test_memory_id"

        # Set up mock returns for search
        self.mock_long_term_memory.search.return_value = [
            (0.8, {
                "id": "test_memory_id_1",
                "text": "name: John Doe",
                "meta_data": {
                    "user_id": 123,
                    "type": "domain_knowledge",
                    "key": "name",
                    "source": "test",
                    "importance": 0.9
                }
            }),
            (0.7, {
                "id": "test_memory_id_2",
                "text": "age: 30",
                "meta_data": {
                    "user_id": 123,
                    "type": "domain_knowledge",
                    "key": "age",
                    "source": "test",
                    "importance": 0.9
                }
            }),
            (0.6, {
                "id": "test_memory_id_3",
                "text": "location: {\"city\": \"New York\", \"country\": \"USA\"}",
                "meta_data": {
                    "user_id": 123,
                    "type": "domain_knowledge",
                    "key": "location",
                    "source": "test",
                    "importance": 0.9
                }
            }),
            (0.5, {
                "id": "test_memory_id_4",
                "text": "interests: [\"programming\", \"AI\", \"music\"]",
                "meta_data": {
                    "user_id": 123,
                    "type": "domain_knowledge",
                    "key": "interests",
                    "source": "test",
                    "importance": 0.9
                }
            }),
        ]

        # Create Memobase with mock LongTermMemory
        self.memobase = Memobase(long_term_memory=self.mock_long_term_memory, default_user_id=0)

    @async_test
    async def test_add_user_domain_knowledge(self):
        """Test adding domain knowledge for a user."""
        # Test data
        user_id = 123
        knowledge = {
            "name": "John Doe",
            "age": 30,
            "location": {"city": "New York", "country": "USA"},
            "interests": ["programming", "AI", "music"]
        }

        # Call the method
        memory_ids = await self.memobase.add_user_domain_knowledge(
            user_id=user_id,
            knowledge=knowledge,
            source="test",
            importance=0.9
        )

        # Verify results
        self.assertEqual(len(memory_ids), 4)
        self.assertEqual(memory_ids[0], "test_memory_id")

        # Verify the mock was called correctly
        self.assertEqual(self.mock_long_term_memory.add.call_count, 4)

        # Verify the collection was created
        collection_name = f"{Memobase.DOMAIN_KNOWLEDGE_COLLECTION}_{user_id}"
        self.mock_long_term_memory._ensure_collection_exists.assert_called_with(
            None, collection_name
        )

    @async_test
    async def test_get_user_domain_knowledge(self):
        """Test retrieving domain knowledge for a user."""
        # Test data
        user_id = 123

        # Call the method
        knowledge = await self.memobase.get_user_domain_knowledge(user_id=user_id)

        # Verify results
        self.assertEqual(len(knowledge), 4)
        self.assertEqual(knowledge["name"], "John Doe")
        self.assertEqual(knowledge["age"], "30")
        self.assertEqual(knowledge["location"], {"city": "New York", "country": "USA"})
        self.assertEqual(knowledge["interests"], ["programming", "AI", "music"])

        # Verify the mock was called correctly
        self.mock_long_term_memory.search.assert_called_once()

    @async_test
    async def test_get_user_domain_knowledge_specific_keys(self):
        """Test retrieving specific domain knowledge keys for a user."""
        # Test data
        user_id = 123
        keys = ["name", "age"]

        # Call the method
        knowledge = await self.memobase.get_user_domain_knowledge(user_id=user_id, keys=keys)

        # Verify results
        self.assertEqual(len(knowledge), 2)
        self.assertEqual(knowledge["name"], "John Doe")
        self.assertEqual(knowledge["age"], "30")

        # Verify the mock was called correctly
        self.assertEqual(self.mock_long_term_memory.search.call_count, 2)

    @async_test
    async def test_import_user_domain_knowledge_from_dict(self):
        """Test importing domain knowledge from a dictionary."""
        # Test data
        user_id = 123
        data = {
            "name": "John Doe",
            "age": 30
        }

        # Call the method
        memory_ids = await self.memobase.import_user_domain_knowledge(
            data_source=data,
            user_id=user_id,
            format="dict",
            source="import_test"
        )

        # Verify results
        self.assertEqual(len(memory_ids), 2)
        self.assertEqual(memory_ids[0], "test_memory_id")

        # Verify the mock was called correctly
        self.assertEqual(self.mock_long_term_memory.add.call_count, 2)

    @async_test
    async def test_import_user_domain_knowledge_from_json_file(self):
        """Test importing domain knowledge from a JSON file."""
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump({"name": "John Doe", "age": 30}, temp_file)
            temp_file_path = temp_file.name

        try:
            # Test data
            user_id = 123

            # Call the method
            memory_ids = await self.memobase.import_user_domain_knowledge(
                data_source=temp_file_path,
                user_id=user_id,
                format="json",
                source="import_test"
            )

            # Verify results
            self.assertEqual(len(memory_ids), 2)
            self.assertEqual(memory_ids[0], "test_memory_id")

            # Verify the mock was called correctly
            self.assertEqual(self.mock_long_term_memory.add.call_count, 2)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    @async_test
    @patch("asyncio.to_thread")
    async def test_clear_user_domain_knowledge(self, mock_to_thread):
        """Test clearing domain knowledge for a user."""
        # Set up mock
        mock_to_thread.return_value = True

        # Test data
        user_id = 123

        # Call the method
        result = await self.memobase.clear_user_domain_knowledge(user_id=user_id)

        # Verify results
        self.assertTrue(result)

        # Verify the mock was called correctly
        self.mock_long_term_memory.delete_collection.assert_called_once()
        self.mock_long_term_memory.create_collection.assert_called_once()

    @async_test
    @patch("asyncio.to_thread")
    async def test_clear_specific_domain_knowledge_keys(self, mock_to_thread):
        """Test clearing specific domain knowledge keys for a user."""
        # Set up mock
        mock_to_thread.return_value = True

        # Test data
        user_id = 123
        keys = ["name", "age"]

        # Call the method
        result = await self.memobase.clear_user_domain_knowledge(user_id=user_id, keys=keys)

        # Verify results
        self.assertTrue(result)

        # Verify the mock was called correctly
        self.assertEqual(self.mock_long_term_memory.search.call_count, 2)
        self.assertEqual(mock_to_thread.call_count, 2)


if __name__ == "__main__":
    unittest.main()
