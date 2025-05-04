# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Knowledge Base - External Knowledge Integration
# Description:  Base classes for agent knowledge source integration
# Role:         Provides knowledge retrieval capabilities to agents
# Usage:        Used to augment agent responses with external information
# Author:       Muxi Framework Team
#
# The knowledge base module provides the foundation for integrating external
# knowledge sources with agents in the Muxi framework. It includes:
#
# 1. Abstract Knowledge Source Interface
#    - Defines the contract for all knowledge source implementations
#    - Standardizes information retrieval methods
#    - Supports metadata for source tracking and attribution
#
# 2. File-Based Knowledge Implementation
#    - Simple implementation using local files as knowledge sources
#    - Demonstrates the pattern for creating knowledge source implementations
#    - Serves as a reference for more sophisticated implementations
#
# 3. Knowledge Handler
#    - Manages multiple knowledge sources
#    - Aggregates and merges results from different sources
#    - Provides unified access to all knowledge sources
#
# Knowledge sources are typically integrated with agents through the Orchestrator,
# which manages access and coordinates knowledge retrieval.
#
# Example usage:
#
#   # Create knowledge sources
#   product_docs = FileKnowledge(
#       name="product_docs",
#       files=["docs/api.md", "docs/usage.md"],
#       description="Product documentation files"
#   )
#
#   # Create a knowledge handler
#   handler = KnowledgeHandler([product_docs])
#
#   # Add additional sources
#   handler.add_source(VectorKnowledge("embeddings_db", "db.sqlite"))
#
#   # Retrieve knowledge
#   results = await handler.retrieve(
#       query="How do I configure the API?",
#       limit_per_source=3
#   )
#
# More sophisticated implementations would include vector databases,
# API connectors, or other specialized knowledge sources.
# =============================================================================

from typing import Any, Dict, List, Optional


class KnowledgeSource:
    """
    Base class for knowledge sources that can be integrated with agents.

    Knowledge sources provide relevant information to augment agent responses.
    This abstract base class defines the contract that all knowledge source
    implementations must follow, ensuring consistent behavior across different
    types of knowledge sources.
    """

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a knowledge source.

        Args:
            name: A unique name for this knowledge source. Used for identification
                and reference in logs and debugging.
            description: Optional description of this knowledge source. Provides
                human-readable context about the source. If not provided, a default
                description is generated from the name.
        """
        self.name = name
        self.description = description or f"Knowledge source: {name}"

    async def retrieve(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information based on a query.

        This is an abstract method that must be implemented by subclasses.
        Each implementation should search its knowledge source and return
        relevant information matching the query.

        Args:
            query: The search query. This is typically a question or keyword
                phrase that should be used to find relevant information.
            limit: Maximum number of results to return. Controls the volume of
                information retrieved from this source.

        Returns:
            List of retrieved knowledge items. Each item should be a dictionary with
            at least 'source' and 'content' keys, and optionally 'metadata'.

        Raises:
            NotImplementedError: This base method raises an error since it must
                be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement retrieve()")


class FileKnowledge(KnowledgeSource):
    """
    Simple knowledge source that retrieves information from files.

    This implementation reads content directly from files on disk. It serves
    as a basic example of a knowledge source implementation and is useful for
    development and testing scenarios where sophisticated retrieval is not required.
    """

    def __init__(self, name: str, files: List[str], description: Optional[str] = None):
        """
        Initialize a file-based knowledge source.

        Args:
            name: A unique name for this knowledge source. Used for identification
                and reference in logs and debugging.
            files: List of file paths to use as knowledge sources. These should be
                valid paths to accessible text files containing the knowledge content.
            description: Optional description of this knowledge source. Provides
                human-readable context about what these files contain.
        """
        super().__init__(name, description)
        self.files = files

    async def retrieve(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information from files based on a query.

        This is a simple implementation that just returns the file contents without
        any sophisticated search or ranking. In a production implementation, this would
        typically use vector search, indexing, or other techniques to find the most
        relevant parts of the files.

        Args:
            query: The search query. In this simple implementation, the query is not
                actually used for filtering, but is required by the interface.
            limit: Maximum number of files to return. If there are more files than
                this limit, only the first 'limit' files are processed.

        Returns:
            List of retrieved knowledge items. Each item includes:
            - source: The file path
            - content: The entire file contents
            - metadata: Additional information including file type, path, and size
        """
        results = []

        for file_path in self.files[:limit]:
            try:
                # Read the entire file contents
                with open(file_path, "r") as f:
                    content = f.read()

                # Create a result item with file information
                results.append(
                    {
                        "source": file_path,
                        "content": content,
                        "metadata": {"type": "file", "path": file_path, "size": len(content)},
                    }
                )
            except Exception as e:
                # Log errors but continue processing other files
                print(f"Error reading file {file_path}: {str(e)}")

        return results


class KnowledgeHandler:
    """
    Manager for multiple knowledge sources.

    This class aggregates results from multiple knowledge sources, providing
    a unified interface for retrieving information from all available sources.
    It handles error isolation, ensuring that failures in one source don't
    affect others, and manages source identification and attribution.
    """

    def __init__(self, sources: Optional[List[KnowledgeSource]] = None):
        """
        Initialize a knowledge handler.

        Args:
            sources: Optional list of knowledge sources to manage. If None,
                an empty list is created, and sources can be added later with
                add_source().
        """
        self.sources = sources or []

    def add_source(self, source: KnowledgeSource) -> None:
        """
        Add a knowledge source to this handler.

        This method allows dynamically adding new knowledge sources after
        the handler has been initialized.

        Args:
            source: The knowledge source to add. Must be an instance of
                KnowledgeSource or a subclass.
        """
        self.sources.append(source)

    async def retrieve(
        self, query: str, limit_per_source: int = 3, max_sources: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve information from all knowledge sources.

        This method queries all registered knowledge sources and aggregates
        their results into a single list. It handles errors in individual
        sources gracefully, ensuring that a failure in one source doesn't
        prevent results from other sources.

        Args:
            query: The search query to send to all knowledge sources. This should
                be a question or keyword phrase that will be used to find relevant
                information across all sources.
            limit_per_source: Maximum number of results to retrieve from each source.
                Controls the total volume of information by limiting each source's
                contribution.
            max_sources: Maximum number of sources to query. If None, all registered
                sources are queried. If specified, only the first 'max_sources'
                sources are used.

        Returns:
            List of retrieved knowledge items from all sources, each enriched with
            metadata identifying its source. The format matches the KnowledgeSource
            retrieve() method, with additional source identification metadata.
        """
        results = []

        # Limit the number of sources if specified
        sources = self.sources
        if max_sources is not None:
            sources = sources[:max_sources]

        # Query each source
        for source in sources:
            try:
                # Retrieve results from this source
                source_results = await source.retrieve(query, limit=limit_per_source)

                # Add source information to each result for attribution
                for result in source_results:
                    if "metadata" not in result:
                        result["metadata"] = {}

                    # Tag each result with its source information
                    result["metadata"]["source_name"] = source.name
                    result["metadata"]["source_description"] = source.description

                # Add this source's results to the combined results
                results.extend(source_results)
            except Exception as e:
                # Log errors but continue processing other sources
                print(f"Error retrieving from source {source.name}: {str(e)}")

        return results
