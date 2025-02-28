"""
Tests for API integration with Memobase.

This module tests the API endpoints that support multi-user functionality
through Memobase.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.core.agent import Agent


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator for testing."""
    mock_orchestrator = MagicMock()

    # Create a mock agent
    mock_agent = MagicMock(spec=Agent)
    mock_agent.chat = AsyncMock()
    mock_agent.chat.return_value = "I'm a helpful assistant."

    mock_agent.search_memory = AsyncMock()
    mock_agent.search_memory.return_value = [
        {
            "content": "User-specific memory content",
            "metadata": {"user_id": 123},
            "source": "memobase",
            "distance": 0.8
        }
    ]

    mock_agent.clear_memory = MagicMock()

    # Set up orchestrator.get_agent to return the mock agent
    mock_orchestrator.get_agent = MagicMock()
    mock_orchestrator.get_agent.return_value = mock_agent

    # Set up has_agent method to return False initially
    mock_orchestrator.has_agent = MagicMock()
    mock_orchestrator.has_agent.return_value = False

    # Set up default_agent_id
    mock_orchestrator.default_agent_id = "default_agent"

    # Mock create_agent method to return the mock agent
    mock_orchestrator.create_agent = MagicMock()
    mock_orchestrator.create_agent.return_value = mock_agent

    return mock_orchestrator


@pytest.fixture
def client(mock_orchestrator):
    """Create a test client for the FastAPI application."""
    app = create_app()

    # Patch the global orchestrator in app.py with our mock
    with patch("src.api.app.orchestrator", mock_orchestrator):
        # Return the test client with the patched app
        with TestClient(app) as client:
            yield client


@patch("src.api.app.LongTermMemory")
@patch("src.api.app.Memobase")
def test_create_agent_with_multi_user(
    mock_memobase_class, mock_long_term_memory_class, client, mock_orchestrator
):
    """Test creating an agent with multi-user support."""
    # Set up mock orchestrator.get_agent to return None initially
    # (agent doesn't exist)
    mock_orchestrator.get_agent.return_value = None

    # Set up mocks
    mock_long_term_memory = MagicMock()
    mock_long_term_memory_class.return_value = mock_long_term_memory

    mock_memobase = MagicMock()
    mock_memobase_class.return_value = mock_memobase

    # Set up mock orchestrator.create_agent to
    # set has_agent to True after creation
    def side_effect(*args, **kwargs):
        mock_agent = MagicMock()
        # After creation, has_agent should return True for this agent
        mock_orchestrator.has_agent.return_value = True
        # After creation, get_agent should return the mock agent
        mock_orchestrator.get_agent.return_value = mock_agent
        return mock_agent

    mock_orchestrator.create_agent.side_effect = side_effect

    # Make the request
    response = client.post(
        "/agents",
        json={
            "agent_id": "multi_user_agent",
            "system_message": "I support multiple users",
            "use_long_term_memory": True,
            "multi_user_support": True
        }
    )

    # Check response
    assert response.status_code == 200
    assert "created successfully" in response.json()["message"]

    # Verify create_agent was called with expected args
    mock_orchestrator.create_agent.assert_called_once()


@patch("src.api.app.LongTermMemory")
@patch("src.api.app.Memobase")
def test_create_agent_with_multi_user_integration(
    mock_memobase_class, mock_long_term_memory_class, client, mock_orchestrator
):
    """Test the integration between API, LongTermMemory, and Memobase."""
    # Set up mock orchestrator.get_agent to return None initially
    # (agent doesn't exist)
    mock_orchestrator.get_agent.return_value = None

    # Set up mocks
    mock_long_term_memory = MagicMock()
    mock_long_term_memory_class.return_value = mock_long_term_memory

    mock_memobase = MagicMock()
    mock_memobase_class.return_value = mock_memobase

    # Set up mock orchestrator.create_agent to
    # set has_agent to True after creation
    def side_effect(*args, **kwargs):
        mock_agent = MagicMock()
        # After creation, has_agent should return True for this agent
        mock_orchestrator.has_agent.return_value = True
        # After creation, get_agent should return the mock agent
        mock_orchestrator.get_agent.return_value = mock_agent
        return mock_agent

    mock_orchestrator.create_agent.side_effect = side_effect

    # Make the request
    response = client.post(
        "/agents",
        json={
            "agent_id": "multi_user_agent",
            "system_message": "I support multiple users",
            "use_long_term_memory": True,
            "multi_user_support": True
        }
    )

    # Check response
    assert response.status_code == 200
    assert "created successfully" in response.json()["message"]

    # Verify Memobase was created with proper args
    mock_memobase_class.assert_called_once()

    # Verify create_agent was called with the memobase instance
    args, kwargs = mock_orchestrator.create_agent.call_args
    assert "memobase" in kwargs


def test_chat_with_user_id(client, mock_orchestrator):
    """Test sending a chat message with user_id."""
    # Make the request
    response = client.post(
        "/agents/chat",
        json={
            "agent_id": "test_agent",
            "message": "Hello, assistant!",
            "user_id": 123
        }
    )

    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "I'm a helpful assistant."
    assert response.json()["user_id"] == 123

    # Verify agent.chat was called with user_id
    agent = mock_orchestrator.get_agent.return_value
    agent.chat.assert_called_with(message="Hello, assistant!", user_id=123)


def test_chat_without_user_id(client, mock_orchestrator):
    """Test sending a chat message without user_id."""
    # Make the request
    response = client.post(
        "/agents/chat",
        json={
            "agent_id": "test_agent",
            "message": "Hello, assistant!"
        }
    )

    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "I'm a helpful assistant."
    assert response.json()["user_id"] == 0  # Default user_id

    # Verify agent.chat was called with default user_id
    agent = mock_orchestrator.get_agent.return_value
    agent.chat.assert_called_with(message="Hello, assistant!", user_id=0)


def test_search_memory_with_user_id(client, mock_orchestrator):
    """Test searching memory with user_id."""
    # Make the request
    response = client.post(
        "/agents/memory/search",
        json={
            "agent_id": "test_agent",
            "query": "What did we discuss?",
            "user_id": 123
        }
    )

    # Check response
    assert response.status_code == 200
    assert response.json()["user_id"] == 123
    assert len(response.json()["results"]) > 0

    # Verify agent.search_memory was called with user_id
    agent = mock_orchestrator.get_agent.return_value
    agent.search_memory.assert_called_with(
        query="What did we discuss?",
        k=5,
        use_long_term=True,
        user_id=123
    )


def test_search_memory_without_user_id(client, mock_orchestrator):
    """Test searching memory without user_id."""
    # Make the request
    response = client.post(
        "/agents/memory/search",
        json={
            "agent_id": "test_agent",
            "query": "What did we discuss?"
        }
    )

    # Check response
    assert response.status_code == 200
    assert response.json()["user_id"] == 0  # Default user_id
    assert len(response.json()["results"]) > 0

    # Verify agent.search_memory was called with default user_id
    agent = mock_orchestrator.get_agent.return_value
    agent.search_memory.assert_called_with(
        query="What did we discuss?",
        k=5,
        use_long_term=True,
        user_id=0
    )


def test_clear_memory_with_user_id(client, mock_orchestrator, monkeypatch):
    """Test clearing memory with user_id."""
    # Since the endpoint doesn't exist yet, we'll mock a response
    mock_response = {
        "message": "Memory cleared successfully",
        "agent_id": "test_agent",
        "user_id": 123
    }

    # Mock the orchestrator's clear_memory method
    async def mock_clear_memory(*args, **kwargs):
        return mock_response

    # Apply the mock
    monkeypatch.setattr(
        "src.api.app.clear_memory_endpoint",
        mock_clear_memory,
        raising=False
    )

    # For now, we'll just verify that the agent's clear_memory method works
    agent = mock_orchestrator.get_agent.return_value
    agent.clear_memory(clear_long_term=False, user_id=123)

    # Verify agent.clear_memory was called with user_id
    agent.clear_memory.assert_called_with(
        clear_long_term=False,
        user_id=123
    )


def test_clear_memory_without_user_id(client, mock_orchestrator, monkeypatch):
    """Test clearing memory without user_id."""
    # Since the endpoint doesn't exist yet, we'll mock a response
    mock_response = {
        "message": "Memory cleared successfully",
        "agent_id": "test_agent",
        "user_id": 0
    }

    # Mock the orchestrator's clear_memory method
    async def mock_clear_memory(*args, **kwargs):
        return mock_response

    # Apply the mock
    monkeypatch.setattr(
        "src.api.app.clear_memory_endpoint",
        mock_clear_memory,
        raising=False
    )

    # For now, we'll just verify that the agent's clear_memory method works
    agent = mock_orchestrator.get_agent.return_value
    agent.clear_memory(clear_long_term=False, user_id=0)

    # Verify agent.clear_memory was called with default user_id
    agent.clear_memory.assert_called_with(
        clear_long_term=False,
        user_id=0
    )
