"""
Context Memory for User-Specific Information

This module provides a class for managing user-specific context memory
in the MUXI Framework. It allows storing and retrieving personal information
and preferences for individual users to enable personalization.
"""

import json
from typing import Any, Dict, List, Optional, Union


class ContextMemory:
    """
    Context Memory for user-specific information and preferences.

    This class provides methods for managing structured information about users
    that can enhance agent responses with personalization.
    """

    def __init__(self):
        """Initialize the context memory."""
        self.knowledge = {}

    def add(self, data: Dict[str, Any]) -> None:
        """
        Add knowledge to the context memory.

        Args:
            data: Dictionary containing knowledge items
        """
        self.knowledge.update(data)

    def add_from_file(self, filepath: str, format: str = "auto") -> None:
        """
        Add knowledge from a file.

        Args:
            filepath: Path to the file containing knowledge
            format: Format of the file - "auto", "json", "txt"

        Raises:
            ValueError: If the file format is not supported or the file cannot be parsed
        """
        # Determine format if auto
        if format == "auto":
            if filepath.endswith(".json"):
                format = "json"
            elif filepath.endswith(".txt"):
                format = "txt"
            else:
                raise ValueError(f"Cannot automatically determine format for file: {filepath}")

        # Parse file based on format
        if format == "json":
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.add(data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                raise ValueError(f"Failed to load JSON file: {e}")
        elif format == "txt":
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Simple key-value parsing: "key: value"
                    for line in content.split("\n"):
                        line = line.strip()
                        if line and ": " in line:
                            key, value = line.split(": ", 1)
                            self.knowledge[key.strip()] = value.strip()
            except FileNotFoundError as e:
                raise ValueError(f"Failed to load text file: {e}")
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get(self, key: Optional[str] = None) -> Union[Dict[str, Any], Any, None]:
        """
        Get knowledge from the context memory.

        Args:
            key: Optional key to retrieve specific knowledge. If None, returns all knowledge.

        Returns:
            The requested knowledge or None if not found
        """
        if key is None:
            return self.knowledge
        return self.knowledge.get(key)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the context memory with a natural language question.

        This is a simple implementation that returns all knowledge.
        In a more advanced implementation, this would use semantic search.

        Args:
            question: The question to answer

        Returns:
            Dictionary of relevant knowledge items
        """
        # Simple implementation - return all knowledge
        # In a real implementation, this would use semantic search
        return self.knowledge

    def clear(self, keys: Optional[List[str]] = None) -> None:
        """
        Clear knowledge from the context memory.

        Args:
            keys: Optional list of keys to clear. If None, clears all knowledge.
        """
        if keys is None:
            self.knowledge = {}
        else:
            for key in keys:
                if key in self.knowledge:
                    del self.knowledge[key]
