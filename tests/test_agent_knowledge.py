"""
Test Agent Knowledge

This module contains tests for the knowledge functionality of the Agent class.
"""

import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from muxi.core.agent import Agent
from muxi.knowledge.base import FileKnowledge


# Fixtures
@pytest.fixture
def agent_setup():
    """Set up test fixtures."""
    # Create mock objects for dependencies
    mock_model = MagicMock()
    mock_buffer_memory = MagicMock()

    # Mock embedding functions
    mock_model.embed = AsyncMock()
    mock_model.embed.return_value = [0.1] * 1536  # Mock embedding of dimension 1536

    mock_model.generate_embeddings = AsyncMock()
    mock_model.generate_embeddings.return_value = [
        [0.1] * 1536 for _ in range(3)]  # 3 mock embeddings

    # Create agent with mock dependencies
    agent = Agent(
        model=mock_model,
        buffer_memory=mock_buffer_memory
    )

    # Create temporary files for testing
    test_file_content = (
        "This is a test file for knowledge testing.\n"
        "It contains information about testing knowledge functionality.\n"
        "MUXI Framework allows agents to use knowledge sources."
    )

    return {
        "agent": agent,
        "mock_model": mock_model,
        "mock_buffer_memory": mock_buffer_memory,
        "test_file_content": test_file_content
    }


# Tests
@pytest.mark.asyncio
@patch('muxi.knowledge.base.KnowledgeHandler')
async def test_initialize_knowledge(mock_knowledge_handler_class, agent_setup):
    """Test initializing knowledge in agent."""
    agent = agent_setup["agent"]
    mock_model = agent_setup["mock_model"]

    # Setup mock
    mock_handler = MagicMock()
    # Set up add_file to return a coroutine that returns 3
    mock_handler.add_file = AsyncMock(return_value=3)
    mock_knowledge_handler_class.return_value = mock_handler

    # Create test knowledge source
    test_source = FileKnowledge(path="/path/to/test.txt", description="Test file")

    # Initialize knowledge
    await agent._initialize_knowledge([test_source])

    # Verify model was used to get embedding dimension
    mock_model.embed.assert_called_once()

    # Verify knowledge handler was created with correct parameters
    mock_knowledge_handler_class.assert_called_once()
    assert agent.knowledge_handler == mock_handler

    # Verify knowledge source was added
    mock_handler.add_file.assert_called_once()


@pytest.mark.asyncio
@patch('muxi.knowledge.base.os.path.exists')
@patch('muxi.knowledge.base.os.path.getmtime')
@patch('builtins.open', new_callable=mock_open, read_data="Test content")
async def test_add_knowledge(mock_file, mock_getmtime, mock_exists, agent_setup):
    """Test adding a knowledge source."""
    agent = agent_setup["agent"]
    mock_model = agent_setup["mock_model"]

    # Setup mocks
    mock_exists.return_value = True
    mock_getmtime.return_value = 12345

    # Create a mock knowledge handler
    agent.knowledge_handler = MagicMock()
    agent.knowledge_handler.add_file = AsyncMock(return_value=3)  # 3 chunks added

    # Create test knowledge source
    test_source = FileKnowledge(path="/path/to/test.txt", description="Test file")

    # Add knowledge
    chunks_added = await agent.add_knowledge(test_source)

    # Verify knowledge was added
    agent.knowledge_handler.add_file.assert_called_once_with(
        test_source, mock_model.generate_embeddings
    )
    assert chunks_added == 3


@pytest.mark.asyncio
async def test_add_knowledge_initializes_handler(agent_setup):
    """Test adding knowledge initializes handler if not already created."""
    agent = agent_setup["agent"]

    # Ensure no handler exists initially
    agent.knowledge_handler = None

    # Create test knowledge source
    test_source = FileKnowledge(path="/path/to/test.txt", description="Test file")

    # Patch KnowledgeHandler class
    with patch('muxi.knowledge.base.KnowledgeHandler') as mock_handler_class:
        # Setup mock handler
        mock_handler = MagicMock()
        mock_handler.add_file = AsyncMock(return_value=0)
        mock_handler_class.return_value = mock_handler

        # Add knowledge
        await agent.add_knowledge(test_source)

        # Verify handler was created
        mock_handler_class.assert_called_once_with(agent.agent_id)
        assert agent.knowledge_handler == mock_handler


@pytest.mark.asyncio
async def test_remove_knowledge(agent_setup):
    """Test removing a knowledge source."""
    agent = agent_setup["agent"]

    # Create a mock knowledge handler
    agent.knowledge_handler = MagicMock()
    agent.knowledge_handler.remove_file = AsyncMock(return_value=True)

    # Remove knowledge
    result = await agent.remove_knowledge("/path/to/test.txt")

    # Verify knowledge was removed
    agent.knowledge_handler.remove_file.assert_called_once_with("/path/to/test.txt")
    assert result is True


@pytest.mark.asyncio
async def test_remove_knowledge_without_handler(agent_setup):
    """Test removing knowledge when no handler exists."""
    agent = agent_setup["agent"]

    # Ensure no handler exists
    agent.knowledge_handler = None

    # Remove knowledge should return False
    result = await agent.remove_knowledge("/path/to/test.txt")
    assert result is False


def test_get_knowledge_sources(agent_setup):
    """Test getting knowledge sources."""
    agent = agent_setup["agent"]

    # Create a mock knowledge handler
    agent.knowledge_handler = MagicMock()
    agent.knowledge_handler.get_sources.return_value = [
        "/path/to/test1.txt", "/path/to/test2.txt"]

    # Get sources
    sources = agent.get_knowledge_sources()

    # Verify sources were retrieved
    agent.knowledge_handler.get_sources.assert_called_once()
    assert sources == ["/path/to/test1.txt", "/path/to/test2.txt"]


def test_get_knowledge_sources_without_handler(agent_setup):
    """Test getting knowledge sources when no handler exists."""
    agent = agent_setup["agent"]

    # Ensure no handler exists
    agent.knowledge_handler = None

    # Get sources should return empty list
    sources = agent.get_knowledge_sources()
    assert sources == []


@pytest.mark.asyncio
async def test_search_knowledge(agent_setup):
    """Test searching knowledge."""
    agent = agent_setup["agent"]
    mock_model = agent_setup["mock_model"]

    # Create mock search results
    mock_results = [
        {"content": "Result 1", "source": "/path/to/test.txt", "relevance": 0.85},
        {"content": "Result 2", "source": "/path/to/test.txt", "relevance": 0.75}
    ]

    # Create a mock knowledge handler
    agent.knowledge_handler = MagicMock()
    agent.knowledge_handler.search = AsyncMock(return_value=mock_results)

    # Search knowledge
    results = await agent.search_knowledge("test query", 2, 0.7)

    # Verify search was performed
    agent.knowledge_handler.search.assert_called_once_with(
        "test query", mock_model.generate_embeddings, 2, 0.7
    )
    assert results == mock_results


@pytest.mark.asyncio
async def test_search_knowledge_without_handler(agent_setup):
    """Test searching knowledge when no handler exists."""
    agent = agent_setup["agent"]

    # Ensure no handler exists
    agent.knowledge_handler = None

    # Search should return empty list
    results = await agent.search_knowledge("test query")
    assert results == []


@pytest.mark.asyncio
@patch('muxi.knowledge.base.KnowledgeHandler')
@patch('muxi.knowledge.base.FileKnowledge')
async def test_integration_with_real_file(mock_file_knowledge_class, mock_knowledge_handler_class, agent_setup):
    """Test integration with a real file."""
    agent = agent_setup["agent"]
    test_file_content = agent_setup["test_file_content"]

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(test_file_content)

    try:
        # Setup mock file knowledge to use the real file
        mock_file_instance = MagicMock()
        mock_file_instance.path = temp_file.name
        mock_file_knowledge_class.return_value = mock_file_instance

        # Setup mock knowledge handler
        mock_handler = MagicMock()
        mock_handler.add_file = AsyncMock(return_value=3)
        mock_handler.search = AsyncMock(return_value=[
            {"content": "MUXI Framework allows agents to use knowledge sources.",
             "source": temp_file.name,
             "relevance": 0.9}
        ])
        mock_knowledge_handler_class.return_value = mock_handler

        # Initialize the agent with knowledge
        agent.knowledge_handler = mock_handler

        # Search for relevant information
        results = await agent.search_knowledge("MUXI knowledge")

        # Verify search was performed
        mock_handler.search.assert_called_once()
        assert len(results) == 1
        assert results[0]["source"] == temp_file.name
        assert "MUXI Framework" in results[0]["content"]

    finally:
        # Clean up temporary file
        os.unlink(temp_file.name)
