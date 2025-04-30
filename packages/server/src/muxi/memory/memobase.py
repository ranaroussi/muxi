"""
Memobase: Multi-user memory system for MUXI Framework.

This module provides a centralized memory manager that supports multiple users
with PostgreSQL/PGVector for memory storage.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union

from muxi.server.memory.long_term import LongTermMemory


class Memobase:
    """
    A multi-user memory manager that provides access to PostgreSQL/PGVector
    storage with user context awareness.

    Memobase allows agents to maintain separate memory contexts for different
    users while providing a unified interface for memory operations.
    """

    # Constants for context memory
    CONTEXT_MEMORY_COLLECTION = "context_memory"
    CONTEXT_MEMORY_TYPE = "context_memory"

    def __init__(self, long_term_memory: LongTermMemory, default_user_id: int = 0):
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
        user_id: Optional[int] = None,
        collection: Optional[str] = None,
    ) -> int:
        """
        Add content to memory for a specific user.

        Args:
            content: The content to add to memory.
            embedding: Optional pre-computed embedding for the content.
            metadata: Optional metadata to associate with the content.
            user_id: The user ID to add memory for. If None, uses the default
                user.
            collection: Optional collection name to store the memory in.
                If None, uses the default user collection.

        Returns:
            The ID of the newly created memory entry.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # Return dummy ID for anonymous users
            return 0

        metadata = metadata or {}

        # Add user_id to metadata
        metadata["user_id"] = user_id

        # Add timestamp if not provided
        if "timestamp" not in metadata:
            metadata["timestamp"] = time.time()

        # Create a collection name based on the user ID if not provided
        if collection is None:
            collection = f"user_{user_id}"

        # Ensure the collection exists
        try:
            self.long_term_memory._ensure_collection_exists(None, collection)
        except Exception:
            # If calling with None session fails, create collection properly
            self.long_term_memory.create_collection(collection, f"Memory for user {user_id}")

        # Add to long-term memory
        memory_id = await asyncio.to_thread(
            self.long_term_memory.add,
            text=content,
            embedding=embedding,
            metadata=metadata,
            collection=collection,
        )

        return memory_id

    async def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        limit: int = 5,
        user_id: Optional[int] = None,
        additional_filter: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in memory for a specific user.

        Args:
            query: The text query to search for.
            query_embedding: Optional pre-computed embedding.
            limit: Maximum number of results to return.
            user_id: The user ID to search memory for. If None, uses the
                default user.
            additional_filter: Optional additional metadata filter.
            collection: Optional collection name to search in. If None, uses
                the default collection for the user.

        Returns:
            A list of memory entries, ordered by relevance.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # Return empty results for anonymous users
            return []

        additional_filter = additional_filter or {}

        # Add user_id to filter
        additional_filter["user_id"] = user_id

        # Create a collection name based on the user ID if not provided
        if collection is None:
            collection = f"user_{user_id}"

        # Search long-term memory
        search_results = await asyncio.to_thread(
            self.long_term_memory.search,
            query=query,
            query_embedding=query_embedding,
            filter_metadata=additional_filter,
            k=limit,
            collection=collection,
        )

        # Convert results to standard format
        results = []
        for distance, memory in search_results:
            results.append(
                {
                    "content": memory.get("text", ""),
                    "metadata": memory.get("meta_data", {}),
                    "distance": distance,
                    "source": "memobase",
                    "id": memory.get("id"),
                    "created_at": memory.get("created_at"),
                }
            )

        return results

    def clear_user_memory(self, user_id: Optional[int] = None) -> None:
        """
        Clear memory for a specific user by recreating their collection.

        Args:
            user_id: The user ID to clear memory for. If None, uses the
                default user.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # No-op for anonymous users
            return

        # Create a collection name based on the user ID
        collection = f"user_{user_id}"

        # Drop and recreate the collection
        try:
            self.long_term_memory.delete_collection(collection)
        except Exception:
            pass  # Collection might not exist

        self.long_term_memory.create_collection(collection, f"Memory collection for user {user_id}")

    def get_user_memories(
        self,
        user_id: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "created_at",
        ascending: bool = False,
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

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # Return empty list for anonymous users
            return []

        # Create a collection name based on the user ID
        collection = f"user_{user_id}"

        # Get memories from the collection
        memories = self.long_term_memory.get_recent_memories(collection=collection, limit=limit)

        return [
            {
                "content": memory.get("text", ""),
                "metadata": memory.get("meta_data", {}),
                "id": memory.get("id"),
                "created_at": memory.get("created_at"),
                "updated_at": memory.get("updated_at"),
            }
            for memory in memories
        ]

    async def add_user_context_memory(
        self,
        user_id: Optional[int] = None,
        knowledge: Dict[str, Any] = None,
        source: str = "explicit_upload",
        importance: float = 0.9,
    ) -> List[str]:
        """
        Add or update context memory about a user.

        Args:
            user_id: The user's ID. If None, uses the default user.
            knowledge: Dictionary of knowledge items where keys are knowledge
                categories and values are the corresponding information.
            source: Where this knowledge came from.
            importance: Importance score for this knowledge (0.0 to 1.0).
                Higher values make it more likely to be retrieved.

        Returns:
            List of memory IDs for the added knowledge items.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # Return empty list for anonymous users
            return []

        knowledge = knowledge or {}
        memory_ids = []

        # Ensure context memory collection exists
        collection_name = f"{self.CONTEXT_MEMORY_COLLECTION}_{user_id}"
        try:
            self.long_term_memory._ensure_collection_exists(None, collection_name)
        except Exception:
            self.long_term_memory.create_collection(
                collection_name,
                f"Context memory for user {user_id}"
            )

        # Process each knowledge item
        for key, value in knowledge.items():
            # Format the content as "key: value"
            if isinstance(value, (dict, list)):
                # Convert complex objects to JSON string
                value_str = json.dumps(value)
            else:
                value_str = str(value)

            content = f"{key}: {value_str}"

            # Add metadata
            metadata = {
                "type": self.CONTEXT_MEMORY_TYPE,
                "key": key,
                "source": source,
                "importance": importance,
                "user_id": user_id,
            }

            # Add to memory
            memory_id = await self.add(
                content=content,
                metadata=metadata,
                user_id=user_id,
                collection=collection_name,
            )

            memory_ids.append(memory_id)

        return memory_ids

    async def get_user_context_memory(
        self,
        user_id: Optional[int] = None,
        keys: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Retrieve context memory about a user.

        Args:
            user_id: The user's ID. If None, uses the default user.
            keys: Optional list of specific knowledge keys to retrieve.
                If None, retrieves all context memory.
            limit: Maximum number of knowledge items to retrieve.

        Returns:
            Dictionary of knowledge items where keys are knowledge categories
            and values are the corresponding information.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # Return empty dictionary for anonymous users
            return {}

        collection_name = f"{self.CONTEXT_MEMORY_COLLECTION}_{user_id}"

        # Check if collection exists
        try:
            self.long_term_memory._ensure_collection_exists(None, collection_name)
        except Exception:
            # Collection doesn't exist, return empty dict
            return {}

        # Prepare filter
        filter_params = {
            "type": self.CONTEXT_MEMORY_TYPE,
            "user_id": user_id,
        }

        results = []

        if keys:
            # Get specific keys
            for key in keys:
                key_filter = filter_params.copy()
                key_filter["key"] = key

                key_results = await self.search(
                    query=key,  # Use key as query for better matching
                    user_id=user_id,
                    additional_filter=key_filter,
                    collection=collection_name,
                    limit=1,  # Only need the most recent/relevant for each key
                )

                results.extend(key_results)
        else:
            # Get all context memory
            # Use empty query to match all items
            results = await self.search(
                query="",
                user_id=user_id,
                additional_filter=filter_params,
                collection=collection_name,
                limit=limit,
            )

        # Format results as a dictionary
        knowledge = {}
        for item in results:
            # Parse content in format "key: value"
            content = item["content"]
            if ": " in content:
                key, value_str = content.split(": ", 1)

                # Try to parse JSON values
                try:
                    # Check if it's a JSON object or array
                    if (value_str.startswith("{") and value_str.endswith("}")) or \
                       (value_str.startswith("[") and value_str.endswith("]")):
                        value = json.loads(value_str)
                    else:
                        value = value_str
                except json.JSONDecodeError:
                    value = value_str

                knowledge[key.strip()] = value

        return knowledge

    async def import_user_context_memory(
        self,
        data_source: Union[str, Dict[str, Any]],
        user_id: Optional[int] = None,
        format: str = "json",
        source: str = "import",
        importance: float = 0.9,
    ) -> List[str]:
        """
        Import context memory from a file or data structure.

        Args:
            data_source: Path to file or data structure containing knowledge.
            user_id: The user's ID. If None, uses the default user.
            format: Format of the data ("json" or "dict").
            source: Source identifier for the imported knowledge.
            importance: Importance score for this knowledge (0.0 to 1.0).

        Returns:
            List of memory IDs for the added knowledge items.

        Raises:
            ValueError: If the format is unsupported or the data cannot be parsed.
        """
        # Load data based on format
        if format == "json" and isinstance(data_source, str):
            try:
                with open(data_source, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                raise ValueError(f"Failed to load JSON file: {e}")
        elif isinstance(data_source, dict):
            data = data_source
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Add the knowledge
        return await self.add_user_context_memory(
            user_id=user_id,
            knowledge=data,
            source=source,
            importance=importance,
        )

    async def clear_user_context_memory(
        self,
        user_id: Optional[int] = None,
        keys: Optional[List[str]] = None,
    ) -> bool:
        """
        Clear context memory for a specific user.

        Args:
            user_id: The user's ID. If None, uses the default user.
            keys: Optional list of specific knowledge keys to clear.
                If None, clears all context memory.

        Returns:
            True if the operation was successful, False otherwise.
        """
        user_id = user_id if user_id is not None else self.default_user_id

        # Skip memory operations for anonymous users (user_id=0)
        if user_id == 0:
            # Return success for anonymous users (no-op)
            return True

        collection_name = f"{self.CONTEXT_MEMORY_COLLECTION}_{user_id}"

        if keys:
            # Clear specific keys
            for key in keys:
                # Find memories with this key
                filter_params = {
                    "type": self.CONTEXT_MEMORY_TYPE,
                    "key": key,
                    "user_id": user_id,
                }

                results = await self.search(
                    query="",
                    user_id=user_id,
                    additional_filter=filter_params,
                    collection=collection_name,
                    limit=100,  # Set a reasonable limit
                )

                # Delete each memory
                for item in results:
                    if "id" in item:
                        await asyncio.to_thread(
                            self.long_term_memory.delete,
                            memory_id=item["id"],
                        )
        else:
            # Clear all context memory by recreating the collection
            try:
                self.long_term_memory.delete_collection(collection_name)
                self.long_term_memory.create_collection(
                    collection_name,
                    f"Context memory for user {user_id}"
                )
                return True
            except Exception:
                return False

        return True
