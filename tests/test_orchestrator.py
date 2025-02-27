"""
Unit tests for the Orchestrator class.

These tests verify that the Orchestrator implementation works correctly.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.core.orchestrator import Orchestrator
from src.core.mcp import MCPMessage


class TestOrchestrator:
    """Tests for the Orchestrator class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        mock = MagicMock()
        mock.name = "mock_agent"
        mock.process_message = AsyncMock(return_value=MCPMessage(
            role="assistant",
            content="Agent response"
        ))
        return mock

    @pytest.fixture
    def orchestrator(self, mock_agent):
        """Create an Orchestrator instance for testing."""
        orchestrator = Orchestrator()
        orchestrator.register_agent(mock_agent)
        return orchestrator

    def test_initialization(self):
        """Test that an orchestrator can be initialized correctly."""
        orchestrator = Orchestrator()

        assert orchestrator.agents == {}

    def test_register_agent(self, orchestrator, mock_agent):
        """Test that an agent can be registered."""
        # Agent is already registered in the fixture
        assert "mock_agent" in orchestrator.agents
        assert orchestrator.agents["mock_agent"] == mock_agent

    def test_register_multiple_agents(self, orchestrator):
        """Test that multiple agents can be registered."""
        # Create additional mock agents
        mock_agent2 = MagicMock()
        mock_agent2.name = "mock_agent2"

        mock_agent3 = MagicMock()
        mock_agent3.name = "mock_agent3"

        # Register the agents
        orchestrator.register_agent(mock_agent2)
        orchestrator.register_agent(mock_agent3)

        # Verify the agents were registered
        assert "mock_agent2" in orchestrator.agents
        assert orchestrator.agents["mock_agent2"] == mock_agent2

        assert "mock_agent3" in orchestrator.agents
        assert orchestrator.agents["mock_agent3"] == mock_agent3

    @pytest.mark.asyncio
    async def test_process_message(self, orchestrator, mock_agent):
        """Test that a message can be processed by a specified agent."""
        # Create a message
        message = MCPMessage(role="user", content="Hello, world!")

        # Process the message
        response = await orchestrator.process_message("mock_agent", message)

        # Verify the response
        assert response.role == "assistant"
        assert response.content == "Agent response"

        # Verify the agent was called correctly
        mock_agent.process_message.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_process_message_nonexistent_agent(self, orchestrator):
        """Test that processing a message for a nonexistent agent raises an error."""
        # Create a message
        message = MCPMessage(role="user", content="Hello, world!")

        # Processing the message for a nonexistent agent should raise a ValueError
        with pytest.raises(ValueError):
            await orchestrator.process_message("nonexistent_agent", message)

    @pytest.mark.asyncio
    async def test_collaborative_processing(self):
        """Test that messages can be processed collaboratively between agents."""
        # Create an orchestrator
        orchestrator = Orchestrator()

        # Create specialized mock agents
        research_agent = MagicMock()
        research_agent.name = "research"
        research_agent.process_message = AsyncMock(
            return_value=MCPMessage(
                role="assistant",
                content="Research information: ..."
            )
        )

        writing_agent = MagicMock()
        writing_agent.name = "writer"
        writing_agent.process_message = AsyncMock(
            return_value=MCPMessage(
                role="assistant",
                content="Final article: ..."
            )
        )

        # Register the agents
        orchestrator.register_agent(research_agent)
        orchestrator.register_agent(writing_agent)

        # Create messages
        research_query = MCPMessage(
            role="user",
            content="Find information about AI"
        )
        writing_query = MCPMessage(
            role="user",
            content="Write an article about AI"
        )

        # Process the messages in sequence
        research_response = await orchestrator.process_message(
            "research",
            research_query
        )
        writing_response = await orchestrator.process_message(
            "writer",
            writing_query
        )

        # Verify the responses
        assert research_response.role == "assistant"
        assert "Research information" in research_response.content

        assert writing_response.role == "assistant"
        assert "Final article" in writing_response.content

        # Verify the agents were called correctly
        research_agent.process_message.assert_called_once_with(research_query)
        writing_agent.process_message.assert_called_once_with(writing_query)

    def test_remove_agent(self, orchestrator, mock_agent):
        """Test that an agent can be removed."""
        # Remove the agent
        orchestrator.remove_agent("mock_agent")

        # Verify the agent was removed
        assert "mock_agent" not in orchestrator.agents

    def test_remove_nonexistent_agent(self, orchestrator):
        """Test that removing a nonexistent agent raises an error."""
        # Removing a nonexistent agent should raise a ValueError
        with pytest.raises(ValueError):
            orchestrator.remove_agent("nonexistent_agent")

    def test_get_agent(self, orchestrator, mock_agent):
        """Test that an agent can be retrieved."""
        # Get the agent
        agent = orchestrator.get_agent("mock_agent")

        # Verify the agent was retrieved
        assert agent == mock_agent

    def test_get_nonexistent_agent(self, orchestrator):
        """Test that getting a nonexistent agent raises an error."""
        # Getting a nonexistent agent should raise a ValueError
        with pytest.raises(ValueError):
            orchestrator.get_agent("nonexistent_agent")

    def test_list_agents(self, orchestrator, mock_agent):
        """Test that agents can be listed."""
        # Register additional agents
        mock_agent2 = MagicMock()
        mock_agent2.name = "mock_agent2"

        mock_agent3 = MagicMock()
        mock_agent3.name = "mock_agent3"

        orchestrator.register_agent(mock_agent2)
        orchestrator.register_agent(mock_agent3)

        # List the agents
        agents = orchestrator.list_agents()

        # Verify the agents were listed
        assert len(agents) == 3
        assert "mock_agent" in agents
        assert "mock_agent2" in agents
        assert "mock_agent3" in agents
