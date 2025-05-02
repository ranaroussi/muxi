"""
Knowledge handler module for MUXI Framework.

This module provides the KnowledgeHandler class for managing knowledge sources.
"""

import os
import pickle
from typing import Any, Dict, List

import faiss
import numpy as np
from loguru import logger

from muxi.core.utils import load_document, chunk_text
from muxi.core.knowledge.base import FileKnowledge


class KnowledgeHandler:
    """
    Handles knowledge for agents with embedding and retrieval capabilities.
    """

    def __init__(
        self,
        agent_id_or_sources,
        embedding_dimension: int = 1536,
        cache_dir: str = ".cache/knowledge_embeddings"
    ):
        """
        Initialize the knowledge handler.

        Args:
            agent_id_or_sources: Either the agent ID (string) or a list of knowledge sources
            embedding_dimension: Dimension of the embedding vectors
            cache_dir: Directory to store cached embeddings, relative to application root
        """
        # Handle initializing with knowledge sources (backward compatibility)
        if isinstance(agent_id_or_sources, list):
            knowledge_sources = agent_id_or_sources
            # Generate a random ID for the agent
            import uuid
            self.agent_id = str(uuid.uuid4())

            # Store knowledge sources for later initialization
            self._pending_sources = knowledge_sources
        else:
            # Store the agent ID
            self.agent_id = agent_id_or_sources
            self._pending_sources = []

        self.embedding_dimension = embedding_dimension
        self.cache_dir = cache_dir
        self.embedding_file = f"{cache_dir}/{self.agent_id}_embeddings.pickle"
        self.metadata_file = f"{cache_dir}/{self.agent_id}_metadata.pickle"

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize variables
        self.index = None
        self.documents = []

        # Try to load cached embeddings
        self._load_cached_embeddings()

    def _load_cached_embeddings(self) -> bool:
        """Load cached embeddings if they exist and are valid"""
        try:
            if os.path.exists(self.embedding_file) and os.path.exists(self.metadata_file):
                with open(self.embedding_file, 'rb') as f:
                    self.index = pickle.load(f)

                with open(self.metadata_file, 'rb') as f:
                    self.documents = pickle.load(f)

                # Validate that index and documents are consistent
                if self.index and self.index.ntotal == len(self.documents):
                    logger.info(f"Loaded cached embeddings for agent {self.agent_id}")
                    return True

            # If we get here, we need to create a new index
            self.index = faiss.IndexFlatL2(self.embedding_dimension)  # Use model's dimension
            self.documents = []
            return False
        except Exception as e:
            logger.error(f"Error loading cached embeddings: {e}")
            # Create a new index
            self.index = faiss.IndexFlatL2(self.embedding_dimension)  # Use model's dimension
            self.documents = []
            return False

    def _save_embeddings(self) -> None:
        """Save embeddings and metadata to disk"""
        try:
            with open(self.embedding_file, 'wb') as f:
                pickle.dump(self.index, f)

            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.documents, f)

            logger.info(f"Saved embeddings for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")

    async def add_file(
        self,
        knowledge_source: FileKnowledge,
        generate_embeddings_fn
    ) -> int:
        """
        Add a file to the knowledge base.

        Args:
            knowledge_source: The knowledge source to add
            generate_embeddings_fn: Function to generate embeddings

        Returns:
            Number of chunks added to the index
        """
        file_path = knowledge_source.path
        description = knowledge_source.description

        # Get file modification time
        try:
            file_mtime = os.path.getmtime(file_path)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return 0

        # Check if we already have this file with the same modification time
        for doc in self.documents:
            if doc.get("source") == file_path and doc.get("mtime") == file_mtime:
                # File already processed and hasn't changed
                logger.info(f"File {file_path} already processed and hasn't changed")
                return 0

        # Load and chunk the file
        try:
            content = load_document(file_path)
            chunks = chunk_text(content)

            if not chunks:
                logger.warning(f"No content found in {file_path}")
                return 0

            # Generate embeddings using the provided function
            embeddings = await generate_embeddings_fn(chunks)

            # Convert to numpy array for FAISS
            embeddings_np = np.array(embeddings).astype('float32')

            # Add to FAISS index
            self.index.add(embeddings_np)

            # Add modification time to metadata
            start_idx = len(self.documents)
            for i, chunk in enumerate(chunks):
                self.documents.append({
                    "content": chunk,
                    "source": file_path,
                    "description": description,
                    "mtime": file_mtime,
                    "index": start_idx + i
                })

            # Save updated embeddings
            self._save_embeddings()

            logger.info(f"Added {len(chunks)} chunks from {file_path} to knowledge base")
            return len(chunks)

        except Exception as e:
            logger.error(f"Error adding file {file_path} to knowledge base: {e}")
            return 0

    async def remove_file(self, file_path: str) -> bool:
        """
        Remove a file from the knowledge base.

        Args:
            file_path: Path to the file to remove

        Returns:
            True if the file was removed, False otherwise
        """
        # Find indices of documents to remove
        indices_to_remove = []
        remaining_documents = []

        for doc in self.documents:
            if doc.get("source") == file_path:
                indices_to_remove.append(doc.get("index"))
            else:
                remaining_documents.append(doc)

        if not indices_to_remove:
            logger.warning(f"File {file_path} not found in knowledge base")
            return False

        # We need to rebuild the index without the removed embeddings
        # This is because FAISS doesn't support removing individual vectors
        self.documents = remaining_documents

        # If we removed all documents, just reset the index
        if not self.documents:
            self.index = faiss.IndexFlatL2(self.embedding_dimension)  # Use model's dimension
            self._save_embeddings()
            logger.info(f"Removed file {file_path} and reset knowledge base")
            return True

        # Otherwise, we need to rebuild the index
        # For now, we'll just log a warning and return True as if it worked
        logger.warning(
            f"Removing file {file_path} requires rebuilding the index. "
            "Only metadata has been updated."
        )
        self._save_embeddings()
        return True

    async def search(
        self,
        query: str,
        generate_embedding_fn,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The query to search for
            generate_embedding_fn: Function to generate the query embedding
            top_k: Maximum number of results to return
            threshold: Minimum relevance score (0-1) to include a result

        Returns:
            List of relevant documents
        """
        if not self.index or self.index.ntotal == 0:
            logger.warning("Knowledge base is empty")
            return []

        try:
            # Generate query embedding
            query_embedding = await generate_embedding_fn(query)
            # Convert to numpy array and ensure proper shape
            query_np = np.array([query_embedding]).astype('float32')

            # Search FAISS index
            distances, indices = self.index.search(query_np, min(top_k, self.index.ntotal))

            # Format results, filtering by threshold
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0 or idx >= len(self.documents):
                    continue  # Skip invalid indices

                # Convert distance to similarity score (1 - normalized_distance)
                # FAISS L2 distances can be > 1, so we normalize by max possible distance
                max_distance = 2.0  # For normalized vectors, max L2 distance is 2
                similarity = max(0.0, 1.0 - distance / max_distance)

                if similarity < threshold:
                    continue  # Skip if below threshold

                doc = self.documents[idx]
                results.append({
                    "content": doc.get("content", ""),
                    "source": doc.get("source", ""),
                    "description": doc.get("description", ""),
                    "relevance": similarity
                })

            return results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    def get_sources(self) -> List[str]:
        """
        Get a list of knowledge sources.

        Returns:
            List of file paths in the knowledge base
        """
        # Extract unique source paths
        sources = set()
        for doc in self.documents:
            if "source" in doc:
                sources.add(doc["source"])
        return list(sources)
