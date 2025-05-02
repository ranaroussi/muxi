"""
Knowledge module for the MUXI Framework.

This module provides interfaces and implementations for knowledge retrieval and management.
"""

from packages.core.knowledge.base import KnowledgeSource, FileKnowledge, KnowledgeHandler

__all__ = [
    "KnowledgeSource",
    "FileKnowledge",
    "KnowledgeHandler",
]
