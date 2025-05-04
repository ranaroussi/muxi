# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Context Memory - Window-Based Memory System
# Description:  Simple context window memory system for conversation history
# Role:         Provides basic memory for storing recent conversation context
# Usage:        Used for maintaining recency-based conversational context
# Author:       Muxi Framework Team
#
# The Context Memory module provides a simple, recency-based memory system
# for the Muxi Framework. It implements a sliding window approach to maintain
# the most recent conversation history without the complexity of vector
# embeddings or semantic search.
#
# Key features include:
#
# 1. Simple Window Memory
#    - Fixed-size memory window based on message count
#    - FIFO (First In, First Out) message management
#    - No vector storage or embeddings required
#
# 2. Metadata Support
#    - Associate metadata with each stored message
#    - Filter retrieval based on metadata criteria
#
# 3. Lightweight Implementation
#    - Efficient storage with minimal overhead
#    - No external dependencies required
#    - Fast retrieval operations
#
# This memory implementation is suitable for simple agents where
# semantic search isn't needed, or as a fallback when embeddings
# aren't available.
# =============================================================================

from collections import deque
from typing import Any, Dict, List, Optional

from .base import BaseMemory


class ContextMemory(BaseMemory):
    """
    Simple context window memory implementation for conversation history.

    This implementation maintains a fixed-size sliding window of the most recent
    messages. It provides a simple FIFO (First In, First Out) approach to memory
    management, where older messages are dropped when the window size is exceeded.

    Unlike more sophisticated memory implementations, ContextMemory doesn't use
    vector embeddings or semantic search, making it lightweight but limited to
    recency-based recall.
    """

    def __init__(self, max_size: int = 10):
        """
        Initialize a new context window memory.

        Args:
            max_size: Maximum number of items to keep in the memory window.
                When this limit is reached, older items are removed to make
                room for new ones. Default is 10 messages.
        """
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)

    async def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add content to the context memory.

        Adds a new item to the memory window, along with optional metadata.
        If the window is full, the oldest item will be removed.

        Args:
            content: The text content to add to memory.
            metadata: Optional key-value pairs for filtering and context.
                Common metadata includes timestamps, message types, and
                user/session identifiers.
        """
        self.buffer.append({"content": content, "metadata": metadata or {}})

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent items from context memory.

        This implementation doesn't perform actual search - it simply returns
        the most recent items in the memory window, up to the specified limit.
        No semantic matching or relevance scoring is performed.

        Args:
            query: Ignored in this implementation since no semantic search is performed.
            limit: Maximum number of results to return, starting from most recent.
                Default is 5 items.

        Returns:
            A list of dictionaries containing the content and metadata of the
            most recent items, ordered from newest to oldest.
        """
        # Return the most recent 'limit' items
        return list(reversed([item for item in list(self.buffer)[-limit:]]))

    def clear(self) -> None:
        """
        Clear all items from the context memory.

        Removes all content from the memory window, effectively resetting
        the memory to an empty state.
        """
        self.buffer.clear()

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all items currently in the context memory.

        Returns:
            A list of all items in the memory window, ordered from oldest to newest.
        """
        return list(self.buffer)

    def get_size(self) -> int:
        """
        Get the current number of items in the context memory.

        Returns:
            The current number of items stored in the memory window.
        """
        return len(self.buffer)
