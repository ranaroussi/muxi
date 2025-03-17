"""
Buffer memory implementation.

This module provides a simple buffer memory system for storing recent messages.
"""

from typing import Dict, List, Any, Optional
from collections import deque

from muxi.server.memory.base import BaseMemory


class BufferMemory(BaseMemory):
    """
    A simple buffer memory implementation.

    This class provides a fixed-size buffer for storing recent messages.
    When the buffer is full, the oldest messages are removed.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize the buffer memory.

        Args:
            max_size: The maximum number of messages to store.
        """
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)

    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add content to the memory.

        Args:
            content: The content to add to memory.
            metadata: Optional metadata to associate with the content.
        """
        self.buffer.appendleft({
            "content": content,
            "metadata": metadata or {}
        })

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant content in memory.

        For buffer memory, this simply returns the most recent messages,
        ignoring the query.

        Args:
            query: The query to search for (ignored in buffer memory).
            limit: The maximum number of results to return.

        Returns:
            A list of dictionaries containing the retrieved content and metadata.
        """
        # Return the most recent messages up to the limit
        return list(self.buffer)[:limit]
