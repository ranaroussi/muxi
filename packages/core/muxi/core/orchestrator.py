# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Orchestrator - Central Coordination Component
# Description:  Core component for managing agents, memory systems, and interactions
# Role:         The backbone of the Muxi framework's multi-agent architecture
# Usage:        Used to create, manage, and coordinate multiple AI agents
# Author:       Muxi Framework Team
#
# The Orchestrator is the primary coordination component in the Muxi framework.
# It serves as the centralized manager for:
#
# 1. Agent Lifecycle Management
#    - Creating and registering agents with different capabilities
#    - Managing agent discovery and selection
#    - Intelligent message routing between agents
#
# 2. Memory System Integration
#    - Centralized buffer memory for recent context
#    - Long-term memory for persistent knowledge
#    - Multi-user context with Memobase
#    - Information extraction and user profiling
#
# 3. External Tool Access
#    - MCP (Model Control Protocol) server integration
#    - Tool registration and discovery
#    - Secure API access management
#
# 4. User Management
#    - Authentication via API keys
#    - Multi-user support
#    - User context management
#
# The Orchestrator can be used in two main ways:
#
# Programmatic API:
#   orchestrator = Orchestrator(buffer_memory=buffer, long_term_memory=ltm)
#   agent = orchestrator.create_agent(agent_id="assistant", model=model)
#   response = await orchestrator.chat("Hello, how can you help me?")
#
# Configuration-based API (via muxi() function):
#   app = muxi(buffer_size=10, long_term="sqlite:///data/memory.db")
#   app.add_agent("assistant", "configs/assistant.yaml")
#   response = await app.chat("Hello, how can you help me?")
#
# This file contains the core implementation of the Orchestrator class, which
# is the foundation of Muxi's agent coordination system.
# =============================================================================

import asyncio
import os
import secrets
import string
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from muxi.core.config import config
from muxi.core.agent import Agent, MCPServer
from muxi.core.mcp import MCPMessage
from muxi.core.mcp import MCPService
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.models.base import BaseModel
from muxi.core.models.providers.openai import OpenAIModel


class Orchestrator:
    """
    Orchestrator for managing agents, memory, and interactions.

    The Orchestrator serves as the central coordination component in the Muxi Framework.
    It manages multiple agents, provides centralized memory access, handles message routing,
    and coordinates user interactions. The Orchestrator maintains buffer and long-term memory
    systems that can be shared across agents, enabling coherent multi-agent conversations.

    Key responsibilities:
    - Agent lifecycle management (creation, retrieval, removal)
    - Centralized memory management
    - Intelligent message routing
    - User authentication and authorization
    - Multi-user support
    - Tool integration via MCP

    Attributes:
        agents (Dict[str, Agent]): Dictionary of registered agents, keyed by agent_id
        agent_descriptions (Dict[str, str]): Descriptions of agents used for routing
        default_agent_id (Optional[str]): ID of the default agent for unrouted messages
        buffer_memory (Optional[BufferMemory]): Short-term memory for recent context
        long_term_memory (Optional[Union[LongTermMemory, Memobase]]): Persistent memory system
        auto_extract_user_info (bool): Whether to automatically extract user information
        extraction_model (Optional[BaseModel]): Model used for information extraction
        is_multi_user (bool): Whether multi-user mode is enabled
        mcp_service (MCPService): Service for managing Model Control Protocol servers
        request_timeout (int): Default timeout for MCP requests in seconds
        user_api_key (str): API key for user-level access
        admin_api_key (str): API key for admin-level access
    """

    def __init__(
        self,
        buffer_memory: Optional[BufferMemory] = None,
        long_term_memory: Optional[Union[LongTermMemory, Memobase]] = None,
        auto_extract_user_info: bool = True,
        extraction_model: Optional[BaseModel] = None,
        request_timeout: int = 60,
        user_api_key: Optional[str] = None,
        admin_api_key: Optional[str] = None,
    ):
        """
        Initialize the orchestrator with optional centralized memory systems.

        The constructor sets up the Orchestrator with the specified memory systems and
        configuration. It initializes agent storage, memory systems, extraction settings,
        and API keys. If memory systems are not provided, the Orchestrator will still
        function but with limited memory capabilities.

        Args:
            buffer_memory: Optional buffer memory for short-term context across all agents.
                This memory system stores recent messages and provides context for ongoing
                conversations.
            long_term_memory: Optional long-term memory for persistent storage across all agents.
                This can be either a LongTermMemory (for basic vector storage) or a Memobase
                (for multi-user support with structured knowledge).
            auto_extract_user_info: Whether to automatically extract user information from
                conversations. When enabled, the system will analyze conversations to identify
                and store user preferences, facts, and other relevant information.
            extraction_model: Optional model to use for automatic information extraction.
                If not provided but auto_extract_user_info is True, a default model will be used.
            request_timeout: Default timeout in seconds for MCP server requests. This controls
                how long to wait for external tools to respond before timing out.
            user_api_key: Optional API key for user-level access. If not provided, a random
                key will be generated.
            admin_api_key: Optional API key for admin-level access. If not provided, a random
                key will be generated.
        """
        # Initialize agent storage
        self.agents: Dict[str, Agent] = {}
        self.agent_descriptions: Dict[str, str] = {}
        self.default_agent_id: Optional[str] = None
        self._routing_cache: Dict[str, str] = {}  # Cache for message routing decisions

        # Store centralized memory systems
        self.buffer_memory = buffer_memory
        self.long_term_memory = long_term_memory

        # Configure extraction settings
        self.auto_extract_user_info = auto_extract_user_info
        self.extraction_model = extraction_model
        self.memory_extractor = None

        # Track message counts per user for extraction
        self.message_counts = {}  # Maps user_id to message count for throttling extraction

        # Determine if we're in multi-user mode based on memory type
        self.is_multi_user = False
        if isinstance(self.long_term_memory, Memobase):
            self.is_multi_user = True

            # Initialize memory extractor if we have a Memobase and auto-extract is enabled
            if self.auto_extract_user_info:
                try:
                    # Dynamically import to avoid circular dependencies
                    from muxi.core.memory.extractor import MemoryExtractor

                    self.memory_extractor = MemoryExtractor(
                        orchestrator=self,
                        extraction_model=self.extraction_model,
                        auto_extract=self.auto_extract_user_info,
                    )
                    logger.info(
                        "Initialized MemoryExtractor for automatic user information extraction"
                    )
                except ImportError:
                    # Log warning but continue if extractor can't be imported
                    logger.warning(
                        "Could not import MemoryExtractor, automatic extraction disabled"
                    )
                    self.auto_extract_user_info = False

        # Get/Initialize the MCP service
        self.mcp_service = MCPService.get_instance()

        # Initialize the routing model if needed
        self._initialize_routing_model()

        # Set request timeout
        self.request_timeout = request_timeout

        # Set or generate API keys
        self.user_api_key = user_api_key
        self.admin_api_key = admin_api_key

        # Generate API keys if not provided
        if self.user_api_key is None:
            self.user_api_key = self._generate_api_key("user")
            self._user_key_auto_generated = True
        else:
            self._user_key_auto_generated = False

        if self.admin_api_key is None:
            self.admin_api_key = self._generate_api_key("admin")
            self._admin_key_auto_generated = True
        else:
            self._admin_key_auto_generated = False

    def _initialize_routing_model(self):
        """
        Initialize the routing model for intelligent message routing between agents.

        This method sets up the LLM model used for selecting the most appropriate agent
        to handle specific messages based on their content and agent capabilities.
        The model and parameters are configured from the global configuration settings.

        If initialization fails (e.g., due to missing API keys or invalid configuration),
        the system will continue to function but will fall back to using the default agent
        for all messages rather than performing intelligent routing.
        """
        try:
            # Get routing configuration from global config
            routing_config = config.routing

            # Initialize the appropriate model based on provider
            provider = routing_config.provider.lower()

            if provider == "openai":
                # Get API key based on provider
                api_key = os.environ.get("OPENAI_API_KEY")

                # Initialize OpenAI model with configured parameters
                self.routing_model = OpenAIModel(
                    model=routing_config.model,
                    temperature=routing_config.temperature,
                    max_tokens=routing_config.max_tokens,
                    api_key=api_key,
                )

                logger.info(
                    f"Initialized routing model: {provider} / {routing_config.model} "
                    f"(temp: {routing_config.temperature})"
                )
            else:
                # Default to OpenAI if provider not recognized
                logger.warning(
                    f"Unrecognized routing LLM provider: {provider}. "
                    "Defaulting to OpenAI gpt-4o-mini."
                )
                self.routing_model = OpenAIModel(
                    model="gpt-4o-mini",
                    temperature=0.0,  # Use deterministic output for routing
                    max_tokens=256,  # Limit tokens since we only need the agent ID
                    api_key=os.environ.get("OPENAI_API_KEY"),
                )

        except Exception as e:
            # If initialization fails, log error but continue (routing will fall back to default)
            logger.error(f"Failed to initialize routing model: {str(e)}")
            self.routing_model = None

    def create_agent(
        self,
        agent_id: str,
        model: BaseModel,
        system_message: Optional[str] = None,
        description: Optional[str] = None,
        set_as_default: bool = False,
        mcp_server: Optional[MCPServer] = None,
        request_timeout: Optional[int] = None,
    ) -> Agent:
        """
        Create a new agent that uses the orchestrator's memory systems.

        This method creates a new agent instance with the specified configuration and registers
        it with the orchestrator. The created agent will have access to the orchestrator's
        centralized memory systems, enabling it to maintain context across conversations.

        Args:
            agent_id: Unique identifier for the agent. Must be unique among all registered agents.
                This ID is used for agent selection, routing, and in memory metadata.
            model: The language model to use for the agent. This model will process messages
                and generate responses for this specific agent.
            system_message: Optional system message to set agent's behavior and persona.
                This defines the agent's role, capabilities, and personality.
            description: Optional description of the agent's capabilities and purpose.
                Used for intelligent message routing to select the appropriate agent for
                specific queries. If not provided, falls back to system_message.
            set_as_default: Whether to set this agent as the default for unrouted messages.
                If True, or if this is the first agent being created, it will become the default.
            mcp_server: Optional MCP server for tool calling and external integrations.
                Enables the agent to access external tools and services.
            request_timeout: Optional timeout in seconds for MCP requests.
                If not provided, defaults to the orchestrator's timeout setting.

        Returns:
            The created agent instance.

        Raises:
            ValueError: If an agent with the provided agent_id already exists.
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent_id}' already exists")

        # Create agent with reference to orchestrator for memory access
        agent = Agent(
            model=model,
            orchestrator=self,  # Pass reference to orchestrator
            system_message=system_message,
            agent_id=agent_id,
            mcp_server=mcp_server,
            request_timeout=request_timeout,  # Pass timeout parameter
        )

        # Store the agent
        self.agents[agent_id] = agent

        # Store description for routing
        self.agent_descriptions[agent_id] = description or system_message or ""

        # Set as default if requested or if it's the first agent
        if set_as_default or len(self.agents) == 1:
            self.default_agent_id = agent_id

        logger.info(f"Created agent with ID '{agent_id}'")

        return agent

    def add_agent(
        self,
        agent: Agent,
        set_as_default: bool = False,
    ) -> Agent:
        """
        Add an existing agent to the orchestrator.

        This method registers a pre-constructed agent with the orchestrator. It's useful
        when you've created an agent instance directly and need to integrate it with
        the orchestrator's management system.

        Args:
            agent: The agent instance to add. Must have a unique agent_id not already
                registered with this orchestrator.
            set_as_default: Whether to set this agent as the default for unrouted messages.
                If True, or if this is the first agent being added, it will become the default.

        Returns:
            The added agent instance (same as input).

        Raises:
            ValueError: If an agent with the same agent_id already exists in the orchestrator.
        """
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent.agent_id}' already exists")

        # Store the agent
        self.agents[agent.agent_id] = agent

        # Store description for routing
        self.agent_descriptions[agent.agent_id] = agent.description or agent.system_message or ""

        # Set as default if requested or if it's the first agent
        if set_as_default or len(self.agents) == 1:
            self.default_agent_id = agent.agent_id

        logger.info(f"Created agent with ID '{agent.agent_id}'")

        return agent

    # Memory access methods

    async def add_to_buffer_memory(
        self,
        message: Any,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
    ) -> bool:
        """
        Add a message to the orchestrator's buffer memory.

        This method stores a message in the short-term buffer memory, which maintains
        context for ongoing conversations. The buffer memory provides recent message
        history and context for agents during conversation.

        Args:
            message: The message to add. Can be text or a vector embedding.
                For text messages, if buffer_memory has an embedding model,
                it will automatically generate the embedding.
            metadata: Optional metadata to associate with the message.
                Useful for filtering during retrieval (e.g., by topic, importance).
            agent_id: Optional agent ID to include in metadata.
                Used to track which agent was involved with this message.

        Returns:
            True if added successfully, False if buffer_memory is not available
            or an error occurred during addition.
        """
        if not self.buffer_memory:
            return False

        # Add agent_id to metadata for context if provided
        full_metadata = metadata or {}
        if agent_id:
            full_metadata["agent_id"] = agent_id

        # Add to buffer memory (now async)
        try:
            await self.buffer_memory.add(message, metadata=full_metadata)
            return True
        except Exception as e:
            logger.error(f"Error adding to buffer memory: {e}")
            return False

    async def add_to_long_term_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[str]:
        """
        Add content to the orchestrator's long-term memory.

        This method stores information in the persistent long-term memory system,
        which maintains knowledge across sessions. Content added to long-term memory
        will be available for semantic retrieval in future conversations.

        Args:
            content: The text content to store. This should be meaningful information
                that's worth retaining for future reference.
            metadata: Optional metadata to associate with the content.
                Useful for categorization and filtering (e.g., by topic, importance).
            embedding: Optional pre-computed embedding vector.
                If provided, skips the embedding generation step.
            agent_id: Optional agent ID to include in metadata.
                Used to track which agent was the source of this information.
            user_id: Optional user ID for multi-user support.
                Required when using Memobase in multi-user mode.

        Returns:
            The ID of the newly created memory entry if successful, None otherwise.
            This ID can be used for later updating or deleting the specific memory.
        """
        if not self.long_term_memory:
            return None

        # Add agent_id to metadata for context if provided
        full_metadata = metadata or {}
        if agent_id:
            full_metadata["agent_id"] = agent_id

        # Handle multi-user case with Memobase
        if self.is_multi_user and user_id is not None:
            try:
                return await self.long_term_memory.add(
                    content=content,
                    metadata=full_metadata,
                    embedding=embedding,
                    user_id=user_id,
                )
            except Exception as e:
                logger.error(f"Error adding to Memobase: {e}")
                return None

        # Standard long-term memory case
        try:
            return await self.long_term_memory.add(
                content=content,
                metadata=full_metadata,
                embedding=embedding,
            )
        except Exception as e:
            logger.error(f"Error adding to long-term memory: {e}")
            return None

    async def search_memory(
        self,
        query: str,
        agent_id: Optional[str] = None,
        k: int = 5,
        use_long_term: bool = True,
        user_id: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the orchestrator's memory systems for relevant information.

        This method performs a semantic search across available memory systems to find
        information relevant to the provided query. It can search both buffer memory
        (for recent context) and long-term memory (for persistent knowledge), combining
        the results into a single unified list.

        Args:
            query: The query text to search for. This will be used for semantic matching
                to find relevant information.
            agent_id: Optional agent ID to filter results by.
                Only returns memories associated with this specific agent.
            k: The number of results to return. Controls the maximum size of the result list.
            use_long_term: Whether to search long-term memory.
                If False, only searches buffer memory.
            user_id: Optional user ID for multi-user support.
                Required when using Memobase in multi-user mode.
            filter_metadata: Additional metadata filters to apply.
                Restricts results to those matching the specified metadata criteria.

        Returns:
            A list of relevant memory items, each as a dictionary with:
            - "text": The content text of the memory
            - "metadata": Associated metadata for the memory
            - "distance": Semantic distance score (lower is more relevant)
            - "source": The memory system source ("buffer" or "long_term")

            Results are sorted by relevance (lowest distance first).
        """
        # Start with empty results
        results = []

        # Prepare metadata filter
        full_filter = filter_metadata or {}
        if agent_id:
            full_filter["agent_id"] = agent_id

        # Search buffer memory if available
        if self.buffer_memory:
            try:
                # Use updated search method (now async)
                buffer_results = await self.buffer_memory.search(
                    query=query, limit=k, filter_metadata=full_filter
                )

                # Convert to standard format
                for item in buffer_results:
                    results.append(
                        {
                            "text": item["content"],
                            "metadata": item["metadata"],
                            "distance": 1.0 - item["score"],  # Convert score to distance
                            "source": "buffer",
                        }
                    )
            except Exception as e:
                logger.error(f"Error searching buffer memory: {e}")

        # Search long-term memory if available and enabled
        if self.long_term_memory and use_long_term:
            try:
                # Handle multi-user case with Memobase
                if self.is_multi_user and user_id is not None:
                    lt_results = await self.long_term_memory.search(
                        query=query, limit=k, user_id=user_id, filter_metadata=full_filter
                    )
                # Standard long-term memory case
                else:
                    lt_results = await self.long_term_memory.search(
                        query=query, k=k, filter_metadata=full_filter
                    )

                # Add to results in standard format
                results.extend(
                    [
                        {
                            "text": item[1].get("text", ""),
                            "metadata": item[1].get("metadata", {}),
                            "distance": item[0],
                            "source": "long_term",
                        }
                        for item in lt_results
                    ]
                )
            except Exception as e:
                logger.error(f"Error searching long-term memory: {e}")

        # Sort by distance and limit to k results
        results.sort(key=lambda x: x["distance"])
        results = results[:k]

        return results

    def clear_memory(
        self,
        clear_long_term: bool = False,
        agent_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        """
        Clear memory for the specified agent or user.

        This method removes items from memory systems based on the provided filters.
        It can clear both buffer memory and optionally long-term memory, with filters
        for specific agents or users.

        Args:
            clear_long_term: Whether to clear long-term memory as well.
                If False, only clears buffer memory.
            agent_id: Optional agent ID to filter by.
                Only clears memories associated with this specific agent.
            user_id: Optional user ID for multi-user support.
                Only clears memories for this specific user (requires Memobase).
        """
        filter_metadata = {}
        if agent_id:
            filter_metadata["agent_id"] = agent_id

        # Clear buffer memory
        if self.buffer_memory:
            try:
                self.buffer_memory.clear(
                    filter_metadata=filter_metadata if filter_metadata else None
                )
            except Exception as e:
                logger.error(f"Error clearing buffer memory: {e}")

        # Clear long-term memory if requested
        if clear_long_term and self.long_term_memory:
            try:
                if self.is_multi_user and user_id is not None:
                    # For multi-user with Memobase
                    asyncio.create_task(
                        self.long_term_memory.clear(
                            user_id=user_id,
                            filter_metadata=filter_metadata if filter_metadata else None,
                        )
                    )
                else:
                    # For standard long-term memory
                    asyncio.create_task(
                        self.long_term_memory.clear(
                            filter_metadata=filter_metadata if filter_metadata else None
                        )
                    )
            except Exception as e:
                logger.error(f"Error clearing long-term memory: {e}")

    def clear_all_memories(self, clear_long_term: bool = False) -> None:
        """
        Clear the memories for all agents.

        This is a convenience method that clears all memory without any agent
        or user filters. It's effectively a wrapper around clear_memory()
        without an agent_id filter.

        Args:
            clear_long_term: Whether to clear long-term memories as well.
                If False, only clears buffer memory.
        """
        self.clear_memory(clear_long_term=clear_long_term)

    def register_agent(self, agent):
        """
        Register an existing agent with the orchestrator.

        This method is a legacy compatibility method that registers an agent that
        uses the older API format (with 'name' attribute instead of 'agent_id').
        For new code, use add_agent() instead.

        Args:
            agent: The agent to register. Must have a 'name' attribute that will
                be used as the agent_id.

        Raises:
            ValueError: If the agent doesn't have a 'name' attribute or an agent
                with the same name already exists.

        Returns:
            The registered agent.
        """
        if not hasattr(agent, "name"):
            raise ValueError("Agent must have a 'name' attribute")

        agent_id = agent.name

        if agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent_id}' already exists")

        # Store the agent
        self.agents[agent_id] = agent

        # Set as default if this is the first agent
        if self.default_agent_id is None:
            self.default_agent_id = agent_id

        logger.info(f"Registered agent with ID '{agent_id}'")

        return agent

    async def process_message(self, agent_id: str, message: MCPMessage) -> MCPMessage:
        """
        Process a message using a specific agent.

        This method routes a message to the specified agent for processing and
        returns the agent's response. It's a lower-level method that works with
        MCPMessage objects rather than plain strings.

        Args:
            agent_id: The ID of the agent to use for processing the message.
                Must refer to an agent that has been registered with this orchestrator.
            message: The MCPMessage object containing the message to process.
                This is the standard message format used by the MCP protocol.

        Returns:
            The agent's response as an MCPMessage.

        Raises:
            ValueError: If no agent with the given ID exists.
        """
        # Get the agent
        if agent_id not in self.agents:
            raise ValueError(f"No agent with ID '{agent_id}' exists")

        agent = self.agents[agent_id]

        # Process the message
        response = await agent.process_message(message)

        return response

    def get_agent(self, agent_id: Optional[str] = None) -> Agent:
        """
        Get an agent by ID.

        This method retrieves a specific agent by its ID, or the default agent
        if no ID is provided.

        Args:
            agent_id: The ID of the agent to get. If None, the default agent
                will be returned.

        Returns:
            The requested agent.

        Raises:
            ValueError: If no agent with the given ID exists, or if no default
                agent has been set when agent_id is None.
        """
        # Use default agent if no ID is provided
        if agent_id is None:
            if self.default_agent_id is None:
                raise ValueError("No default agent has been set")
            agent_id = self.default_agent_id

        # Get the agent
        if agent_id not in self.agents:
            raise ValueError(f"No agent with ID '{agent_id}' exists")

        return self.agents[agent_id]

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the orchestrator.

        This method unregisters an agent and updates the default agent if necessary.

        Args:
            agent_id: The ID of the agent to remove.

        Returns:
            True if the agent was removed successfully.

        Raises:
            ValueError: If no agent with the given ID exists.
        """
        if agent_id not in self.agents:
            raise ValueError(f"No agent with ID '{agent_id}' exists")

        # Remove the agent
        del self.agents[agent_id]

        # Update default agent if necessary
        if self.default_agent_id == agent_id:
            # Set the first available agent as default, or None if no agents remain
            self.default_agent_id = next(iter(self.agents)) if self.agents else None

        logger.info(f"Removed agent with ID '{agent_id}'")

        return True

    def set_default_agent(self, agent_id: str) -> None:
        """
        Set the default agent for the orchestrator.

        The default agent is used when no specific agent is specified for a message,
        or when agent routing fails.

        Args:
            agent_id: The ID of the agent to set as default.
                Must refer to an agent that has been registered with this orchestrator.

        Raises:
            ValueError: If no agent with the given ID exists.
        """
        if agent_id not in self.agents:
            raise ValueError(f"No agent with ID '{agent_id}' exists")

        self.default_agent_id = agent_id
        logger.info(f"Set agent '{agent_id}' as default")

    async def run_agent(
        self, input_text: str, agent_id: Optional[str] = None, use_memory: bool = True
    ) -> str:
        """
        Run an agent on an input text and return the text response.

        This is a high-level convenience method that handles the common case of
        sending a text message to an agent and receiving a text response.

        Args:
            input_text: The input text to process. This is the user's message
                or query that will be sent to the agent.
            agent_id: Optional ID of the agent to use. If None, the default agent will be used.
                Must refer to an agent registered with this orchestrator.
            use_memory: Whether to use memory for context. If True, the agent will
                have access to relevant memories when processing the message.

        Returns:
            The agent's response as a string.

        Raises:
            ValueError: If no agent with the given ID exists, or if no default
                agent has been set when agent_id is None.
        """
        # Get the agent
        agent = self.get_agent(agent_id)

        # Run the agent
        return await agent.run(input_text, use_memory=use_memory)

    def run(self, host="0.0.0.0", port=5050, reload=True, mcp=False) -> None:
        """
        Start the MUXI server with the current orchestrator.

        This method launches the MUXI web server, which provides a REST API for
        interacting with the orchestrator and its agents. The server includes
        API documentation and endpoints for chat, memory management, and agent
        operations.

        Args:
            host: Host address to bind the server to. Default "0.0.0.0" binds to all
                available network interfaces.
            port: Port to bind the server to. Default is 5050.
            reload: Whether to enable auto-reload for development. When True, the
                server will restart automatically when source files change.
            mcp: Whether to enable MCP server functionality. When True, enables
                the Model Control Protocol server for tool integrations.
        """
        try:
            # Import here to avoid circular imports
            from muxi.core.run import run_server, is_port_in_use

            # Check if port is already in use
            if is_port_in_use(port):
                msg = f"Port {port} is already in use. MUXI server cannot start."
                logger.error(msg)
                print(f"Error: {msg}")
                print(f"Please stop any other processes using port {port} and try again.")
                return

            # Display splash screen
            if self._user_key_auto_generated or self._admin_key_auto_generated:
                self.__display_splash_screen_with_api_keys()
            else:
                self._display_splash_screen(host, port)

            # Start the server
            run_server(host=host, port=port, reload=reload, mcp=mcp)

        except Exception as e:
            logger.error(f"Failed to start MUXI server: {str(e)}")
            print(f"Error: Failed to start MUXI server: {str(e)}")

    async def select_agent_for_message(self, message: str) -> str:
        """
        Select the most appropriate agent for a given message using intelligent routing.

        This method analyzes the content of a message and determines which agent is best
        suited to handle it, based on agent descriptions and capabilities. It uses the
        routing model to make this determination, with fallbacks to ensure a valid
        agent is always selected.

        Args:
            message: The message to route. This is the user's message or query
                that needs to be directed to an appropriate agent.

        Returns:
            The ID of the selected agent. This will always be a valid agent ID
            registered with this orchestrator.

        Raises:
            ValueError: If no agents are available in the orchestrator.
        """
        # If there's only one agent, use it
        if len(self.agents) == 1:
            return next(iter(self.agents))

        # If there's no default agent and we have agents, set the first one as default
        if self.default_agent_id is None and self.agents:
            self.default_agent_id = next(iter(self.agents))
            logger.info(f"Set agent '{self.default_agent_id}' as default (only agent)")

        # If there are no agents, raise an error
        if not self.agents:
            raise ValueError("No agents available")

        # Check if we've seen this message before (use cached routing decision)
        if message in self._routing_cache:
            return self._routing_cache[message]

        # Check if a routing model is available
        if not hasattr(self, "routing_model") or self.routing_model is None:
            # Fall back to default agent
            logger.info(
                f"No routing model available, using default agent '{self.default_agent_id}'"
            )
            return self.default_agent_id

        try:
            # Create a prompt for the routing model
            prompt = self._create_routing_prompt(message)

            # Query the routing model
            response = await self.routing_model.generate(prompt)

            # Parse the response
            selected_agent_id = self._parse_routing_response(response)

            # If parsing failed or the agent doesn't exist, use the default
            if selected_agent_id is None or selected_agent_id not in self.agents:
                logger.warning(
                    f"Routing failed or returned invalid agent: '{selected_agent_id}'. "
                    f"Using default: '{self.default_agent_id}'"
                )
                selected_agent_id = self.default_agent_id
            else:
                logger.info(f"Routed message to agent: '{selected_agent_id}'")

            # Cache the result for future identical messages
            self._routing_cache[message] = selected_agent_id

            return selected_agent_id

        except Exception as e:
            # If anything goes wrong, use the default agent
            logger.error(f"Error routing message: {str(e)}")
            return self.default_agent_id

    def _create_routing_prompt(self, message: str) -> str:
        """
        Create a prompt for the routing model to determine the appropriate agent.

        This internal method constructs a prompt that instructs the LLM to select
        the most appropriate agent based on agent descriptions and the user's message.
        The prompt includes descriptions of all available agents and asks the model
        to select the best one for the given message.

        Args:
            message: The user's message that needs to be routed to an appropriate agent.

        Returns:
            A formatted prompt string for the routing model.
        """
        # Get agent descriptions
        agent_descriptions = []
        for agent_id, description in self.agent_descriptions.items():
            agent_descriptions.append(f"{agent_id}: {description}")

        # Create the prompt
        prompt = """
I need to decide which AI agent should handle a user's message. Based on the agent
descriptions and the user's message, select the most appropriate agent ID.

Available agents:
"""
        # Add agent descriptions
        for description in agent_descriptions:
            prompt += f"- {description}\n"

        # Add the message
        prompt += f"\nUser message: {message}\n"
        prompt += "\nRespond with the agent ID only."

        return prompt

    def _parse_routing_response(self, response: str) -> Optional[str]:
        """
        Parse the routing model's response to extract the selected agent ID.

        This internal method processes the LLM's response to identify which agent ID
        was selected. It uses various heuristics to extract the agent ID from the
        model's response, which might not always be in the exact format requested.

        Args:
            response: The raw text response from the routing model.

        Returns:
            The ID of the selected agent if successfully parsed, or None if parsing failed.
            A successful return value will be one of the agent IDs registered with this
            orchestrator.
        """
        # If the response is empty, return None
        if not response:
            return None

        # First, check if the response exactly matches an agent ID
        if response.strip() in self.agents:
            return response.strip()

        # Try to extract an agent ID using various heuristics
        for line in response.split("\n"):
            # Look for a clean statement like "Agent ID: xyz"
            if ":" in line:
                parts = line.split(":", 1)
                key, value = parts[0].strip().lower(), parts[1].strip()
                if "agent" in key and "id" in key:
                    if value in self.agents:
                        return value

            # Check if any agent ID is mentioned in the line
            for agent_id in self.agents:
                if agent_id in line:
                    return agent_id

        # If no agent ID was found, return None
        return None

    async def chat(
        self,
        message: str,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> MCPMessage:
        """
        Chat with an agent, automatically routing if no specific agent is specified.

        This is a high-level method that handles agent selection and message processing
        in a single call, making it easy to use the orchestrator for chat applications.
        If no agent is specified, it will use intelligent routing to select the most
        appropriate agent based on the message content.

        Args:
            message: The message to send. This is the user's message or query.
            agent_name: Optional name of the agent to use. If None, the best agent
                will be selected automatically using intelligent routing.
            user_id: Optional user ID for multi-user systems. Used for associating
                the message with a specific user and accessing user-specific memory.

        Returns:
            The agent's response as an MCPMessage.
        """
        # If agent_name is not specified, automatically select an agent
        if agent_name is None:
            agent_name = await self.select_agent_for_message(message)

        # Get the agent
        agent = self.get_agent(agent_name)

        # Process the message
        return await agent.process_message(message, user_id=user_id)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered agents and their descriptions.

        This method provides information about all available agents in the orchestrator,
        including their descriptions and whether they are set as the default agent.
        It's useful for displaying agent options in user interfaces or for debugging.

        Returns:
            A dictionary mapping agent IDs to their information, where each agent's
            information is itself a dictionary with:
            - "name": The agent's name (usually same as agent_id)
            - "description": The agent's description used for routing
            - "is_default": Boolean indicating if this is the default agent
        """
        agent_info = {}
        for agent_id, agent in self.agents.items():
            agent_info[agent_id] = {
                "name": agent.name,
                "description": self.agent_descriptions.get(agent_id, ""),
                "is_default": agent_id == self.default_agent_id,
            }
        return agent_info

    async def handle_user_information_extraction(
        self,
        user_message: str,
        agent_response: str,
        user_id: int,
        agent_id: str,
        extraction_model: Optional[BaseModel] = None,
    ) -> None:
        """
        Handle the process of extracting user information from a conversation turn.

        This method centralizes the logic for automatic extraction of user information.
        When enabled, it analyzes conversation messages to identify and store important
        user details like preferences, facts, and context information.

        The extraction runs asynchronously to avoid blocking the main conversation flow,
        and uses message counting to throttle extraction frequency.

        Args:
            user_message: The latest message from the user. This is analyzed
                for information about the user.
            agent_response: The agent's response to the user. This provides
                context for understanding the user's message.
            user_id: The user's ID. Required for storing extracted information.
                Anonymous users (user_id=0) are skipped.
            agent_id: The agent's ID that handled the conversation.
                Used for metadata and context.
            extraction_model: Optional model to use for extraction.
                If provided, overrides the default extraction model.
        """
        # Skip extraction for anonymous users
        if user_id == 0:
            return

        # Skip if extraction is disabled or not available
        if not self.auto_extract_user_info or not self.memory_extractor:
            return

        # Increment message count for this user
        self.message_counts[user_id] = self.message_counts.get(user_id, 0) + 1

        # Process this conversation turn for information extraction
        try:
            # Use asyncio.create_task to run extraction in background
            asyncio.create_task(
                self._run_extraction(
                    user_message=user_message,
                    agent_response=agent_response,
                    user_id=user_id,
                    agent_id=agent_id,
                    message_count=self.message_counts[user_id],
                    extraction_model=extraction_model,
                )
            )
            logger.debug(f"Automatic extraction scheduled for user {user_id}")
        except Exception as e:
            # Log but don't fail if extraction errors occur
            logger.warning(f"User information extraction failed: {str(e)}")

    async def _run_extraction(
        self,
        user_message: str,
        agent_response: str,
        user_id: int,
        agent_id: str,
        message_count: int = 1,
        extraction_model: Optional[BaseModel] = None,
    ) -> None:
        """
        Run the extraction process asynchronously.

        This internal method handles the actual extraction process,
        using the MemoryExtractor to analyze the conversation turn and
        extract relevant user information.

        Args:
            user_message: The user's message to analyze.
            agent_response: The agent's response for context.
            user_id: The user's ID for storing extracted information.
            agent_id: The agent's ID for metadata.
            message_count: The current message count for this user.
                Used for throttling extraction frequency.
            extraction_model: Optional model to use for extraction.
                If provided, temporarily overrides the default model.
        """
        # Use provided extraction model if available
        if extraction_model:
            # Temporarily override the extractor's model
            original_model = self.memory_extractor.extraction_model
            self.memory_extractor.extraction_model = extraction_model

            try:
                # Process the conversation turn
                await self.memory_extractor.process_conversation_turn(
                    user_message=user_message,
                    agent_response=agent_response,
                    user_id=user_id,
                    message_count=message_count,
                )
            finally:
                # Restore the original model
                self.memory_extractor.extraction_model = original_model
        else:
            # Use the default extraction model
            await self.memory_extractor.process_conversation_turn(
                user_message=user_message,
                agent_response=agent_response,
                user_id=user_id,
                message_count=message_count,
            )

    # Keep the existing extract_user_information method for backward compatibility
    # but rename it to clarify its actual role
    async def extract_user_information(
        self,
        user_message: str,
        agent_response: str,
        user_id: int,
        agent_id: Optional[str] = None,
        message_count: int = 1,
        extraction_model: Optional[BaseModel] = None,
    ):
        """
        Extract and store information about a user from a conversation turn.

        This method is kept for backward compatibility.
        New code should use handle_user_information_extraction instead.

        Args:
            user_message: The message from the user to analyze.
            agent_response: The response from the agent for context.
            user_id: The user's ID for storing extracted information.
            agent_id: Optional agent ID that handled this conversation.
                If None, uses the default agent ID.
            message_count: Counter for this user's messages (for throttling).
            extraction_model: Optional model to use for extraction.
                If provided, temporarily overrides the default model.

        Returns:
            None, but extracts and stores user information in the background.
        """
        await self.handle_user_information_extraction(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            agent_id=agent_id or self.default_agent_id or "",
            extraction_model=extraction_model,
        )

    async def get_user_context_memory(
        self, user_id: int, agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get context memory for a specific user.

        This method retrieves structured information about a user, such as preferences,
        facts, and other contextual details that have been stored in the memory system.
        It requires multi-user support to be enabled (Memobase).

        Args:
            user_id: The user's ID to get context for. This identifies the specific
                user whose context should be retrieved.
            agent_id: Optional agent ID to scope the context. Currently not used,
                but maintained for API consistency.

        Returns:
            Dictionary of user context information. The structure depends on what
            has been stored for the user, but typically includes sections like:
            - preferences: User UI/interaction preferences
            - personal_info: User personal details
            - facts: Known facts about the user

            Returns an empty dictionary if no context exists or if multi-user
            support is not enabled.
        """
        if not self.is_multi_user or not isinstance(self.long_term_memory, Memobase):
            return {}

        return await self.long_term_memory.get_user_context_memory(user_id=user_id)

    async def add_user_context_memory(
        self,
        user_id: int,
        knowledge: Dict[str, Any],
        source: str = "manual_input",
        importance: float = 0.9,
        agent_id: Optional[str] = None,
    ) -> List[str]:
        """
        Add context memory for a specific user.

        This method stores structured information about a user, such as preferences,
        facts, and other contextual details. It requires multi-user support to be
        enabled (Memobase).

        Args:
            user_id: The user's ID. This identifies the specific user whose
                context is being updated.
            knowledge: Dictionary of information to store. Can contain nested
                structures like preferences, personal information, etc.
            source: Where this knowledge came from (e.g., "manual_input",
                "conversation", "profile_update").
            importance: Importance score (0.0 to 1.0). Higher values indicate
                more important information.
            agent_id: Optional agent ID that provided this information.
                Currently not used, but maintained for API consistency.

        Returns:
            List of memory IDs for stored information. These can be used to
            reference the specific memory items later.
            Returns an empty list if multi-user support is not enabled.
        """
        if not self.is_multi_user or not isinstance(self.long_term_memory, Memobase):
            return []

        return await self.long_term_memory.add_user_context_memory(
            user_id=user_id, knowledge=knowledge, source=source, importance=importance
        )

    async def clear_user_context_memory(
        self, user_id: int, keys: Optional[List[str]] = None, agent_id: Optional[str] = None
    ) -> bool:
        """
        Clear context memory for a specific user.

        This method removes stored information about a user from the memory system.
        It requires multi-user support to be enabled (Memobase).

        Args:
            user_id: The user's ID. This identifies the specific user whose
                context should be cleared.
            keys: Optional list of specific keys to clear. If provided, only
                clears those specific keys rather than all context.
                Example: ["preferences.theme", "location"]
            agent_id: Optional agent ID that's clearing the memory.
                Currently not used, but maintained for API consistency.

        Returns:
            True if successful, False otherwise (including if multi-user
            support is not enabled).
        """
        if not self.is_multi_user or not isinstance(self.long_term_memory, Memobase):
            return False

        return await self.long_term_memory.clear_user_context_memory(user_id=user_id, keys=keys)

    async def register_mcp_server(
        self,
        server_id: str,
        url: Optional[str] = None,
        command: Optional[str] = None,
        credentials: Optional[Dict[str, Any]] = None,
        model: Optional[BaseModel] = None,
        request_timeout: Optional[int] = None,
    ) -> str:
        """
        Register an MCP server with the centralized MCP service.

        This method adds a Model Control Protocol (MCP) server to the orchestrator,
        making its tools available to agents. MCP servers can be external HTTP services,
        local command-line tools, or other tool providers that implement the MCP protocol.

        Args:
            server_id: Unique identifier for the MCP server. Used to reference the
                server when invoking tools or updating its configuration.
            url: URL for HTTP/SSE MCP servers. Required for web-based MCP servers,
                providing the endpoint to send MCP requests to.
            command: Command for command-line MCP servers. Required for CLI-based MCP
                servers, specifying the command to execute.
            credentials: Optional credentials for authentication with the MCP server.
                Format depends on the server's requirements.
            model: Optional model to use for this MCP handler. Some MCP servers
                require a model for processing tool invocations.
            request_timeout: Optional timeout in seconds for requests to this server.
                Defaults to the orchestrator's global timeout setting if not specified.

        Returns:
            The server_id of the registered server, confirming successful registration.

        Raises:
            ValueError: If neither url nor command is provided, or if both are provided.
            ConnectionError: If the MCP server cannot be contacted during registration.
        """
        # Use orchestrator's default timeout if none specified
        timeout = request_timeout if request_timeout is not None else self.request_timeout

        # Register the server with the MCP service
        return await self.mcp_service.register_mcp_server(
            server_id=server_id,
            url=url,
            command=command,
            credentials=credentials,
            model=model,
            request_timeout=timeout,
        )

    async def list_mcp_tools(
        self, server_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List available tools from MCP servers.

        This method retrieves information about the tools available from registered
        MCP servers, including their names, descriptions, parameters, and the servers
        they belong to.

        Args:
            server_id: Optional server ID to list tools from a specific server.
                If not provided, lists tools from all registered servers.

        Returns:
            Dictionary mapping server IDs to lists of available tools, where each
            tool is represented as a dictionary with:
            - "name": The tool's name
            - "description": The tool's description
            - "parameters": The tool's parameter schema (if any)
            - "returns": The tool's return type schema (if available)

            Example:
            {
                "weather_server": [
                    {
                        "name": "get_weather",
                        "description": "Get current weather for a location",
                        "parameters": {...}
                    }
                ]
            }
        """
        return await self.mcp_service.list_tools(server_id=server_id)

    def get_mcp_service(self) -> MCPService:
        """
        Get the centralized MCP service.

        This method provides access to the underlying MCPService instance that
        manages all MCP servers and tool invocations.

        Returns:
            The MCPService instance used by this orchestrator.
        """
        return self.mcp_service

    async def add_message_to_memory(
        self,
        content: str,
        role: str,
        timestamp: float,
        agent_id: str,
        user_id: Optional[int] = None,
    ) -> None:
        """
        Add a message to appropriate memory stores based on configuration.

        This method centralizes all memory operations that were previously split between
        Agent and Orchestrator classes. It handles adding messages to both buffer memory
        and long-term memory, with special handling for user context in multi-user mode.

        Args:
            content: The message content to store. This is the actual text message.
            role: The role of the message sender (e.g., 'user', 'assistant').
                Used for filtering and context management.
            timestamp: The timestamp of the message as a float (unix timestamp).
                Used for chronological ordering and recency calculations.
            agent_id: The ID of the agent involved in the conversation.
                Used for filtering and attribution.
            user_id: Optional user ID for multi-user support.
                Required for user context enhancement in multi-user mode.
        """
        # Always add to buffer memory regardless of user context
        if self.buffer_memory:
            metadata = {"role": role, "timestamp": timestamp, "agent_id": agent_id}

            self.buffer_memory.add(content, metadata=metadata)

        # Add to long-term memory if we have a valid user_id and multi-user support
        if self.is_multi_user and user_id is not None and user_id != 0 and self.long_term_memory:
            metadata = {"role": role, "timestamp": timestamp, "agent_id": agent_id}

            # Enhanced message with user context if this is a user message
            if role == "user":
                try:
                    # Get user context memory
                    context_memory = await self.get_user_context_memory(user_id=user_id)

                    # If context is available, enhance the message before storing
                    if context_memory:
                        # Format context memory for storage with the message
                        context_str = "User Context:\n"
                        for key, value in context_memory.items():
                            if isinstance(value, dict) and "value" in value:
                                # Handle structured context memory format
                                actual_value = value["value"]
                                context_str += f"- {key}: {actual_value}\n"
                            else:
                                # Handle simple format
                                context_str += f"- {key}: {value}\n"

                        # Store the enhanced content
                        enhanced_content = f"{context_str}\n\nUser Message: {content}"
                        metadata["enhanced"] = True
                        metadata["original_content"] = content

                        await self.long_term_memory.add(
                            content=enhanced_content, metadata=metadata, user_id=user_id
                        )
                    else:
                        # Store the original content
                        await self.long_term_memory.add(
                            content=content, metadata=metadata, user_id=user_id
                        )
                except Exception as e:
                    # Log error and fall back to original message
                    error_msg = "Error enhancing message with user context:"
                    logger.error(f"{error_msg} {e}")  # noqa: E501
                    await self.long_term_memory.add(
                        content=content, metadata=metadata, user_id=user_id
                    )
            else:
                # For non-user messages, just store directly
                await self.long_term_memory.add(content=content, metadata=metadata, user_id=user_id)

    def _generate_api_key(self, key_type: str) -> str:
        """
        Generate a new API key with appropriate prefix.

        This internal method creates a random, secure API key with a prefix indicating
        the key type (user or admin).

        Args:
            key_type: Type of key to generate ("user" or "admin").
                Determines the prefix of the generated key.

        Returns:
            A new API key string in the format:
            - User keys: "sk_muxi_user_[random string]"
            - Admin keys: "sk_muxi_admin_[random string]"
        """
        # Generate a random string
        alphabet = string.ascii_letters + string.digits
        random_part = "".join(secrets.choice(alphabet) for _ in range(24))

        # Add the appropriate prefix
        if key_type == "user":
            return f"sk_muxi_user_{random_part}"
        else:
            return f"sk_muxi_admin_{random_part}"

    def _display_splash_screen(self, host: str, port: int, api_keys: bool = False) -> None:
        """
        Display the MUXI splash screen with server information.

        This internal method shows a formatted ASCII art splash screen with the MUXI logo
        and information about the running server.

        Args:
            host: Host the server is running on, displayed in the splash screen.
            port: Port the server is running on, displayed in the splash screen.
            api_keys: Whether to modify the splash screen for API key display.
                If True, changes the footer line to support key display.
        """
        # Get the package version
        try:
            from importlib import metadata

            version = metadata.version("muxi")
        except (metadata.PackageNotFoundError, ImportError):
            version = "1.0.0"

        # Calculate padding for the URL display
        padding = " " * (24 - len(host) - len(str(port)))

        last_line = "╰──────────────────────────────────────╯"
        if api_keys:
            last_line = "╰─────────────┬────────────────────────╯"

        print(
            f"""
╭──────────────────────────────────────╮
│  ███╗   ███╗ ██╗   ██╗ ██╗  ██╗ ██╗  │
│  ████╗ ████║ ██║   ██║ ╚██╗██╔╝ ██║  │
│  ██╔████╔██║ ██║   ██║  ╚███╔╝  ██║  │
│  ██║╚██╔╝██║ ██║   ██║  ██╔██╗  ██║  │
│  ██║ ╚═╝ ██║ ╚██████╔╝ ██╔╝ ██╗ ██║  │
│  ╚═╝     ╚═╝  ╚═════╝  ╚═╝  ╚═╝ ╚═╝  │
│───────────────┬──────────────────────│
│  * MUXI Core  │  Version: {version:<10} │
│───────────────┴──────────────────────│
│                                      │
│  Running on:                         │
│  http://{host}:{port}{padding}│
│                                      │
{last_line}
"""
        )

    def _display_splash_screen_with_api_keys(self) -> None:
        """
        Display the MUXI splash screen with auto-generated API keys.

        This internal method shows the standard splash screen with an additional
        section for API keys, which is displayed when keys have been auto-generated.
        It includes a warning message about using auto-generated keys in production.
        """
        # Determine which keys to display
        if self._user_key_auto_generated:
            user_key_display = self.user_api_key
        else:
            user_key_display = "[user provided]"

        if self._admin_key_auto_generated:
            admin_key_display = self.admin_api_key
        else:
            admin_key_display = "[user provided]"

        # Determine key generation status message
        if self._user_key_auto_generated and self._admin_key_auto_generated:
            status = "(auto-generated)"
        else:
            status = "(partially auto-generated)"

        print(
            f"""              │
╭─────────────╰────────────────────────────────────────────────────────╮
│                                                                      │
│  API Keys {status:^40} │
│                                                                      │
│   — User:  {user_key_display:<50} │
│   — Admin: {admin_key_display:<50} │
│                                                                      │
│  ⚡ Auto-generating API keys should only be used during development.  │
│  We recommend to explicitly set your own API keys.                   │
│                                                                      │
╰──────────────────────────────────────────────────────────────────────╯
"""
        )
