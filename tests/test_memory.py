"""
Test memory implementations

This module contains tests for the memory implementations in the muxi framework.
"""

import unittest
import numpy as np

from muxi.core.memory.buffer import BufferMemory
from muxi.core.models.base import BaseModel


class TestBufferMemory(unittest.IsolatedAsyncioTestCase):
    """Test cases for the BufferMemory implementation."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        self.memory = BufferMemory(max_size=3, buffer_multiplier=10)

    async def test_add_content(self):
        """Test adding content to the buffer memory."""
        # Add some content
        await self.memory.add("Hello, world!")
        await self.memory.add("This is a test.")

        # Check that content was added
        results = await self.memory.search("", limit=10)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "This is a test.")
        self.assertEqual(results[1]["content"], "Hello, world!")

    async def test_add_with_metadata(self):
        """Test adding content with metadata."""
        # Add content with metadata
        await self.memory.add("Hello", {"source": "user"})
        await self.memory.add("Hi there", {"source": "assistant"})

        # Check that metadata was stored
        results = await self.memory.search("", limit=10)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["metadata"]["source"], "assistant")
        self.assertEqual(results[1]["metadata"]["source"], "user")

    async def test_max_size(self):
        """Test that buffer respects the maximum size."""
        # Add more content than the max size
        await self.memory.add("First message")
        await self.memory.add("Second message")
        await self.memory.add("Third message")
        await self.memory.add("Fourth message")

        # Check the results
        results = await self.memory.search("", limit=10)

        # With buffer_multiplier=10, total capacity is 30, so all messages are kept
        # The buffer capacity is 3 (max_size) * 10 (buffer_multiplier) = 30
        self.assertEqual(len(results), 4, "Should contain all 4 messages within capacity")
        self.assertEqual(results[0]["content"], "Fourth message", "Most recent message first")
        self.assertEqual(results[1]["content"], "Third message")
        self.assertEqual(results[2]["content"], "Second message")
        self.assertEqual(results[3]["content"], "First message")

    async def test_search_limit(self):
        """Test that search respects the limit parameter."""
        # Add some content
        await self.memory.add("First message")
        await self.memory.add("Second message")
        await self.memory.add("Third message")

        # Check that search respects the limit
        results = await self.memory.search("", limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "Third message")
        self.assertEqual(results[1]["content"], "Second message")


class MockLLM(BaseModel):
    """Mock LLM for testing."""

    async def chat(self, messages, **kwargs):
        """Mock implementation that always returns a fixed response."""
        return "This is a mock response."

    async def embed(self, text):
        """Mock implementation that returns a simple embedding."""
        # Just return a vector of 1s with the requested dimension
        return np.ones(5) / np.sqrt(5)  # Unit vector

    async def generate_embeddings(self, texts):
        """Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embeddings, one for each input text
        """
        # Generate a simple embedding for each text
        return [np.ones(5) / np.sqrt(5) for _ in texts]  # Unit vectors


if __name__ == "__main__":
    unittest.main()
