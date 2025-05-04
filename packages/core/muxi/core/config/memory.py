# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Memory Configuration - Framework Memory Settings
# Description:  Configuration for memory systems in the Muxi Framework
# Role:         Provides settings for buffer and long-term memory components
# Usage:        Imported by memory components for configuration
# Author:       Muxi Framework Team
#
# The Memory Configuration module provides centralized settings for the memory
# systems in the Muxi Framework. It defines parameters for both buffer memory
# (short-term conversation context) and long-term memory storage.
#
# Key features include:
#
# 1. Buffer Memory Configuration
#    - Buffer size limits
#    - Vector dimensions for embeddings
#    - Maximum size constraints
#
# 2. Long-Term Memory Settings
#    - Enable/disable toggle
#    - Storage location configuration
#    - Search parameters
#
# 3. Vector Storage Settings
#    - FAISS index configuration
#    - Default collection management
#    - Similarity thresholds
#
# Example usage:
#
#   from muxi.core.config import memory_config
#
#   # Access memory configuration
#   vector_dim = memory_config.vector_dimension
#   similarity = memory_config.similarity_threshold
# =============================================================================

import os
from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """
    Memory configuration settings for the Muxi Framework.

    This class defines parameters for both short-term buffer memory and
    long-term persistent memory. It uses Pydantic for validation and type
    safety, with all settings configurable via environment variables.
    """

    use_long_term: Union[bool, str] = Field(
        default_factory=lambda: os.getenv("USE_LONG_TERM_MEMORY", "true").lower() == "true",
        description="Enable long-term memory. Can be boolean or path to SQLite DB/Postgres URL",
    )

    vector_dimension: int = Field(
        default_factory=lambda: int(os.getenv("VECTOR_DIMENSION", "1536")),
        description="Dimension of vector embeddings (matches OpenAI embedding models)",
    )

    buffer_max_size: int = Field(
        default_factory=lambda: int(os.getenv("BUFFER_MAX_SIZE", "1000")),
        description="Maximum number of items to store in buffer memory",
    )

    faiss_index_path: str = Field(
        default_factory=lambda: os.getenv(
            "FAISS_INDEX_PATH", str(Path("./data/faiss_index").absolute())
        ),
        description="Path where FAISS indexes are stored for vector similarity search",
    )

    default_collection: str = Field(
        default_factory=lambda: os.getenv("MEMORY_DEFAULT_COLLECTION", "default"),
        description="Default collection name for memory storage",
    )

    similarity_threshold: float = Field(
        default_factory=lambda: float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", "0.7")),
        description="Minimum similarity score (0-1) for memory retrieval results",
    )

    max_search_results: int = Field(
        default_factory=lambda: int(os.getenv("MEMORY_MAX_SEARCH_RESULTS", "10")),
        description="Maximum number of results to return from memory searches",
    )


# Create a global memory config instance for easy imports
memory_config = MemoryConfig()
