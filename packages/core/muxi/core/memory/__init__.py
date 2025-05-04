# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Memory Package - Conversation and Knowledge Storage
# Description:  Memory system implementations for the Muxi framework
# Role:         Provides short and long-term storage for agent interactions
# Usage:        Imported by components needing memory capabilities
# Author:       Muxi Framework Team
#
# The memory package provides various memory implementations for storing and
# retrieving information in the Muxi framework. This includes:
#
# 1. Short-Term Memory (BufferMemory)
#    - Stores recent conversation history
#    - Implements semantic search via vector embeddings
#    - Balances recency and relevance for context retrieval
#
# 2. Long-Term Memory (LongTermMemory)
#    - Persistent storage for important information
#    - Uses PostgreSQL with pgvector for scalable vector search
#    - Supports metadata filtering and collection organization
#
# 3. Context Memory
#    - Stores user-specific information and preferences
#    - Enables personalization of agent responses
#    - Structured storage with simple query interface
#
# 4. SQLite-Based Storage
#    - Local-first vector database implementation
#    - Uses SQLite with vector extension for similarity search
#    - Ideal for edge deployments and development environments
#
# 5. Base Abstractions
#    - Common interfaces for all memory implementations
#    - Standardized methods for adding and retrieving information
#    - Extensible design for custom memory implementations
#
# Memory systems are a core component of the framework, enabling agents to:
# - Maintain conversation context across multiple turns
# - Remember important information about users and topics
# - Retrieve relevant information based on semantic similarity
# - Provide personalized and contextually appropriate responses
#
# Example usage:
#
#   # Create a buffer memory for conversation history
#   from muxi.core.memory import BufferMemory
#
#   buffer = BufferMemory(
#       max_size=10,              # Context window size
#       buffer_multiplier=10,     # Total capacity = 10 × 10 = 100
#       model=embedding_model     # For vector search
#   )
#
#   # Add items to memory
#   await buffer.add("User message", {"role": "user"})
#
#   # Search memory for relevant information
#   results = await buffer.search("topic of interest")
# =============================================================================

from muxi.core.memory.base import BaseMemory
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.memory.sqlite import SQLiteMemory
from muxi.core.memory.context_memory import ContextMemory

__all__ = [
    "BaseMemory",
    "BufferMemory",
    "LongTermMemory",
    "Memobase",
    "SQLiteMemory",
    "ContextMemory",
]
