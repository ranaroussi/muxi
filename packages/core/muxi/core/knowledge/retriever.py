# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Knowledge Retriever - Agent Knowledge Access Interface
# Description:  Streamlined interface for retrieving information from knowledge sources
# Role:         Provides a simplified API for agent knowledge access
# Usage:        Used by agents to retrieve information from multiple knowledge sources
# Author:       Muxi Framework Team
#
# The Knowledge Retriever module provides a simplified interface for retrieving
# information from knowledge sources. It serves as a convenience layer on top of
# the KnowledgeHandler, making it easier for agents to access external knowledge.
# Key features include:
#
# 1. Simplified API
#    - Clean interface optimized for agent integration
#    - Handles the complexity of knowledge source management
#    - Provides sensible defaults for common operations
#
# 2. Dynamic Source Management
#    - Add sources at runtime as needed
#    - Transparently handles source initialization
#    - Works with any implementation of KnowledgeSource
#
# 3. Result Standardization
#    - Consistent result format across different knowledge sources
#    - Metadata enrichment for source attribution
#    - Configurable result limiting and filtering
#
# The Retriever class is typically used by agents to fetch relevant information
# when responding to user queries. It helps ground agent responses in factual
# information from trusted sources rather than relying solely on model training data.
#
# Example usage:
#
#   # Create a retriever with initial sources
#   docs_source = FileKnowledge("docs", ["api.md", "faq.md"])
#   retriever = Retriever([docs_source])
#
#   # Add additional sources as needed
#   kb_source = VectorKnowledge("knowledge_base", "kb.sqlite")
#   retriever.add_source(kb_source)
#
#   # Retrieve information for a query
#   results = await retriever.retrieve(
#       query="How do I reset my password?",
#       limit_per_source=3
#   )
# =============================================================================

from typing import Any, Dict, List, Optional

from muxi.core.knowledge.base import KnowledgeHandler, KnowledgeSource


class Retriever:
    """
    Retriever for knowledge sources.

    The Retriever provides a simplified interface for retrieving information from
    multiple knowledge sources. It serves as a convenience layer on top of the
    KnowledgeHandler, making it easier for agents to access external knowledge
    without dealing with the complexities of source management.
    """

    def __init__(self, sources: Optional[List[KnowledgeSource]] = None):
        """
        Initialize a retriever with optional knowledge sources.

        Args:
            sources: Optional list of knowledge sources to start with. Sources can
                be any implementation of the KnowledgeSource interface. If None, an
                empty list is used, and sources can be added later with add_source().
        """
        self.handler = KnowledgeHandler(sources=sources)

    def add_source(self, source: KnowledgeSource) -> None:
        """
        Add a knowledge source to the retriever.

        This method allows dynamically adding new knowledge sources after
        the retriever has been initialized, enabling flexible source management
        as application needs evolve.

        Args:
            source: The knowledge source to add. Must be an instance of
                KnowledgeSource or a subclass that implements the retrieve() method.
        """
        self.handler.add_source(source)

    async def retrieve(
        self, query: str, limit_per_source: int = 3, max_sources: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve information from all knowledge sources based on a query.

        This method queries all registered knowledge sources and aggregates
        their results into a single list. It handles error isolation, ensuring
        that failures in one source don't affect others.

        Args:
            query: The search query to send to all knowledge sources. This should
                be a question or keyword phrase that will be used to find relevant
                information across all sources.
            limit_per_source: Maximum number of results to retrieve from each source.
                Controls the total volume of information by limiting each source's
                contribution. Default is 3 results per source.
            max_sources: Maximum number of sources to query. If None, all registered
                sources are queried. If specified, only the first 'max_sources'
                sources are used.

        Returns:
            A list of dictionaries containing the retrieved information from all sources.
            Each dictionary includes source identification metadata, allowing for
            attribution and result organization.
        """
        return await self.handler.retrieve(
            query=query, limit_per_source=limit_per_source, max_sources=max_sources
        )
