"""
Smart buffer memory implementation with semantic search.

This module provides a buffer memory system that combines recency with semantic search
capabilities using FAISS for efficient vector similarity operations.
"""

import time
from typing import Dict, List, Any, Optional
from collections import deque

import faiss
import numpy as np
from loguru import logger

from muxi.core.memory.base import BaseMemory
from muxi.core.models.base import BaseModel


class SmartBufferMemory(BaseMemory):
    """
    A smart buffer memory implementation with semantic search capabilities.

    This class provides a fixed-size buffer for storing recent messages, but with
    semantic search capabilities powered by FAISS vector similarity search.
    When the buffer is full, the oldest messages are removed.
    """

    def __init__(
        self,
        max_size: int = 100,
        vector_dimension: int = 1536,
        model: Optional[BaseModel] = None,
        default_score: float = 0.8,
    ):
        """
        Initialize the smart buffer memory.

        Args:
            max_size: The maximum number of messages to store.
            vector_dimension: Dimension of the embedding vectors.
            model: The language model to use for generating embeddings.
                If None, the memory will fall back to recency-based retrieval.
            default_score: Default similarity score for recency-based results.
        """
        self.max_size = max_size
        self.dimension = vector_dimension
        self.model = model
        self.default_score = default_score

        # Use deque for ordered storage with automatic cleanup
        self.buffer = deque(maxlen=max_size)

        # Initialize FAISS index if we have a model
        self.has_vector_search = model is not None
        if self.has_vector_search:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.embedding_map = {}  # Maps buffer indices to FAISS indices
            logger.info("Initialized SmartBufferMemory with vector search capabilities")
        else:
            logger.info("Initialized SmartBufferMemory in recency-only mode (no model provided)")

    async def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add content to the memory.

        Args:
            content: The content to add to memory.
            metadata: Optional metadata to associate with the content.
        """
        # Default metadata if not provided
        if metadata is None:
            metadata = {}

        # Add timestamp to metadata
        if "timestamp" not in metadata:
            metadata["timestamp"] = time.time()

        # Create the entry to store
        entry = {
            "content": content,
            "metadata": metadata,
            "index": len(self.buffer),  # Current position in buffer
        }

        # Add embedding if we have a model
        if self.has_vector_search and self.model:
            try:
                # Generate embedding asynchronously
                embedding = await self.model.embed(content)
                entry["embedding"] = embedding

                # Add to FAISS index
                vector = np.array([embedding]).astype("float32")
                self.index.add(vector)

                # Update mapping
                faiss_idx = self.index.ntotal - 1
                self.embedding_map[len(self.buffer)] = faiss_idx
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")

        # Add to buffer
        self.buffer.appendleft(entry)

        # Update indices of all items in buffer
        for i, item in enumerate(self.buffer):
            item["index"] = i

        # Rebuild embedding map if we have a full buffer (simplifies management)
        if self.has_vector_search and len(self.buffer) == self.max_size:
            self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild the FAISS index from current buffer contents to maintain consistency."""
        if not self.has_vector_search:
            return

        # Reset the index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.embedding_map = {}

        # Rebuild vectors
        vectors = []
        for i, item in enumerate(self.buffer):
            if "embedding" in item:
                vectors.append(item["embedding"])
                self.embedding_map[i] = len(vectors) - 1

        if vectors:
            # Add vectors to index
            vectors_array = np.array(vectors).astype("float32")
            self.index.add(vectors_array)

    async def search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        query_vector: Optional[List[float]] = None,
        recency_bias: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant content in memory.

        For smart buffer memory, this combines semantic search with recency.
        If a model is not available, falls back to recency-based results.

        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            filter_metadata: Optional metadata criteria for filtering results.
            query_vector: Optional pre-computed query embedding.
            recency_bias: How much to weight recency vs semantic relevance (0-1).
                Higher values favor recent messages over semantic matches.

        Returns:
            A list of dictionaries containing the retrieved content and metadata,
            with similarity scores.
        """
        # Cap limit to buffer size
        limit = min(limit, len(self.buffer))
        if limit == 0:
            return []

        # If we don't have vector search capability, return most recent messages
        if not self.has_vector_search or not self.model:
            return self._recency_search(limit, filter_metadata)

        # Get embedding for query if not provided
        if query_vector is None:
            try:
                query_vector = await self.model.embed(query)
            except Exception as e:
                logger.error(f"Error generating query embedding: {e}")
                return self._recency_search(limit, filter_metadata)

        # Convert to numpy array
        query_array = np.array([query_vector]).astype("float32")

        # Search FAISS index
        k = min(limit * 2, len(self.embedding_map))  # Get more results than needed for filtering
        if k == 0:
            return self._recency_search(limit, filter_metadata)

        distances, faiss_indices = self.index.search(query_array, k)

        # Convert FAISS indices to buffer indices
        results = []
        buffer_indices = {}
        for i, faiss_idx in enumerate(faiss_indices[0]):
            # Skip invalid results
            if faiss_idx < 0 or faiss_idx >= self.index.ntotal:
                continue

            # Find buffer index for this FAISS index
            buffer_idx = None
            for buf_idx, f_idx in self.embedding_map.items():
                if f_idx == faiss_idx:
                    buffer_idx = buf_idx
                    break

            if buffer_idx is not None and buffer_idx < len(self.buffer):
                # Skip if already processed
                if buffer_idx in buffer_indices:
                    continue

                buffer_indices[buffer_idx] = True

                # Get item from buffer
                item = self.buffer[buffer_idx]

                # Apply metadata filter if specified
                if filter_metadata and not self._matches_filter(item, filter_metadata):
                    continue

                # Calculate combined score (semantic + recency)
                semantic_score = 1.0 / (1.0 + float(distances[0][i]))
                recency_score = 1.0 - (buffer_idx / len(self.buffer))
                combined_score = (1 - recency_bias) * semantic_score + recency_bias * recency_score

                results.append({
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "score": combined_score,
                    "buffer_index": buffer_idx,
                })

        # Sort by combined score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:limit]

        # If we didn't get enough results, supplement with recency-based results
        if len(results) < limit:
            recency_results = self._recency_search(
                limit - len(results),
                filter_metadata,
                exclude_indices=buffer_indices
            )
            results.extend(recency_results)

        return results

    def _recency_search(
        self,
        limit: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
        exclude_indices: Optional[Dict[int, bool]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform a recency-based search (fallback when no vector search is available).

        Args:
            limit: Maximum number of results to return.
            filter_metadata: Optional metadata criteria for filtering.
            exclude_indices: Optional indices to exclude from results.

        Returns:
            Most recent messages matching filters.
        """
        results = []
        exclude_indices = exclude_indices or {}

        for buffer_idx, item in enumerate(self.buffer):
            # Skip excluded indices
            if buffer_idx in exclude_indices:
                continue

            # Apply metadata filter if specified
            if filter_metadata and not self._matches_filter(item, filter_metadata):
                continue

            # Calculate recency score
            recency_score = 1.0 - (buffer_idx / len(self.buffer))

            # Add to results
            results.append({
                "content": item["content"],
                "metadata": item["metadata"],
                "score": recency_score * self.default_score,  # Adjust recency score
                "buffer_index": buffer_idx,
            })

            # Stop if we have enough results
            if len(results) >= limit:
                break

        return results

    def _matches_filter(self, item: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """
        Check if an item matches the specified metadata filters.

        Args:
            item: The memory item to check.
            filter_metadata: Metadata criteria for filtering.

        Returns:
            True if the item matches the filter, False otherwise.
        """
        metadata = item.get("metadata", {})

        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False

        return True

    def clear(self, filter_metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Clear the buffer memory, optionally filtering by metadata.

        Args:
            filter_metadata: Optional metadata criteria for selective clearing.
        """
        if filter_metadata is None:
            # Clear everything
            self.buffer.clear()
            if self.has_vector_search:
                self.index = faiss.IndexFlatL2(self.dimension)
                self.embedding_map = {}
            return

        # Selective clearing based on filter
        indices_to_keep = []
        items_to_keep = []

        for i, item in enumerate(self.buffer):
            if not self._matches_filter(item, filter_metadata):
                indices_to_keep.append(i)
                items_to_keep.append(item)

        # Reset buffer
        self.buffer.clear()

        # Add back kept items
        for item in items_to_keep:
            self.buffer.append(item)

        # Rebuild index
        if self.has_vector_search:
            self._rebuild_index()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the buffer memory.

        Returns:
            Dictionary with memory statistics.
        """
        return {
            "total_items": len(self.buffer),
            "max_size": self.max_size,
            "vector_search_enabled": self.has_vector_search,
            "vector_dimension": self.dimension,
            "vector_index_size": self.index.ntotal if self.has_vector_search else 0,
        }


# Alias for backward compatibility
BufferMemory = SmartBufferMemory
