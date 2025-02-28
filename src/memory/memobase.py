"""
Memobase: Multi-user memory system for AI Agent Framework.

This module provides a centralized memory manager that supports multiple users
with PostgreSQL/PGVector for memory storage.
"""

from typing import Dict, List, Any, Optional
import asyncio
import time

from src.memory.long_term import LongTermMemory


class Memobase:
    """
    A multi-user memory manager that provides access to PostgreSQL/PGVector
    storage with user context awareness.

    Memobase allows agents to maintain separate memory contexts for different
    users while providing a unified interface for memory operations.
    """

    def __init__(
        self,
        long_term_memory: LongTermMemory,
        default_user_id: int = 0
    ):
        """
        Initialize the Memobase memory manager.

        Args:
            long_term_memory: PostgreSQL/PGVector-based long-term memory.
            default_user_id: The default user ID to use (0 for single-user
                mode).
        """
        self.default_user_id = default_user_id
        self.long_term_memory = long_term_memory

    async def add(
        self,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> int:
        """
        Add content to memory for a specific user.

        Args:
            content: The content to add to memory.
            embedding: Optional pre-computed embedding for the content.
            metadata: Optional metadata to associate with the content.
            user_id: The user ID to add memory for. If None, uses the default
                user.

        Returns:
            The ID of the newly created memory entry.
        """
        user_id = user_id if user_id is not None else self.default_user_id
        metadata = metadata or {}

        # Add user_id to metadata
        metadata["user_id"] = user_id

        # Add timestamp if not provided
        if "timestamp" not in metadata:
            metadata["timestamp"] = time.time()

        # Create a collection name based on the user ID
        collection = f"user_{user_id}"

        # Ensure the collection exists
        try:
            self.long_term_memory._ensure_collection_exists(None, collection)
        except Exception:
            # If calling with None session fails, create collection properly
            self.long_term_memory.create_collection(
                collection,
                f"Memory for user {user_id}"
            )

        # Add to long-term memory
        memory_id = await asyncio.to_thread(
            self.long_term_memory.add,
            text=content,
            embedding=embedding,
            metadata=metadata,
            collection=collection
        )

        return memory_id

    async def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        limit: int = 5,
        user_id: Optional[int] = None,
        additional_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant content in memory for a specific user.

        Args:
            query: The query to search for (used if query_embedding not
                provided).
            query_embedding: Optional pre-computed embedding for the query.
            limit: The maximum number of results to return.
            user_id: The user ID to search memory for. If None, uses the
                default user.
            additional_filter: Additional metadata filters to apply to the
                search.

        Returns:
            A list of dictionaries containing the retrieved content and
            metadata.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Create filter for user_id
        filter_metadata = {"user_id": user_id}

        # Add any additional filters
        if additional_filter:
            filter_metadata.update(additional_filter)

        # Create a collection name based on the user ID
        collection = f"user_{user_id}"

        # Search long-term memory
        search_results = await asyncio.to_thread(
            self.long_term_memory.search,
            query=query,
            query_embedding=query_embedding,
            filter_metadata=filter_metadata,
            k=limit,
            collection=collection
        )

        # Convert results to standard format
        results = []
        for distance, memory in search_results:
            results.append({
                "content": memory.get("text", ""),
                "metadata": memory.get("meta_data", {}),
                "distance": distance,
                "source": "memobase",
                "id": memory.get("id"),
                "created_at": memory.get("created_at")
            })

        return results

    def clear_user_memory(self, user_id: Optional[int] = None) -> None:
        """
        Clear memory for a specific user by recreating their collection.

        Args:
            user_id: The user ID to clear memory for. If None, uses the
                default user.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Create a collection name based on the user ID
        collection = f"user_{user_id}"

        # Drop and recreate the collection
        try:
            self.long_term_memory.delete_collection(collection)
        except Exception:
            pass  # Collection might not exist

        self.long_term_memory.create_collection(
            collection,
            f"Memory collection for user {user_id}"
        )

    def get_user_memories(
        self,
        user_id: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "created_at",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get recent memories for a specific user.

        Args:
            user_id: The user ID to get memories for. If None, uses the
                default user.
            limit: Maximum number of memories to return.
            offset: Number of memories to skip (for pagination).
            sort_by: Field to sort by (created_at, updated_at, id).
            ascending: Whether to sort in ascending order.

        Returns:
            A list of memory entries.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Create a collection name based on the user ID
        collection = f"user_{user_id}"

        # Get memories from the collection
        memories = self.long_term_memory.get_recent_memories(
            collection=collection,
            limit=limit
        )

        return [
            {
                "content": memory.get("text", ""),
                "metadata": memory.get("meta_data", {}),
                "id": memory.get("id"),
                "created_at": memory.get("created_at"),
                "updated_at": memory.get("updated_at")
            }
            for memory in memories
        ]
