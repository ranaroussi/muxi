# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Memory Base - Abstract Memory Interface
# Description:  Base abstract class for all memory implementations
# Role:         Defines the contract that all memory systems must follow
# Usage:        Extended by concrete memory implementations
# Author:       Muxi Framework Team
#
# The memory base module provides the foundation for all memory implementations
# in the Muxi framework. It defines:
#
# 1. BaseMemory Abstract Class
#    - Common interface for all memory implementations
#    - Standardized methods for adding and searching content
#    - Type annotations for consistent usage
#
# 2. Core Memory Operations
#    - Content addition with metadata support
#    - Semantic search functionality
#    - Consistent result formatting
#
# This abstract base class ensures that all memory implementations follow a
# consistent interface, allowing them to be used interchangeably in the framework.
# By defining clear contracts for memory operations, it enables:
#
# - Easy switching between different memory backends
# - Consistent behavior across memory implementations
# - Simplified testing and mocking
# - Clear extension points for custom memory systems
#
# All concrete memory implementations (BufferMemory, LongTermMemory, etc.)
# must inherit from BaseMemory and implement its abstract methods.
#
# Example usage:
#
#   # Creating a concrete memory implementation
#   class MyCustomMemory(BaseMemory):
#       async def add(self, content, metadata=None):
#           # Implementation for adding content
#           ...
#
#       async def search(self, query, limit=5):
#           # Implementation for searching content
#           ...
#
#   # Using memory implementations through the common interface
#   async def use_memory(memory: BaseMemory):
#       await memory.add("Important information", {"source": "user"})
#       results = await memory.search("relevant query")
# =============================================================================

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseMemory(ABC):
    """
    Abstract base class for memory implementations.

    This class defines the core interface that all memory systems in the Muxi
    framework must implement. It provides abstract methods for adding content
    to memory and searching for relevant information, ensuring consistent
    behavior across different memory implementations.

    Memory systems serve as the "memory" for agents, enabling them to:
    - Store and retrieve conversation history
    - Remember important facts and information
    - Search for relevant context based on user queries
    - Maintain state across multiple conversation turns
    """

    @abstractmethod
    async def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add content to memory.

        This method stores new content in the memory system, along with optional
        metadata for additional context. Implementations must handle content storage,
        indexing, and any necessary processing for later retrieval.

        Args:
            content: The text content to add to memory. This is the primary information
                that will be stored and later retrieved via search.
            metadata: Optional key-value pairs providing additional context for the content.
                Common metadata includes timestamps, source information, agent IDs,
                message types, and any other relevant attributes.
        """
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant content in memory.

        This method retrieves content from memory that is relevant to the provided
        query, using whatever search mechanism is appropriate for the implementation
        (e.g., semantic search, keyword matching, recency, etc.).

        Args:
            query: The search query to find relevant content. This could be a question,
                a statement, or any text for which we want to find matching information.
            limit: The maximum number of results to return. Controls the volume of
                information retrieved. Default is 5 items.

        Returns:
            A list of dictionaries containing the retrieved content and metadata.
            Each dictionary should have at least 'content' and 'metadata' keys,
            and may include additional keys such as 'score' or 'relevance' to
            indicate match quality.
        """
        pass
