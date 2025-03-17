"""
Test memory implementations

This module contains tests for the memory implementations in the muxi framework.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import faiss
import numpy as np

from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.vector import VectorMemory
from muxi.models.base import BaseModel


class TestBufferMemory(unittest.TestCase):
    """Test cases for the BufferMemory implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory = BufferMemory(max_size=3)

    def test_add_content(self):
        """Test adding content to the buffer memory."""
        # Add some content
        self.memory.add("Hello, world!")
        self.memory.add("This is a test.")

        # Check that content was added
        results = self.memory.search("", 10)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "This is a test.")
        self.assertEqual(results[1]["content"], "Hello, world!")

    def test_add_with_metadata(self):
        """Test adding content with metadata."""
        # Add content with metadata
        self.memory.add("Hello", {"source": "user"})
        self.memory.add("Hi there", {"source": "assistant"})

        # Check that metadata was stored
        results = self.memory.search("", 10)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["metadata"]["source"], "assistant")
        self.assertEqual(results[1]["metadata"]["source"], "user")

    def test_max_size(self):
        """Test that buffer respects the maximum size."""
        # Add more content than the max size
        self.memory.add("First message")
        self.memory.add("Second message")
        self.memory.add("Third message")
        self.memory.add("Fourth message")

        # Check that only the most recent messages are kept
        results = self.memory.search("", 10)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["content"], "Fourth message")
        self.assertEqual(results[1]["content"], "Third message")
        self.assertEqual(results[2]["content"], "Second message")

        # First message should be dropped
        for result in results:
            self.assertNotEqual(result["content"], "First message")

    def test_search_limit(self):
        """Test that search respects the limit parameter."""
        # Add some content
        self.memory.add("First message")
        self.memory.add("Second message")
        self.memory.add("Third message")

        # Check that search respects the limit
        results = self.memory.search("", 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "Third message")
        self.assertEqual(results[1]["content"], "Second message")


class MockLLM(BaseModel):
    """Mock LLM for testing vector memory."""

    def chat(self, messages, **kwargs):
        """Mock implementation of chat method."""
        return "This is a mock response."

    def embed(self, text):
        """Mock implementation that returns a simple embedding."""
        # Just return a vector of 1s with the requested dimension
        return np.ones(5) / np.sqrt(5)  # Unit vector


class TestVectorMemory(unittest.TestCase):
    """Test cases for the VectorMemory implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "index")

        # Mock LLM for generating embeddings
        self.mock_model = MockLLM()

        # Create vector memory
        self.memory = VectorMemory(
            model=self.mock_model, vector_dimension=5, index_path=self.index_path
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_add_content(self):
        """Test adding content to vector memory."""
        # Add some content
        self.memory.add("First message")
        self.memory.add("Second message")

        # Verify items were added (memory.documents should have 2 items)
        self.assertEqual(len(self.memory.documents), 2)

        # Verify the index has the correct number of vectors
        self.assertEqual(self.memory.index.ntotal, 2)

    def test_add_with_metadata(self):
        """Test adding content with metadata."""
        # Add content with metadata
        self.memory.add("Hello", {"source": "user"})

        # Check that metadata was stored
        self.assertEqual(self.memory.documents[0]["metadata"]["source"], "user")

    def test_search(self):
        """Test searching in vector memory."""
        # Add some content
        self.memory.add("Apple is a fruit")
        self.memory.add("Banana is yellow")
        self.memory.add("Computers are electronic devices")

        # Search for content
        # Since our mock LLM returns the same embedding for all text,
        # all results should have the same score
        results = self.memory.search("fruit", 2)

        # Should return 2 results
        self.assertEqual(len(results), 2)

        # Scores should be close to 1.0 (cosine similarity of identical unit vectors)
        self.assertAlmostEqual(results[0]["score"], 1.0, places=5)
        self.assertAlmostEqual(results[1]["score"], 1.0, places=5)

    @patch("faiss.write_index")
    @patch("faiss.read_index")
    def test_save_load_index(self, mock_read_index, mock_write_index):
        """Test saving and loading the index."""
        # Create a mock index
        mock_index = MagicMock(spec=faiss.IndexFlatIP)
        mock_index.ntotal = 2

        # Set up read_index to return our mock index
        mock_read_index.return_value = mock_index

        # Test loading an existing index
        memory = VectorMemory(model=self.mock_model, vector_dimension=5, index_path=self.index_path)

        # Verify the read_index was called
        mock_read_index.assert_called_once_with(self.index_path)

        # Add some content to trigger a save
        memory.add("Test message")

        # Verify write_index was called
        mock_write_index.assert_called_once()

    def test_clear(self):
        """Test clearing the memory."""
        # Add some content
        self.memory.add("First message")
        self.memory.add("Second message")

        # Clear the memory
        self.memory.clear()

        # Verify memory is empty
        self.assertEqual(len(self.memory.documents), 0)
        self.assertEqual(self.memory.index.ntotal, 0)


if __name__ == "__main__":
    unittest.main()
