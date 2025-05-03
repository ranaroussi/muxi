"""
Test Agent Knowledge

This module contains tests for the knowledge functionality of the Agent class.
"""

from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from muxi.core.agent import Agent


# Fixtures
@pytest.fixture
def agent_setup():
    """Set up test fixtures."""
    # Create mock objects for dependencies
    mock_model = MagicMock()
    mock_buffer_memory = MagicMock()

    # Create mock orchestrator
    mock_orchestrator = MagicMock()
    mock_orchestrator.buffer_memory = mock_buffer_memory

    # Mock embedding functions
    mock_model.embed = AsyncMock()
    mock_model.embed.return_value = [0.1] * 1536  # Mock embedding of dimension 1536

    mock_model.generate_embeddings = AsyncMock()
    mock_model.generate_embeddings.return_value = [
        [0.1] * 1536 for _ in range(3)
    ]  # 3 mock embeddings

    # Create agent with mock dependencies
    agent = Agent(model=mock_model, orchestrator=mock_orchestrator)

    # Create test file content
    test_file_content = (
        "This is a test file for knowledge testing.\n"
        "It contains information about testing knowledge functionality.\n"
        "MUXI Framework allows agents to use knowledge sources."
    )

    return agent, mock_model, mock_buffer_memory, test_file_content


# Tests
@pytest.mark.asyncio
@patch("muxi.core.knowledge.handler.KnowledgeHandler")
async def test_initialize_knowledge(mock_knowledge_handler_class, agent_setup):
    """Test initializing knowledge in agent."""
    # Skip this test as the Agent class doesn't have knowledge initialization anymore
    pytest.skip("Agent class no longer has knowledge initialization")


@pytest.mark.asyncio
@patch("os.path.exists")
@patch("os.path.getmtime")
@patch("builtins.open", new_callable=mock_open, read_data="Test content")
async def test_add_knowledge(mock_file, mock_getmtime, mock_exists, agent_setup):
    """Test adding a knowledge source."""
    # Skip this test as the Agent class doesn't have add_knowledge anymore
    pytest.skip("Agent class no longer has add_knowledge method")


@pytest.mark.asyncio
async def test_add_knowledge_initializes_handler(agent_setup):
    """Test adding knowledge initializes handler if not already created."""
    # Skip this test as the Agent class doesn't have add_knowledge anymore
    pytest.skip("Agent class no longer has add_knowledge method")


@pytest.mark.asyncio
async def test_remove_knowledge(agent_setup):
    """Test removing a knowledge source."""
    # Skip this test as the Agent class doesn't have remove_knowledge anymore
    pytest.skip("Agent class no longer has remove_knowledge method")


@pytest.mark.asyncio
async def test_remove_knowledge_without_handler(agent_setup):
    """Test removing knowledge when no handler exists."""
    # Skip this test as the Agent class doesn't have remove_knowledge anymore
    pytest.skip("Agent class no longer has remove_knowledge method")


def test_get_knowledge_sources(agent_setup):
    """Test getting knowledge sources."""
    # Skip this test as the Agent class doesn't have get_knowledge_sources anymore
    pytest.skip("Agent class no longer has get_knowledge_sources method")


def test_get_knowledge_sources_without_handler(agent_setup):
    """Test getting knowledge sources when no handler exists."""
    # Skip this test as the Agent class doesn't have get_knowledge_sources anymore
    pytest.skip("Agent class no longer has get_knowledge_sources method")


@pytest.mark.asyncio
async def test_search_knowledge(agent_setup):
    """Test searching knowledge."""
    # Skip this test as the Agent class doesn't have search_knowledge anymore
    pytest.skip("Agent class no longer has search_knowledge method")


@pytest.mark.asyncio
async def test_search_knowledge_without_handler(agent_setup):
    """Test searching knowledge when no handler exists."""
    # Skip this test as the Agent class doesn't have search_knowledge anymore
    pytest.skip("Agent class no longer has search_knowledge method")


@pytest.mark.asyncio
@patch("muxi.core.knowledge.handler.KnowledgeHandler")
@patch("muxi.core.knowledge.base.FileKnowledge")
async def test_integration_with_real_file(
    mock_file_knowledge_class, mock_knowledge_handler_class, agent_setup
):
    """Test integration with a real file."""
    # Skip this test as the Agent class doesn't have knowledge functionality anymore
    pytest.skip("Agent class no longer has knowledge integration")
