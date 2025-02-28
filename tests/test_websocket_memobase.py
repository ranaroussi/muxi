"""
Tests for WebSocket integration with Memobase.

This module tests the WebSocket handler's ability to handle user_id for
multi-user functionality through Memobase.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import WebSocket
from src.api.websocket import (
    handle_websocket,
    handle_chat_message,
    handle_memory_search,
    connection_user_id,
    update_activity
)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    ws = MagicMock(spec=WebSocket)
    ws.receive_text = AsyncMock()
    ws.send_json = AsyncMock()
    ws.accept = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = MagicMock()
    agent.chat = AsyncMock(return_value="I'm a helpful assistant.")
    agent.search_memory = AsyncMock(return_value=[
        {
            "content": "User-specific memory content",
            "metadata": {"user_id": 123},
            "source": "memobase",
            "distance": 0.8
        }
    ])
    return agent


@pytest.fixture
def mock_orchestrator(mock_agent):
    """Create a mock orchestrator that returns the mock agent."""
    orchestrator = MagicMock()
    orchestrator.get_agent = MagicMock(return_value=mock_agent)
    return orchestrator


@patch("src.api.websocket._orchestrator")
async def test_set_user_id_message(
    mock_orchestrator_global, mock_websocket
):
    """Test setting user_id via WebSocket message."""
    # Set up mock to receive a set_user message
    connection_id = "test_connection"
    mock_websocket.receive_text.side_effect = [
        json.dumps({"type": "set_user", "user_id": 123}),
        Exception("Stop test")  # To exit the loop
    ]

    # Call handle_websocket (which will exit after the first message due to exception)
    try:
        await handle_websocket(mock_websocket)
    except Exception as e:
        assert str(e) == "Stop test"

    # Verify that the WebSocket was accepted
    mock_websocket.accept.assert_called_once()

    # Verify that a user_set message was sent back
    user_set_call = False
    for call in mock_websocket.send_json.call_args_list:
        args, kwargs = call
        message = args[0]
        if message.get("type") == "user_set" and message.get("user_id") == 123:
            user_set_call = True
            break

    assert user_set_call, "No user_set message was sent"

    # Test that the connection_user_id dictionary was updated correctly
    # Need to check indirectly since we don't have the connection_id
    # The handle_websocket function should have updated the dictionary


@patch("src.api.websocket.get_agent")
async def test_handle_chat_message_with_user_id(
    mock_get_agent, mock_websocket, mock_agent
):
    """Test handling a chat message with user_id."""
    # Set up mocks
    mock_get_agent.return_value = mock_agent
    connection_id = "test_connection"

    # Add user_id to connection
    connection_user_id[connection_id] = 123

    # Handle chat message
    await handle_chat_message(
        connection_id,
        mock_websocket,
        {"agent_id": "test_agent", "message": "Hello, assistant!"},
        user_id=123
    )

    # Verify agent.chat was called with user_id
    mock_agent.chat.assert_called_with(
        "Hello, assistant!",
        user_id=123
    )

    # Verify appropriate messages were sent
    thinking_call = False
    message_call = False

    for call in mock_websocket.send_json.call_args_list:
        args, kwargs = call
        message = args[0]

        if message.get("type") == "thinking":
            thinking_call = True

        if message.get("type") == "message" and message.get("user_id") == 123:
            message_call = True

    assert thinking_call, "No thinking message was sent"
    assert message_call, "No message with user_id was sent"

    # Clean up
    if connection_id in connection_user_id:
        del connection_user_id[connection_id]


@patch("src.api.websocket.get_agent")
async def test_handle_chat_message_without_user_id(
    mock_get_agent, mock_websocket, mock_agent
):
    """Test handling a chat message without user_id."""
    # Set up mocks
    mock_get_agent.return_value = mock_agent
    connection_id = "test_connection"

    # Handle chat message (without setting user_id in connection_user_id)
    await handle_chat_message(
        connection_id,
        mock_websocket,
        {"agent_id": "test_agent", "message": "Hello, assistant!"}
    )

    # Verify agent.chat was called with default user_id (0)
    mock_agent.chat.assert_called_with(
        "Hello, assistant!",
        user_id=0
    )

    # Verify appropriate messages were sent with default user_id
    message_sent = False
    for call in mock_websocket.send_json.call_args_list:
        args, kwargs = call
        message = args[0]
        if (message.get("type") == "message" and
            message.get("user_id", None) == 0):
            message_sent = True
            break

    assert message_sent, "No message with default user_id was sent"


@patch("src.api.websocket.get_agent")
async def test_handle_memory_search_with_user_id(
    mock_get_agent, mock_websocket, mock_agent
):
    """Test handling a memory search with user_id."""
    # Set up mocks
    mock_get_agent.return_value = mock_agent
    connection_id = "test_connection"

    # Add user_id to connection
    connection_user_id[connection_id] = 123

    # Handle memory search
    await handle_memory_search(
        connection_id,
        mock_websocket,
        {
            "agent_id": "test_agent",
            "query": "What did we discuss?"
        },
        user_id=123
    )

    # Verify agent.search_memory was called with user_id
    mock_agent.search_memory.assert_called_with(
        query="What did we discuss?",
        k=5,
        use_long_term=True,
        user_id=123
    )

    # Verify appropriate response was sent
    response_sent = False
    for call in mock_websocket.send_json.call_args_list:
        args, kwargs = call
        message = args[0]
        if (message.get("type") == "memory_results" and
            message.get("user_id") == 123):
            response_sent = True
            break

    assert response_sent, "No memory_results with user_id was sent"

    # Clean up
    if connection_id in connection_user_id:
        del connection_user_id[connection_id]


@patch("src.api.websocket.get_agent")
async def test_handle_memory_search_without_user_id(
    mock_get_agent, mock_websocket, mock_agent
):
    """Test handling a memory search without user_id."""
    # Set up mocks
    mock_get_agent.return_value = mock_agent
    connection_id = "test_connection"

    # Handle memory search (without setting user_id in connection_user_id)
    await handle_memory_search(
        connection_id,
        mock_websocket,
        {
            "agent_id": "test_agent",
            "query": "What did we discuss?"
        }
    )

    # Verify agent.search_memory was called with default user_id (0)
    mock_agent.search_memory.assert_called_with(
        query="What did we discuss?",
        k=5,
        use_long_term=True,
        user_id=0
    )

    # Verify appropriate response was sent with default user_id
    response_sent = False
    for call in mock_websocket.send_json.call_args_list:
        args, kwargs = call
        message = args[0]
        if (message.get("type") == "memory_results" and
            message.get("user_id", None) == 0):
            response_sent = True
            break

    assert response_sent, "No memory_results with default user_id was sent"


async def test_websocket_connection_activity_tracking():
    """Test tracking activity for WebSocket connections."""
    # Test that update_activity updates the last activity time
    connection_id = "test_connection"

    # Call update_activity
    update_activity(connection_id)

    # Check if connection_id is in connection_last_activity
    from src.api.websocket import connection_last_activity
    assert connection_id in connection_last_activity
    assert isinstance(connection_last_activity[connection_id], float)
