"""
Knowledge retriever for the MUXI Framework.

This module provides a retriever class for getting knowledge from various sources.
"""

from typing import Any, Dict, List, Optional

from packages.core.knowledge.base import KnowledgeHandler, KnowledgeSource


class Retriever:
    """
    Retriever for knowledge sources.

    This class provides methods for retrieving knowledge from various sources.
    """

    def __init__(self, sources: Optional[List[KnowledgeSource]] = None):
        """
        Initialize a retriever.

        Args:
            sources: Optional list of knowledge sources
        """
        self.handler = KnowledgeHandler(sources=sources)

    def add_source(self, source: KnowledgeSource) -> None:
        """
        Add a knowledge source.

        Args:
            source: The knowledge source to add
        """
        self.handler.add_source(source)

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
        return await self.handler.retrieve(
            query=query,
            limit_per_source=limit_per_source,
            max_sources=max_sources
        )
