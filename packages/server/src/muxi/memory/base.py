"""
Base memory implementations.

This module provides the base abstract class for memory implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseMemory(ABC):
    """
    Abstract base class for memory implementations.

    Memory implementations should provide methods for adding content to memory
    and searching for relevant content.
    """

    @abstractmethod
    async def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add content to memory.

        Args:
            content: The content to add to memory.
            metadata: Optional metadata to associate with the content.
        """
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant content in memory.

        Args:
            query: The query to search for.
            limit: The maximum number of results to return.

        Returns:
            A list of dictionaries containing the retrieved content and metadata.
            Each dictionary should have at least 'content' and 'metadata' keys.
        """
        pass
