"""
Memory configuration for the AI Agent Framework.

This module provides memory-related configuration settings.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """Memory configuration settings."""

    vector_dimension: int = Field(
        default_factory=lambda: int(os.getenv("VECTOR_DIMENSION", "1536"))
    )

    buffer_max_size: int = Field(
        default_factory=lambda: int(os.getenv("BUFFER_MAX_SIZE", "1000"))
    )

    faiss_index_path: str = Field(
        default_factory=lambda: os.getenv(
            "FAISS_INDEX_PATH",
            str(Path("./data/faiss_index").absolute())
        )
    )

    default_collection: str = Field(
        default_factory=lambda: os.getenv("MEMORY_DEFAULT_COLLECTION", "default")
    )

    similarity_threshold: float = Field(
        default_factory=lambda: float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", "0.7"))
    )

    max_search_results: int = Field(
        default_factory=lambda: int(os.getenv("MEMORY_MAX_SEARCH_RESULTS", "10"))
    )


# Create a global memory config instance
memory_config = MemoryConfig()
