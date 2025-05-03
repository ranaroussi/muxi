"""
Test Knowledge Handler

This module contains tests for the KnowledgeHandler class.
"""

import os
import tempfile
from unittest.mock import AsyncMock

import pytest

from muxi.core.knowledge.base import KnowledgeHandler, KnowledgeSource, FileKnowledge


class TestKnowledgeSource(KnowledgeSource):
    """Test knowledge source implementation."""

    def __init__(self, name="test", description=None, return_value=None):
        super().__init__(name, description)
        self.return_value = return_value or []
        self.retrieve_called = False

    async def retrieve(self, query, limit=5):
        """Mock retrieve implementation."""
        self.retrieve_called = True
        self.last_query = query
        self.last_limit = limit
        return self.return_value


# Tests for KnowledgeHandler
def test_initialization():
    """Test knowledge handler initialization."""
    # Basic initialization with no sources
    handler = KnowledgeHandler()
    assert handler.sources == []

    # Initialization with sources
    source1 = TestKnowledgeSource(name="source1")
    source2 = TestKnowledgeSource(name="source2")
    handler = KnowledgeHandler(sources=[source1, source2])
    assert handler.sources == [source1, source2]


def test_add_source():
    """Test adding a knowledge source."""
    handler = KnowledgeHandler()
    source = TestKnowledgeSource(name="test_source")

    # Add source
    handler.add_source(source)
    assert source in handler.sources
    assert len(handler.sources) == 1


@pytest.mark.asyncio
async def test_retrieve():
    """Test retrieving from knowledge sources."""
    # Create test sources with mock return values
    source1 = TestKnowledgeSource(
        name="source1",
        return_value=[
            {"source": "file1.txt", "content": "Content 1"}
        ]
    )
    source2 = TestKnowledgeSource(
        name="source2",
        return_value=[
            {"source": "file2.txt", "content": "Content 2"},
            {"source": "file3.txt", "content": "Content 3"}
        ]
    )

    # Create handler with both sources
    handler = KnowledgeHandler(sources=[source1, source2])

    # Retrieve from all sources
    results = await handler.retrieve(query="test query", limit_per_source=2)

    # Verify sources were called
    assert source1.retrieve_called
    assert source2.retrieve_called

    # Verify query parameters were passed correctly
    assert source1.last_query == "test query"
    assert source1.last_limit == 2

    # Verify results were aggregated
    assert len(results) == 3

    # Verify metadata was added
    assert results[0]["metadata"]["source_name"] == "source1"
    assert results[1]["metadata"]["source_name"] == "source2"


@pytest.mark.asyncio
async def test_retrieve_with_max_sources():
    """Test retrieving with a limit on number of sources."""
    source1 = TestKnowledgeSource(name="source1", return_value=[{"content": "Content 1"}])
    source2 = TestKnowledgeSource(name="source2", return_value=[{"content": "Content 2"}])
    source3 = TestKnowledgeSource(name="source3", return_value=[{"content": "Content 3"}])

    handler = KnowledgeHandler(sources=[source1, source2, source3])

    # Retrieve from only the first 2 sources
    results = await handler.retrieve(query="test", limit_per_source=1, max_sources=2)

    # Verify only first 2 sources were called
    assert source1.retrieve_called
    assert source2.retrieve_called
    assert not source3.retrieve_called

    # Verify results count
    assert len(results) == 2


@pytest.mark.asyncio
async def test_retrieve_with_error():
    """Test retrieving when a source raises an error."""
    # Create a source that works
    good_source = TestKnowledgeSource(
        name="good",
        return_value=[{"content": "Good content"}]
    )

    # Create a source that fails
    bad_source = TestKnowledgeSource(name="bad")
    bad_source.retrieve = AsyncMock(side_effect=Exception("Test error"))

    handler = KnowledgeHandler(sources=[good_source, bad_source])

    # Should not raise an exception
    results = await handler.retrieve(query="test")

    # Should still return results from the good source
    assert len(results) == 1
    assert results[0]["content"] == "Good content"


@pytest.mark.asyncio
async def test_file_knowledge():
    """Test FileKnowledge source."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("This is test content")
        file_path = temp_file.name

    try:
        # Create FileKnowledge source
        file_source = FileKnowledge(
            name="test_files",
            files=[file_path],
            description="Test file source"
        )

        # Test retrieval
        results = await file_source.retrieve(query="test", limit=1)

        # Verify results
        assert len(results) == 1
        assert results[0]["source"] == file_path
        assert "This is test content" in results[0]["content"]
        assert results[0]["metadata"]["type"] == "file"
        assert results[0]["metadata"]["path"] == file_path
    finally:
        # Clean up temp file
        os.unlink(file_path)
