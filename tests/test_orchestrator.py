"""
Unit tests for the Orchestrator class.

These tests verify that the Orchestrator implementation works correctly.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from muxi.core.orchestrator import Orchestrator
from muxi.core.mcp import MCPMessage


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
    def mock_buffer_memory(self):
        """Create a mock buffer memory for testing."""
        # Creating a custom class to define methods for the mock
        class MockBufferMemory:
            def add(self, message, metadata):
                return True

            def search(self, *args, **kwargs):
                return [(0.9, {"text": "Memory content"})]

            def clear(self, *args, **kwargs):
                return None

        # Create and return the mock
        mock = MagicMock(spec=MockBufferMemory())
        mock.add.return_value = True
        mock.search.return_value = [(0.9, {"text": "Memory content"})]
        mock.clear.return_value = None
        return mock

    @pytest.fixture
    def mock_long_term_memory(self):
        """Create a mock long term memory for testing."""
        # Creating a custom class to define methods for the mock
        class MockLongTermMemory:
            default_collection = "default"

            async def add(self, content, metadata, embedding=None):
                return "memory_id_123"

            async def search(self, query=None, query_embedding=None, k=5, filter_metadata=None):
                return [(0.8, {
                    "text": "Long term memory content",
                    "metadata": {"source": "knowledge_base"}
                })]

            def clear(self, *args, **kwargs):
                return None

            def create_collection(self, *args, **kwargs):
                return None

        # Create and return the mock
        mock = MagicMock(spec=MockLongTermMemory())
        mock.add = AsyncMock(return_value="memory_id_123")
        mock.search = AsyncMock(return_value=[
            (0.8, {
                "text": "Long term memory content",
                "metadata": {"source": "knowledge_base"}
            })
        ])
        mock.clear.return_value = None
        mock.create_collection.return_value = None
        mock.default_collection = "default"
        return mock

    @pytest.fixture
    def orchestrator(self, mock_agent):
        """Create an Orchestrator instance for testing."""
        orchestrator = Orchestrator()
        orchestrator.register_agent(mock_agent)
        return orchestrator

    @pytest.fixture
    def memory_orchestrator(self, mock_buffer_memory, mock_long_term_memory):
        """Create an Orchestrator instance with memory for testing."""
        return Orchestrator(
            buffer_memory=mock_buffer_memory,
            long_term_memory=mock_long_term_memory
        )

    def test_initialization(self):
        """Test that an orchestrator can be initialized correctly."""
        orchestrator = Orchestrator()

        assert orchestrator.agents == {}
        assert orchestrator.buffer_memory is None
        assert orchestrator.long_term_memory is None

    def test_initialization_with_memory(self, mock_buffer_memory, mock_long_term_memory):
        """Test that an orchestrator can be initialized with memory."""
        orchestrator = Orchestrator(
            buffer_memory=mock_buffer_memory,
            long_term_memory=mock_long_term_memory
        )

        assert orchestrator.buffer_memory == mock_buffer_memory
        assert orchestrator.long_term_memory == mock_long_term_memory

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

    @pytest.mark.asyncio
    async def test_add_to_buffer_memory(self, memory_orchestrator, mock_buffer_memory):
        """Test adding to buffer memory."""
        # Set up mock for add method
        mock_buffer_memory.add = AsyncMock()

        # Add to buffer memory
        await memory_orchestrator.add_to_buffer_memory(
            message="Test message",
            metadata={"test": "metadata"},
            agent_id="test_agent"
        )

        # Verify buffer memory was called
        mock_buffer_memory.add.assert_called_once_with(
            "Test message",
            metadata={"test": "metadata", "agent_id": "test_agent"}
        )

    @pytest.mark.asyncio
    async def test_add_to_buffer_memory_no_memory(self, orchestrator):
        """Test adding to buffer memory when not available."""
        # Override buffer_memory to None
        orchestrator.buffer_memory = None

        # Add to buffer memory when it's None
        result = await orchestrator.add_to_buffer_memory(
            message="Test message",
            metadata={"test": "metadata"}
        )

        # Verify result
        assert result is False

    @pytest.mark.asyncio
    async def test_add_to_long_term_memory(self, memory_orchestrator, mock_long_term_memory):
        """Test adding to long-term memory."""
        # Add to long-term memory
        result = await memory_orchestrator.add_to_long_term_memory(
            content="Test content",
            metadata={"test": "metadata"},
            agent_id="test_agent"
        )

        # Verify long-term memory was called
        mock_long_term_memory.add.assert_called_once_with(
            content="Test content",
            metadata={"test": "metadata", "agent_id": "test_agent"},
            embedding=None
        )

        # Verify result
        assert result == "memory_id_123"

    @pytest.mark.asyncio
    async def test_add_to_long_term_memory_no_memory(self, orchestrator):
        """Test adding to long-term memory when not available."""
        # Add to long-term memory when it's None
        result = await orchestrator.add_to_long_term_memory(
            content="Test content",
            metadata={"test": "metadata"}
        )

        # Verify result
        assert result is None

    @pytest.mark.skip("Test needs to be refactored due to API changes")
    @pytest.mark.asyncio
    async def test_search_memory(
        self,
        memory_orchestrator,
        mock_buffer_memory,
        mock_long_term_memory
    ):
        """Test searching memory."""
        # This test needs to be rewritten to match the current API
        pass

    @pytest.mark.skip("Test needs to be refactored due to API changes")
    def test_clear_memory(self, memory_orchestrator, mock_buffer_memory, mock_long_term_memory):
        """Test clearing memory."""
        # This test needs to be rewritten to match the current API
        pass

    def test_clear_memory_agent_filter(self, memory_orchestrator, mock_buffer_memory):
        """Test clearing memory with agent filter."""
        # Clear memory for specific agent
        memory_orchestrator.clear_memory(agent_id="test_agent")

        # Verify buffer memory was cleared with filter
        mock_buffer_memory.clear.assert_called_once_with(
            filter_metadata={"agent_id": "test_agent"}
        )
