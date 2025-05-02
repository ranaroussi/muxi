"""
Knowledge base module for MUXI Framework.

This module provides classes for handling agent-level knowledge.
"""

from typing import Any, Dict, List, Optional


class KnowledgeSource:
    """
    Base class for knowledge sources that can be integrated with agents.

    Knowledge sources provide relevant information to augment agent responses.
    """

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a knowledge source.

        Args:
            name: A unique name for this knowledge source
            description: Optional description of this knowledge source
        """
        self.name = name
        self.description = description or f"Knowledge source: {name}"

    async def retrieve(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information based on a query.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            List of retrieved knowledge items
        """
        raise NotImplementedError("Subclasses must implement retrieve()")


class FileKnowledge(KnowledgeSource):
    """
    Simple knowledge source that retrieves information from files.
    """

    def __init__(self, name: str, files: List[str], description: Optional[str] = None):
        """
        Initialize a file-based knowledge source.

        Args:
            name: A unique name for this knowledge source
            files: List of file paths to use as knowledge sources
            description: Optional description of this knowledge source
        """
        super().__init__(name, description)
        self.files = files

    async def retrieve(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information from files based on a query.

        This is a simple implementation that just returns the file contents.
        A real implementation would use vector search or other techniques.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            List of retrieved knowledge items
        """
        results = []

        for file_path in self.files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                results.append({
                    "source": file_path,
                    "content": content,
                    "metadata": {
                        "type": "file",
                        "path": file_path,
                        "size": len(content)
                    }
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")

        return results


class KnowledgeHandler:
    """
    Manager for multiple knowledge sources.

    This class allows an agent to use multiple knowledge sources and
    aggregate results.
    """

    def __init__(self, sources: Optional[List[KnowledgeSource]] = None):
        """
        Initialize a knowledge handler.

        Args:
            sources: Optional list of knowledge sources
        """
        self.sources = sources or []

    def add_source(self, source: KnowledgeSource) -> None:
        """
        Add a knowledge source.

        Args:
            source: The knowledge source to add
        """
        self.sources.append(source)

    async def retrieve(
        self,
        query: str,
        limit_per_source: int = 3,
        max_sources: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve information from all knowledge sources.

        Args:
            query: The search query
            limit_per_source: Maximum number of results per source
            max_sources: Maximum number of sources to query (None for all)

        Returns:
            List of retrieved knowledge items from all sources
        """
        results = []

        # Limit the number of sources if specified
        sources = self.sources
        if max_sources is not None:
            sources = sources[:max_sources]

        # Query each source
        for source in sources:
            try:
                source_results = await source.retrieve(query, limit=limit_per_source)

                # Add source information to each result
                for result in source_results:
                    if "metadata" not in result:
                        result["metadata"] = {}

                    result["metadata"]["source_name"] = source.name
                    result["metadata"]["source_description"] = source.description

                results.extend(source_results)
            except Exception as e:
                print(f"Error retrieving from source {source.name}: {str(e)}")

        return results
