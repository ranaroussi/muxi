# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Knowledge Package - External Information Integration
# Description:  Framework for integrating external knowledge with agents
# Role:         Augments agent capabilities with domain-specific knowledge
# Usage:        Used to provide agents with access to external information sources
# Author:       Muxi Framework Team
#
# The knowledge package provides mechanisms for integrating external knowledge
# sources with Muxi agents. This allows agents to access, retrieve, and leverage
# information beyond their training data, including:
#
# 1. Knowledge Source Interface
#    - Abstract base classes for knowledge source implementations
#    - Standardized retrieval and integration patterns
#    - Pluggable architecture for different knowledge types
#
# 2. File-Based Knowledge
#    - Simple implementation for retrieving information from local files
#    - Supports various file formats including text, markdown, and JSON
#    - Useful for static documentation and reference materials
#
# 3. Knowledge Handlers
#    - Coordination layer for multiple knowledge sources
#    - Result aggregation and filtering
#    - Metadata enrichment and source attribution
#
# Knowledge integration significantly enhances agent capabilities by:
# - Providing access to domain-specific information
# - Reducing hallucination through grounded responses
# - Enabling agents to stay current with the latest information
# - Supporting references and citations in responses
#
# Example usage:
#
#   # Create knowledge sources
#   docs = FileKnowledge(
#       name="documentation",
#       files=["docs/api.md", "docs/usage.md"],
#       description="Product documentation files"
#   )
#
#   # Create a knowledge handler with the sources
#   handler = KnowledgeHandler([docs])
#
#   # Retrieve relevant information
#   results = await handler.retrieve(
#       query="How do I configure the API?",
#       limit_per_source=3
#   )
# =============================================================================


from muxi.core.knowledge.base import KnowledgeSource, FileKnowledge, KnowledgeHandler

__all__ = [
    "KnowledgeSource",
    "FileKnowledge",
    "KnowledgeHandler",
]
