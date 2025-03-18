"""
Test Agent Knowledge

This module contains tests for the knowledge functionality of the Agent class.
"""

import asyncio
import os
import unittest
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from muxi.core.agent import Agent
from muxi.knowledge.base import FileKnowledge


class TestAgentKnowledge(unittest.TestCase):
    """Test cases for Agent knowledge functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects for dependencies
        self.mock_model = MagicMock()
        self.mock_memory = MagicMock()

        # Mock embedding functions
        self.mock_model.embed = AsyncMock()
        self.mock_model.embed.return_value = [0.1] * 1536  # Mock embedding of dimension 1536

        self.mock_model.generate_embeddings = AsyncMock()
        self.mock_model.generate_embeddings.return_value = [[0.1] * 1536 for _ in range(3)]  # 3 mock embeddings

        # Create agent with mock dependencies
        self.agent = Agent(
            model=self.mock_model,
            memory=self.mock_memory
        )

        # Create temporary files for testing
        self.test_file_content = (
            "This is a test file for knowledge testing.\n"
            "It contains information about testing knowledge functionality.\n"
            "MUXI Framework allows agents to use knowledge sources."
        )

    @patch('muxi.knowledge.base.KnowledgeHandler')
    async def test_initialize_knowledge(self, mock_knowledge_handler_class):
        """Test initializing knowledge in agent."""
        # Setup mock
        mock_handler = MagicMock()
        mock_knowledge_handler_class.return_value = mock_handler

        # Create test knowledge source
        test_source = FileKnowledge(path="/path/to/test.txt", description="Test file")

        # Initialize knowledge
        await self.agent._initialize_knowledge([test_source])

        # Verify model was used to get embedding dimension
        self.mock_model.embed.assert_called_once()

        # Verify knowledge handler was created with correct parameters
        mock_knowledge_handler_class.assert_called_once()
        self.assertEqual(self.agent.knowledge_handler, mock_handler)

        # Verify knowledge source was added
        mock_handler.add_file.assert_called_once()

    @patch('muxi.knowledge.base.os.path.exists')
    @patch('muxi.knowledge.base.os.path.getmtime')
    @patch('builtins.open', new_callable=mock_open, read_data="Test content")
    async def test_add_knowledge(self, mock_file, mock_getmtime, mock_exists):
        """Test adding a knowledge source."""
        # Setup mocks
        mock_exists.return_value = True
        mock_getmtime.return_value = 12345

        # Create a mock knowledge handler
        self.agent.knowledge_handler = MagicMock()
        self.agent.knowledge_handler.add_file = AsyncMock(return_value=3)  # 3 chunks added

        # Create test knowledge source
        test_source = FileKnowledge(path="/path/to/test.txt", description="Test file")

        # Add knowledge
        chunks_added = await self.agent.add_knowledge(test_source)

        # Verify knowledge was added
        self.agent.knowledge_handler.add_file.assert_called_once_with(
            test_source, self.mock_model.generate_embeddings
        )
        self.assertEqual(chunks_added, 3)

    async def test_add_knowledge_initializes_handler(self):
        """Test adding knowledge initializes handler if not already created."""
        # Ensure no handler exists initially
        self.agent.knowledge_handler = None

        # Create test knowledge source
        test_source = FileKnowledge(path="/path/to/test.txt", description="Test file")

        # Patch KnowledgeHandler class
        with patch('muxi.knowledge.base.KnowledgeHandler') as mock_handler_class:
            # Setup mock handler
            mock_handler = MagicMock()
            mock_handler.add_file = AsyncMock(return_value=0)
            mock_handler_class.return_value = mock_handler

            # Add knowledge
            await self.agent.add_knowledge(test_source)

            # Verify handler was created
            mock_handler_class.assert_called_once_with(self.agent.agent_id)
            self.assertEqual(self.agent.knowledge_handler, mock_handler)

    async def test_remove_knowledge(self):
        """Test removing a knowledge source."""
        # Create a mock knowledge handler
        self.agent.knowledge_handler = MagicMock()
        self.agent.knowledge_handler.remove_file = AsyncMock(return_value=True)

        # Remove knowledge
        result = await self.agent.remove_knowledge("/path/to/test.txt")

        # Verify knowledge was removed
        self.agent.knowledge_handler.remove_file.assert_called_once_with("/path/to/test.txt")
        self.assertTrue(result)

    async def test_remove_knowledge_without_handler(self):
        """Test removing knowledge when no handler exists."""
        # Ensure no handler exists
        self.agent.knowledge_handler = None

        # Remove knowledge should return False
        result = await self.agent.remove_knowledge("/path/to/test.txt")
        self.assertFalse(result)

    def test_get_knowledge_sources(self):
        """Test getting knowledge sources."""
        # Create a mock knowledge handler
        self.agent.knowledge_handler = MagicMock()
        self.agent.knowledge_handler.get_sources.return_value = ["/path/to/test1.txt", "/path/to/test2.txt"]

        # Get sources
        sources = self.agent.get_knowledge_sources()

        # Verify sources were retrieved
        self.agent.knowledge_handler.get_sources.assert_called_once()
        self.assertEqual(sources, ["/path/to/test1.txt", "/path/to/test2.txt"])

    def test_get_knowledge_sources_without_handler(self):
        """Test getting knowledge sources when no handler exists."""
        # Ensure no handler exists
        self.agent.knowledge_handler = None

        # Get sources should return empty list
        sources = self.agent.get_knowledge_sources()
        self.assertEqual(sources, [])

    async def test_search_knowledge(self):
        """Test searching knowledge."""
        # Create mock search results
        mock_results = [
            {"content": "Result 1", "source": "/path/to/test.txt", "relevance": 0.85},
            {"content": "Result 2", "source": "/path/to/test.txt", "relevance": 0.75}
        ]

        # Create a mock knowledge handler
        self.agent.knowledge_handler = MagicMock()
        self.agent.knowledge_handler.search = AsyncMock(return_value=mock_results)

        # Search knowledge
        results = await self.agent.search_knowledge("test query", 2, 0.7)

        # Verify search was performed
        self.agent.knowledge_handler.search.assert_called_once_with(
            "test query", self.mock_model.generate_embeddings, 2, 0.7
        )
        self.assertEqual(results, mock_results)

    async def test_search_knowledge_without_handler(self):
        """Test searching knowledge when no handler exists."""
        # Ensure no handler exists
        self.agent.knowledge_handler = None

        # Search should return empty list
        results = await self.agent.search_knowledge("test query")
        self.assertEqual(results, [])

    @patch('muxi.knowledge.base.KnowledgeHandler')
    @patch('muxi.core.agent.FileKnowledge')
    async def test_integration_with_real_file(self, mock_file_knowledge, mock_knowledge_handler):
        """Test integration with a real file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(self.test_file_content)

        try:
            # Setup mock file knowledge to use the real file
            mock_file_instance = MagicMock()
            mock_file_instance.path = temp_file.name
            mock_file_knowledge.return_value = mock_file_instance

            # Setup mock knowledge handler
            mock_handler = MagicMock()
            mock_handler.add_file = AsyncMock(return_value=3)
            mock_handler.search = AsyncMock(return_value=[
                {"content": "MUXI Framework allows agents to use knowledge sources.",
                 "source": temp_file.name,
                 "relevance": 0.9}
            ])
            mock_knowledge_handler.return_value = mock_handler

            # Initialize the agent with knowledge
            self.agent.knowledge_handler = mock_handler

            # Search for relevant information
            results = await self.agent.search_knowledge("MUXI knowledge")

            # Verify search was performed
            mock_handler.search.assert_called_once()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["source"], temp_file.name)
            self.assertIn("MUXI Framework", results[0]["content"])

        finally:
            # Clean up temporary file
            os.unlink(temp_file.name)


if __name__ == "__main__":
    # Use asyncio to run async tests
    async def run_tests():
        test_loader = unittest.TestLoader()
        test_suite = test_loader.loadTestsFromTestCase(TestAgentKnowledge)
        test_runner = unittest.TextTestRunner()
        test_runner.run(test_suite)

    asyncio.run(run_tests())
