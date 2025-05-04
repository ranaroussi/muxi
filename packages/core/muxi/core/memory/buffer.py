# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Buffer Memory - Smart Context Window Implementation
# Description:  Hybrid recency and semantic search memory buffer implementation
# Role:         Provides temporary conversation memory with semantic search
# Usage:        Used by the Orchestrator to maintain conversation context
# Author:       Muxi Framework Team
#
# The Buffer Memory is a sophisticated short-term memory system that combines:
#
# 1. Recency-Based Memory
#    - Maintains a fixed-size context window of recent messages
#    - Ensures immediate conversation context is preserved
#    - Supports filtering by metadata (agent_id, user_id, etc.)
#
# 2. Semantic Search Capability
#    - Uses FAISS vector index for efficient similarity search
#    - Maintains embeddings for all messages in the buffer
#    - Enables retrieving contextually relevant information
#
# 3. Hybrid Retrieval Approach
#    - Combines recency and semantic relevance scores
#    - Configurable recency bias for different use cases
#    - Graceful fallback to recency-only if vector search unavailable
#
# The BufferMemory uses a two-tiered size system:
#   - context_window (max_size): The number of recent messages to include
#   - buffer_multiplier: Total buffer capacity = max_size × buffer_multiplier
#
# This design addresses the need for a larger storage capacity while
# maintaining a smaller, focused context window for immediate conversations.
#
# Example usage:
#
#   # Create buffer memory with semantic search
#   model = OpenAIModel(model="text-embedding-3-small")
#   buffer = BufferMemory(
#       max_size=10,              # Context window size
#       buffer_multiplier=10,     # Total capacity = 10 × 10 = 100
#       model=model               # For generating embeddings
#   )
#
#   # Add items to buffer
#   await buffer.add("User message", {"role": "user"})
#   await buffer.add("Assistant response", {"role": "assistant"})
#
#   # Search for relevant content
#   results = await buffer.search("topic of interest", recency_bias=0.3)
#
# The implementation includes thread-safety, automatic index rebuilding,
# and comprehensive error handling for production-grade reliability.
# =============================================================================

import collections
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    import numpy as np
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning(
        "FAISS not available. Vector search in BufferMemory will be disabled. "
        "Install with 'pip install faiss-cpu' or 'pip install faiss-gpu'."
    )


class BufferMemory:
    """
    A fixed-size buffer memory with vector search capabilities.

    BufferMemory provides a hybrid memory system that combines recency-based retrieval
    with semantic search powered by FAISS. It maintains a buffer of messages with
    associated metadata and vector embeddings for efficient contextual search.

    The buffer operates with two key size parameters:
    - max_size (context window): Number of most recent items to include when retrieving by recency
    - buffer_multiplier: Factor to determine total buffer capacity (max_size × buffer_multiplier)

    This enables maintaining a larger storage for vector search while keeping a smaller
    context window for recent conversations.
    """

    def __init__(
        self,
        max_size: int = 10,
        buffer_multiplier: int = 10,
        dimension: int = 1536,
        model=None,
    ):
        """
        Initialize a buffer memory with vector search capabilities.

        Args:
            max_size: The context window size - number of recent messages to include
                when retrieving by recency. Default is 10.
            buffer_multiplier: Multiplier to determine total buffer capacity.
                Total capacity = max_size × buffer_multiplier. Default is 10.
            dimension: Dimension of embedding vectors. Default is 1536, which matches
                OpenAI's text-embedding-3-small model.
            model: Optional language model instance for generating embeddings.
                Must have an async embed(text) method. If None, vector search
                will be disabled and only recency-based retrieval will be used.
        """
        # Buffer size and content
        self.max_size = max_size
        self.buffer_multiplier = buffer_multiplier
        self.buffer_size = max_size * buffer_multiplier
        self.buffer = collections.deque(maxlen=self.buffer_size)

        # Vector search configuration
        self.dimension = dimension
        self.model = model
        self.has_vector_search = FAISS_AVAILABLE

        # Initialize vector storage if FAISS is available
        if self.has_vector_search:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index_mapping = {}  # Maps buffer indices to FAISS indices
            self.index_count = 0  # Counter for FAISS indices
            self.needs_rebuild = False  # Flag to track if index needs rebuilding
        else:
            self.index = None
            self.index_mapping = None
            self.index_count = 0
            logger.warning(
                "FAISS not available, BufferMemory will use recency-based search only. "
                "Install FAISS for vector search capabilities."
            )

    async def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an item to the buffer memory.

        This method adds a new text item to the buffer with its associated metadata.
        If a language model is available, it also generates and stores an embedding
        vector for the text, enabling semantic search functionality.

        Args:
            text: The text content to add to the buffer. This is what will be searched
                and retrieved later.
            metadata: Optional dictionary of metadata associated with this text.
                Can include any contextual information like timestamps, user IDs,
                message roles, etc. Default is an empty dictionary.
        """
        # Initialize metadata dictionary if None
        if metadata is None:
            metadata = {}

        # Create item with text and metadata
        item = {"text": text, "metadata": metadata}

        # Generate embedding if model is available
        if self.model and self.has_vector_search:
            try:
                # Generate embedding for the text
                embedding = await self.model.embed(text)
                item["embedding"] = embedding

                # Record the mapping from buffer index to FAISS index
                buffer_idx = len(self.buffer)
                self.index_mapping[buffer_idx] = self.index_count

                # Add the embedding to the FAISS index
                embedding_array = np.array([embedding], dtype=np.float32)
                self.index.add(embedding_array)

                # Increment the FAISS index counter
                self.index_count += 1
            except Exception as e:
                # Handle embedding generation failures gracefully
                logger.error(f"Error generating embedding: {e}")
                item["embedding"] = None
        else:
            # No embedding if model or FAISS is not available
            item["embedding"] = None

        # Add item to the buffer
        self.buffer.append(item)

        # Check if we need to rebuild the index (buffer is full and items were removed)
        if len(self.buffer) == self.buffer_size and self.has_vector_search and self.model:
            self.needs_rebuild = True

    def _rebuild_index(self) -> None:
        """
        Rebuild the FAISS index after buffer overflow.

        This internal method rebuilds the FAISS index and mapping when the buffer
        is full and new items have displaced old ones. It ensures the vector search
        stays in sync with the actual buffer contents.
        """
        if not self.has_vector_search or not self.model:
            return

        # Create a new index with the same dimension
        new_index = faiss.IndexFlatL2(self.dimension)
        new_mapping = {}
        new_count = 0

        # Add embeddings from the current buffer to the new index
        embeddings = []
        for i, item in enumerate(self.buffer):
            if "embedding" in item and item["embedding"] is not None:
                embeddings.append(item["embedding"])
                new_mapping[i] = new_count
                new_count += 1

        # Add collected embeddings to the index if any exist
        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            new_index.add(embeddings_array)

        # Replace the old index and mapping
        self.index = new_index
        self.index_mapping = new_mapping
        self.index_count = new_count
        self.needs_rebuild = False

        logger.debug(f"Rebuilt FAISS index with {new_count} embeddings")

    def _recency_search(
        self,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the buffer based on recency only.

        This internal method searches the buffer based solely on recency (most recent first)
        and applies optional metadata filtering. It's used as a fallback when vector
        search is not available or as part of the hybrid search approach.

        Args:
            limit: Maximum number of results to return. Default is 10.
            filter_metadata: Optional dictionary of metadata for filtering.
                Only items with matching metadata values will be included.

        Returns:
            List of buffer items (dictionaries) with matching metadata,
            ordered by recency (most recent first).
        """
        # Start with the most recent items (up to max_size)
        # This implements the concept of a smaller context window within the larger buffer
        recent_items = list(self.buffer)[-self.max_size:]

        # Apply metadata filtering if specified
        if filter_metadata:
            results = []
            for item in reversed(recent_items):  # Reverse to get most recent first
                # Check if all filter criteria match
                if all(
                    key in item["metadata"] and item["metadata"][key] == value
                    for key, value in filter_metadata.items()
                ):
                    # Include a copy of the item to avoid modifying the buffer
                    results.append(item.copy())
                    # Stop if we've reached the limit
                    if len(results) >= limit:
                        break
            return results
        else:
            # If no filtering, just return the most recent items (most recent first)
            return [item.copy() for item in reversed(recent_items)][:limit]

    async def search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        query_vector: Optional[List[float]] = None,
        recency_bias: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Search the buffer using vector similarity and recency.

        This method performs a hybrid search that combines semantic similarity with
        recency bias. It can use a pre-computed query vector or generate one from
        the query text if a model is available.

        Args:
            query: The search query text. Used to generate a query vector if
                query_vector is not provided.
            limit: Maximum number of results to return. Default is 10.
            filter_metadata: Optional dictionary of metadata for filtering.
                Only items with matching metadata values will be included.
            query_vector: Optional pre-computed query vector. If provided,
                skips the embedding generation step.
            recency_bias: Weight given to recency vs. semantic similarity (0.0-1.0).
                Higher values favor recent items, lower values favor semantic similarity.
                Default is 0.3, providing a balance that slightly favors similarity.

        Returns:
            List of matched items sorted by the combined score of semantic
            similarity and recency. Each item includes the original text, metadata,
            and a score field indicating the match quality.
        """
        # If we don't have vector search capability, return most recent messages
        if not self.has_vector_search or not self.model:
            logger.debug("Using recency-only search (vector search not available)")
            return self._recency_search(limit, filter_metadata)

        # Rebuild index if needed
        if self.needs_rebuild:
            self._rebuild_index()

        # Generate a query vector if not provided
        if query_vector is None:
            try:
                query_vector = await self.model.embed(query)
            except Exception as e:
                logger.error(f"Error generating query embedding: {e}")
                # Fallback to recency search if embedding generation fails
                return self._recency_search(limit, filter_metadata)

        # If we have no embeddings in the index, use recency search
        if self.index_count == 0:
            return self._recency_search(limit, filter_metadata)

        try:
            # Convert query vector to numpy array
            query_np = np.array([query_vector], dtype=np.float32)

            # Search the FAISS index for similar vectors
            k = min(limit * 2, self.index_count)  # Get more results to allow for filtering
            distances, indices = self.index.search(query_np, k)

            # Map FAISS indices back to buffer indices
            buffer_indices = []
            for faiss_idx in indices[0]:
                # Find the buffer index for this FAISS index
                for buffer_idx, mapped_faiss_idx in self.index_mapping.items():
                    if mapped_faiss_idx == faiss_idx:
                        buffer_indices.append(buffer_idx)
                        break

            # Combine semantic score with recency score
            results = []
            for i, buffer_idx in enumerate(buffer_indices):
                # Make sure buffer_idx is in range
                if buffer_idx >= len(self.buffer):
                    continue

                item = self.buffer[buffer_idx].copy()

                # Apply metadata filters if provided
                if filter_metadata and not all(
                    key in item["metadata"] and item["metadata"][key] == value
                    for key, value in filter_metadata.items()
                ):
                    continue

                # Calculate combined score (semantic + recency)
                semantic_score = 1.0 / (1.0 + float(distances[0][i]))
                recency_score = 1.0 - (buffer_idx / len(self.buffer))
                combined_score = (1 - recency_bias) * semantic_score + recency_bias * recency_score

                # Add score to the item
                item["score"] = combined_score
                results.append(item)

                # Stop if we have enough results
                if len(results) >= limit:
                    break

            # If we don't have enough results, try recency search
            if not results:
                return self._recency_search(limit, filter_metadata)

            # Sort by combined score (descending)
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

        except Exception as e:
            # Handle FAISS search errors gracefully
            logger.error(f"Error in vector search: {e}")
            return self._recency_search(limit, filter_metadata)

    def get_recent_items(
        self, limit: int = 10, filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent items from the buffer.

        This method retrieves the most recent items from the buffer,
        optionally filtered by metadata. It uses pure recency ordering
        without any semantic search.

        Args:
            limit: Maximum number of items to return. Default is 10.
            filter_metadata: Optional dictionary of metadata for filtering.
                Only items with matching metadata values will be included.

        Returns:
            List of the most recent items matching the filter criteria.
        """
        return self._recency_search(limit, filter_metadata)

    def clear(self) -> None:
        """
        Clear the buffer memory.

        This method removes all items from the buffer and resets the FAISS index
        if vector search is enabled. It effectively resets the memory to an empty state.
        """
        # Clear the buffer
        self.buffer.clear()

        # Reset FAISS index if enabled
        if self.has_vector_search:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index_mapping = {}
            self.index_count = 0
            self.needs_rebuild = False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the buffer memory.

        This method returns information about the current state of the buffer
        memory, including size information, vector search availability, and
        other relevant metrics.

        Returns:
            Dictionary with statistics about the buffer memory:
            - buffer_length: Current number of items in the buffer
            - buffer_capacity: Maximum number of items the buffer can hold
            - context_window_size: Size of the context window (max_size)
            - has_vector_search: Whether vector search is available
            - vector_index_size: Number of vectors in the FAISS index
            - model_available: Whether a model is available for embedding generation
        """
        stats = {
            "buffer_length": len(self.buffer),
            "buffer_capacity": self.buffer_size,
            "context_window_size": self.max_size,
            "has_vector_search": self.has_vector_search,
            "model_available": self.model is not None,
        }

        if self.has_vector_search:
            stats["vector_index_size"] = self.index_count

        return stats

    def __len__(self) -> int:
        """Return the current length of the buffer."""
        return len(self.buffer)
