"""
Test KnowledgeHandler

This module contains tests for the KnowledgeHandler class.
"""

import os
import pickle
import tempfile
import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import faiss
import numpy as np

from muxi.knowledge.base import KnowledgeHandler, FileKnowledge


class TestKnowledgeHandler(unittest.TestCase):
    """Test cases for KnowledgeHandler."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a unique agent ID for testing
        self.agent_id = "test_agent_123"

        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Initialize knowledge handler with temporary directory
        self.knowledge_handler = KnowledgeHandler(
            agent_id=self.agent_id,
            embedding_dimension=1536,
            cache_dir=self.temp_dir
        )

        # Test file content
        self.test_file_content = (
            "This is a test file for knowledge testing.\n"
            "It contains information about testing knowledge functionality.\n"
            "MUXI Framework allows agents to use knowledge sources."
        )

        # Generate mock embeddings function
        self.generate_embeddings = AsyncMock()
        self.generate_embeddings.return_value = [
            [0.1] * 1536,
            [0.2] * 1536,
            [0.3] * 1536
        ]

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.unlink(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test knowledge handler initialization."""
        # Verify paths are set correctly
        self.assertEqual(self.knowledge_handler.agent_id, self.agent_id)
        self.assertEqual(self.knowledge_handler.cache_dir, self.temp_dir)
        self.assertEqual(
            self.knowledge_handler.embedding_file,
            f"{self.temp_dir}/{self.agent_id}_embeddings.pickle"
        )
        self.assertEqual(
            self.knowledge_handler.metadata_file,
            f"{self.temp_dir}/{self.agent_id}_metadata.pickle"
        )

        # Verify index initialized with correct dimension
        self.assertIsNotNone(self.knowledge_handler.index)
        self.assertEqual(self.knowledge_handler.index.d, 1536)

        # Verify documents list initialized
        self.assertEqual(self.knowledge_handler.documents, [])

    @patch('os.path.exists')
    def test_load_cached_embeddings_success(self, mock_exists):
        """Test loading cached embeddings successfully."""
        # Mock file existence
        mock_exists.return_value = True

        # Create mock index and documents
        mock_index = faiss.IndexFlatL2(1536)
        mock_index.add(np.array([[0.1] * 1536, [0.2] * 1536]).astype('float32'))
        mock_documents = [
            {"content": "Doc 1", "source": "test.txt", "index": 0},
            {"content": "Doc 2", "source": "test.txt", "index": 1}
        ]

        # Mock pickle.load to return test data
        with patch('builtins.open', mock_open()):
            with patch('pickle.load') as mock_pickle_load:
                mock_pickle_load.side_effect = [mock_index, mock_documents]

                # Create new handler to trigger loading
                handler = KnowledgeHandler(
                    agent_id=self.agent_id,
                    embedding_dimension=1536,
                    cache_dir=self.temp_dir
                )

                # Verify data loaded correctly
                self.assertEqual(handler.documents, mock_documents)
                self.assertEqual(handler.index.ntotal, 2)

    @patch('os.path.exists')
    def test_load_cached_embeddings_failure(self, mock_exists):
        """Test handling failure when loading cached embeddings."""
        # Mock file existence but cause an exception during loading
        mock_exists.return_value = True

        # Mock pickle.load to raise exception
        with patch('builtins.open', mock_open()):
            with patch('pickle.load') as mock_pickle_load:
                mock_pickle_load.side_effect = Exception("Error loading file")

                # Create new handler to trigger loading
                handler = KnowledgeHandler(
                    agent_id=self.agent_id,
                    embedding_dimension=1536,
                    cache_dir=self.temp_dir
                )

                # Verify new index was created
                self.assertEqual(handler.documents, [])
                self.assertEqual(handler.index.ntotal, 0)
                self.assertEqual(handler.index.d, 1536)

    def test_save_embeddings(self):
        """Test saving embeddings to disk."""
        # Setup mock data
        self.knowledge_handler.index = faiss.IndexFlatL2(1536)
        self.knowledge_handler.documents = [
            {"content": "Doc 1", "source": "test.txt", "index": 0}
        ]

        # Mock open and pickle.dump
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('pickle.dump') as mock_pickle_dump:
                # Save embeddings
                self.knowledge_handler._save_embeddings()

                # Verify files were opened
                self.assertEqual(mock_file.call_count, 2)

                # Verify pickle.dump was called
                self.assertEqual(mock_pickle_dump.call_count, 2)

    @patch('muxi.core.utils.load_document')
    @patch('muxi.core.utils.chunk_text')
    @patch('os.path.getmtime')
    @patch('os.path.exists')
    async def test_add_file(self, mock_exists, mock_getmtime, mock_chunk_text, mock_load_document):
        """Test adding a file to the knowledge base."""
        # Setup mocks
        mock_exists.return_value = True
        mock_getmtime.return_value = 12345
        mock_load_document.return_value = self.test_file_content
        mock_chunk_text.return_value = [
            "This is a test file for knowledge testing.",
            "It contains information about testing knowledge functionality.",
            "MUXI Framework allows agents to use knowledge sources."
        ]

        # Create knowledge source
        knowledge_source = FileKnowledge(
            path="/path/to/test.txt",
            description="Test file"
        )

        # Add to knowledge base
        with patch.object(self.knowledge_handler, '_save_embeddings') as mock_save:
            chunks_added = await self.knowledge_handler.add_file(
                knowledge_source, self.generate_embeddings
            )

            # Verify file was processed
            mock_load_document.assert_called_once_with("/path/to/test.txt")
            mock_chunk_text.assert_called_once_with(self.test_file_content)

            # Verify embeddings were generated
            self.generate_embeddings.assert_called_once()

            # Verify chunks were added
            self.assertEqual(chunks_added, 3)
            self.assertEqual(len(self.knowledge_handler.documents), 3)
            self.assertEqual(self.knowledge_handler.index.ntotal, 3)

            # Verify metadata
            self.assertEqual(self.knowledge_handler.documents[0]["source"], "/path/to/test.txt")
            self.assertEqual(self.knowledge_handler.documents[0]["description"], "Test file")
            self.assertEqual(self.knowledge_handler.documents[0]["mtime"], 12345)

            # Verify save was called
            mock_save.assert_called_once()

    @patch('os.path.getmtime')
    @patch('os.path.exists')
    async def test_add_file_already_processed(self, mock_exists, mock_getmtime):
        """Test adding a file that was already processed."""
        # Setup mocks
        mock_exists.return_value = True
        mock_getmtime.return_value = 12345

        # Add a document to indicate file was already processed
        self.knowledge_handler.documents = [
            {"content": "Existing doc", "source": "/path/to/test.txt", "mtime": 12345}
        ]

        # Create knowledge source
        knowledge_source = FileKnowledge(
            path="/path/to/test.txt",
            description="Test file"
        )

        # Add to knowledge base
        chunks_added = await self.knowledge_handler.add_file(
            knowledge_source, self.generate_embeddings
        )

        # Verify no chunks were added
        self.assertEqual(chunks_added, 0)
        self.assertEqual(len(self.knowledge_handler.documents), 1)

    @patch('os.path.exists')
    async def test_add_file_not_found(self, mock_exists):
        """Test handling file not found error."""
        # Setup mock
        mock_exists.return_value = False

        # Create knowledge source
        knowledge_source = FileKnowledge(
            path="/path/to/nonexistent.txt",
            description="Test file"
        )

        # Add to knowledge base
        chunks_added = await self.knowledge_handler.add_file(
            knowledge_source, self.generate_embeddings
        )

        # Verify no chunks were added
        self.assertEqual(chunks_added, 0)
        self.assertEqual(len(self.knowledge_handler.documents), 0)

    async def test_remove_file(self):
        """Test removing a file from the knowledge base."""
        # Add documents
        self.knowledge_handler.documents = [
            {"content": "Doc 1", "source": "/path/to/test.txt", "index": 0},
            {"content": "Doc 2", "source": "/path/to/other.txt", "index": 1},
            {"content": "Doc 3", "source": "/path/to/test.txt", "index": 2}
        ]

        # Set up mock index
        self.knowledge_handler.index = MagicMock()

        # Mock save_embeddings
        with patch.object(self.knowledge_handler, '_save_embeddings') as mock_save:
            # Set documents empty to simulate all documents being removed
            self.knowledge_handler.documents = []

            # Remove file
            result = await self.knowledge_handler.remove_file("/path/to/test.txt")

            # Verify result
            self.assertTrue(result)

            # Verify save was called
            mock_save.assert_called_once()

    async def test_remove_file_not_found(self):
        """Test removing a file that isn't in the knowledge base."""
        # Add documents for a different file
        self.knowledge_handler.documents = [
            {"content": "Doc 1", "source": "/path/to/other.txt", "index": 0}
        ]

        # Remove nonexistent file
        result = await self.knowledge_handler.remove_file("/path/to/nonexistent.txt")

        # Verify result
        self.assertFalse(result)

        # Verify documents weren't changed
        self.assertEqual(len(self.knowledge_handler.documents), 1)

    async def test_search(self):
        """Test searching the knowledge base."""
        # Add documents
        self.knowledge_handler.documents = [
            {"content": "MUXI Framework documentation", "source": "doc1.txt", "index": 0},
            {"content": "Knowledge base information", "source": "doc2.txt", "index": 1},
            {"content": "Testing functionality", "source": "doc3.txt", "index": 2}
        ]

        # Mock FAISS index search
        mock_index = MagicMock()
        mock_index.search.return_value = (
            np.array([[0.1, 0.2, 0.9]]),  # Distances
            np.array([[2, 1, 0]])          # Indices
        )
        self.knowledge_handler.index = mock_index

        # Mock embedding generation
        generate_embedding = AsyncMock()
        generate_embedding.return_value = [[0.5] * 1536]

        # Search for information
        results = await self.knowledge_handler.search(
            "testing framework",
            generate_embedding,
            top_k=3,
            threshold=0.0
        )

        # Verify search was performed
        generate_embedding.assert_called_once_with(["testing framework"])
        mock_index.search.assert_called_once()

        # Verify results
        self.assertEqual(len(results), 3)

        # Results should be in order of relevance (reverse of distances)
        self.assertEqual(results[0]["content"], "Testing functionality")
        self.assertEqual(results[1]["content"], "Knowledge base information")
        self.assertEqual(results[2]["content"], "MUXI Framework documentation")

        # Verify relevance scores
        self.assertAlmostEqual(results[0]["relevance"], 1.0 - 0.9)
        self.assertAlmostEqual(results[1]["relevance"], 1.0 - 0.2)
        self.assertAlmostEqual(results[2]["relevance"], 1.0 - 0.1)

    async def test_search_with_threshold(self):
        """Test searching with a relevance threshold."""
        # Add documents
        self.knowledge_handler.documents = [
            {"content": "MUXI Framework documentation", "source": "doc1.txt", "index": 0},
            {"content": "Knowledge base information", "source": "doc2.txt", "index": 1},
            {"content": "Testing functionality", "source": "doc3.txt", "index": 2}
        ]

        # Mock FAISS index search
        mock_index = MagicMock()
        mock_index.search.return_value = (
            np.array([[0.1, 0.6, 0.9]]),  # Distances
            np.array([[2, 1, 0]])          # Indices
        )
        self.knowledge_handler.index = mock_index

        # Mock embedding generation
        generate_embedding = AsyncMock()
        generate_embedding.return_value = [[0.5] * 1536]

        # Search with threshold of 0.5
        results = await self.knowledge_handler.search(
            "testing framework",
            generate_embedding,
            top_k=3,
            threshold=0.5
        )

        # Verify results - only one document should be above threshold
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "MUXI Framework documentation")
        self.assertAlmostEqual(results[0]["relevance"], 0.9)

    async def test_search_empty_index(self):
        """Test searching an empty knowledge base."""
        # Ensure index is empty
        self.knowledge_handler.index = faiss.IndexFlatL2(1536)
        self.knowledge_handler.documents = []

        # Mock embedding generation
        generate_embedding = AsyncMock()

        # Search
        results = await self.knowledge_handler.search(
            "testing framework",
            generate_embedding
        )

        # Verify no results
        self.assertEqual(results, [])

        # Verify embedding function wasn't called
        generate_embedding.assert_not_called()

    def test_get_sources(self):
        """Test getting knowledge sources."""
        # Add documents
        self.knowledge_handler.documents = [
            {"content": "Doc 1", "source": "file1.txt"},
            {"content": "Doc 2", "source": "file2.txt"},
            {"content": "Doc 3", "source": "file1.txt"}
        ]

        # Get sources
        sources = self.knowledge_handler.get_sources()

        # Verify unique sources
        self.assertEqual(len(sources), 2)
        self.assertIn("file1.txt", sources)
        self.assertIn("file2.txt", sources)


if __name__ == "__main__":
    unittest.main()
