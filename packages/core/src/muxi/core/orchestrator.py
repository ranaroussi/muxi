"""
Updated Orchestrator implementation with memory at the orchestrator level.

This module provides the updated Orchestrator class, which manages both agents
and memory systems centrally.
"""

import asyncio
import os
import secrets
import string
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from muxi.server.config import config
from muxi.core.agent import Agent
from muxi.core.mcp import MCPMessage
from muxi.core.mcp_service import MCPService
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory
from muxi.server.memory.memobase import Memobase
from muxi.models.base import BaseModel
from muxi.models.providers.openai import OpenAIModel


class Orchestrator:
    """
    Orchestrator for managing agents, memory, and interactions.

    This class provides a high-level interface for creating and managing
    agents, centralized memory access, and coordinating interactions with
    users and other systems.
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
        Initialize the orchestrator with optional centralized memory.

        Args:
            buffer_memory: Optional buffer memory for short-term context across all agents.
            long_term_memory: Optional long-term memory for persistent storage across all agents.
            auto_extract_user_info: Whether to automatically extract user information.
            extraction_model: Optional model to use for automatic information extraction.
            request_timeout: Default timeout in seconds for MCP server requests
            user_api_key: Optional API key for user-level access
            admin_api_key: Optional API key for admin-level access
        """
        self.agents: Dict[str, Agent] = {}
        self.agent_descriptions: Dict[str, str] = {}
        self.default_agent_id: Optional[str] = None
        self._routing_cache: Dict[str, str] = {}

        # Store centralized memory systems
        self.buffer_memory = buffer_memory
        self.long_term_memory = long_term_memory

        # Configure extraction settings
        self.auto_extract_user_info = auto_extract_user_info
        self.extraction_model = extraction_model
        self.memory_extractor = None

        # Track message counts per user for extraction
        self.message_counts = {}

        # If long-term memory is a Memobase instance, mark as multi-user
        self.is_multi_user = False
        if isinstance(self.long_term_memory, Memobase):
            self.is_multi_user = True

            # Initialize memory extractor if we have a Memobase and auto-extract is enabled
            if self.auto_extract_user_info:
                try:
                    from muxi.server.memory.extractor import MemoryExtractor
                    self.memory_extractor = MemoryExtractor(
                        orchestrator=self,
                        extraction_model=self.extraction_model,
                        auto_extract=self.auto_extract_user_info
                    )
                    logger.info(
                        "Initialized MemoryExtractor for automatic user information extraction"
                    )
                except ImportError:
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
        """Initialize the routing model from configuration."""
        try:
            # Get routing configuration
            routing_config = config.routing

            # Initialize the appropriate model based on provider
            provider = routing_config.provider.lower()

            if provider == "openai":
                # Get API key based on provider
                api_key = os.environ.get("OPENAI_API_KEY")

                self.routing_model = OpenAIModel(
                    model=routing_config.model,
                    temperature=routing_config.temperature,
                    max_tokens=routing_config.max_tokens,
                    api_key=api_key
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
                    temperature=0.0,
                    max_tokens=256,
                    api_key=os.environ.get("OPENAI_API_KEY")
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
        mcp_server: Optional['MCPServer'] = None,  # noqa: F821
        request_timeout: Optional[int] = None,
    ) -> Agent:
        """
        Create a new agent that uses the orchestrator's memory.

        Args:
            agent_id: Unique identifier for the agent.
            model: The language model to use for the agent.
            system_message: Optional system message to set agent's behavior.
            description: Optional description of the agent's capabilities and purpose.
                Used for intelligent message routing. Defaults to system_message if not provided.
            set_as_default: Whether to set this agent as the default.
            mcp_server: Optional MCP server for tool calling and external integrations.
            request_timeout: Optional timeout in seconds for MCP requests
                (defaults to orchestrator's timeout).

        Returns:
            The created agent.
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

        Args:
            agent: The agent to add.
            set_as_default: Whether to set this agent as the default.

        Returns:
            The created agent.
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

    def add_to_buffer_memory(
        self,
        message: Any,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Add a message to the orchestrator's buffer memory.

        Args:
            message: The message to add. Can be text or vector embedding.
            metadata: Optional metadata to associate with the message.
            agent_id: Optional agent ID to include in metadata.

        Returns:
            True if added successfully, False otherwise.
        """
        if not self.buffer_memory:
            return False

        # Add agent_id to metadata for context if provided
        full_metadata = metadata or {}
        if agent_id:
            full_metadata["agent_id"] = agent_id

        # Add to buffer memory
        self.buffer_memory.add(message, metadata=full_metadata)
        return True

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

        Args:
            content: The text content to store.
            metadata: Optional metadata to associate with the content.
            embedding: Optional pre-computed embedding vector.
            agent_id: Optional agent ID to include in metadata.
            user_id: Optional user ID for multi-user support.

        Returns:
            The ID of the newly created memory entry if successful, None otherwise.
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
        Search the orchestrator's memory for relevant information.

        Args:
            query: The query to search for.
            agent_id: Optional agent ID to filter results by.
            k: The number of results to return.
            use_long_term: Whether to search long-term memory.
            user_id: Optional user ID for multi-user support.
            filter_metadata: Additional metadata filters to apply.

        Returns:
            A list of relevant memory items.
        """
        # Start with empty results
        results = []

        # Prepare metadata filter
        full_filter = filter_metadata or {}
        if agent_id:
            full_filter["agent_id"] = agent_id

        # If we have a model, get embedding for query
        query_embedding = None
        if self.agents and next(iter(self.agents.values())).model:
            query_embedding = await next(iter(self.agents.values())).model.embed(query)

        # Search buffer memory if available
        if self.buffer_memory:
            try:
                if query_embedding:
                    buffer_results = self.buffer_memory.search(
                        query_vector=query_embedding,
                        k=k,
                        filter_metadata=full_filter
                    )
                else:
                    buffer_results = self.buffer_memory.search(
                        query=query,
                        k=k,
                        filter_metadata=full_filter
                    )

                # Convert to standard format
                results.extend([
                    {
                        "text": item[1].get("text", ""),
                        "metadata": item[1],
                        "distance": item[0],
                        "source": "buffer",
                    }
                    for item in buffer_results
                ])
            except Exception as e:
                logger.error(f"Error searching buffer memory: {e}")

        # Search long-term memory if available and enabled
        if self.long_term_memory and use_long_term:
            try:
                # Handle multi-user case with Memobase
                if self.is_multi_user and user_id is not None:
                    lt_results = await self.long_term_memory.search(
                        query=query,
                        limit=k,
                        user_id=user_id,
                        filter_metadata=full_filter
                    )
                # Standard long-term memory case
                else:
                    if query_embedding:
                        lt_results = await self.long_term_memory.search(
                            query_embedding=query_embedding,
                            k=k,
                            filter_metadata=full_filter
                        )
                    else:
                        lt_results = await self.long_term_memory.search(
                            query=query,
                            k=k,
                            filter_metadata=full_filter
                        )

                # Add to results in standard format
                results.extend([
                    {
                        "text": item[1].get("text", ""),
                        "metadata": item[1].get("metadata", {}),
                        "distance": item[0],
                        "source": "long_term",
                    }
                    for item in lt_results
                ])
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
        user_id: Optional[int] = None
    ) -> None:
        """
        Clear the orchestrator's memory.

        Args:
            clear_long_term: Whether to clear long-term memory as well.
            agent_id: Optional agent ID to clear only memory for a specific agent.
            user_id: Optional user ID for multi-user support.
        """
        # If we have multi-user memory and a user ID, clear just that user's memory
        if self.is_multi_user and user_id is not None:
            if self.long_term_memory:
                self.long_term_memory.clear_user_memory(user_id)
            return

        # Otherwise, handle centralized memory clearing
        # Clear buffer memory
        if self.buffer_memory:
            if agent_id:
                # Clear only entries with matching agent_id in metadata
                self.buffer_memory.clear(filter_metadata={"agent_id": agent_id})
            else:
                # Clear all buffer memory
                self.buffer_memory.clear()

        # Clear long-term memory if requested
        if clear_long_term and self.long_term_memory:
            if agent_id:
                # Clear only entries with matching agent_id in metadata
                # Implementation depends on long-term memory type
                logger.warning(
                    "Selective clearing by agent_id not fully implemented for long-term memory"
                )
            else:
                # For standard long-term memory, recreate the default collection
                has_create = hasattr(self.long_term_memory, "create_collection")
                has_default = hasattr(self.long_term_memory, "default_collection")
                if has_create and has_default:
                    self.long_term_memory.create_collection(
                        self.long_term_memory.default_collection,
                        "Default collection for memories",
                    )

        action = "all" if clear_long_term else "buffer"
        scope = f"for agent '{agent_id}'" if agent_id else "for all agents"
        logger.info(f"Cleared {action} memories {scope}")

    def clear_all_memories(self, clear_long_term: bool = False) -> None:
        """
        Clear the memories for all agents.

        This is now a wrapper around clear_memory() without agent_id filter.

        Args:
            clear_long_term: Whether to clear long-term memories as well.
        """
        self.clear_memory(clear_long_term=clear_long_term)

    def register_agent(self, agent):
        """
        Register an existing agent with the orchestrator.

        Args:
            agent: The agent to register. Must have a 'name' attribute.

        Raises:
            ValueError: If an agent with the same name already exists.
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

        Args:
            agent_id: The ID of the agent to use.
            message: The message to process.

        Returns:
            The agent's response.

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

        Args:
            agent_id: The ID of the agent to get. If None, the default agent
                will be returned.

        Returns:
            The requested agent.

        Raises:
            ValueError: If no agent with the given ID exists, or if no default
                agent has been set.
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
        Remove an agent.

        Args:
            agent_id: The ID of the agent to remove.

        Returns:
            True if the agent was removed, False if it didn't exist.
        """
        if agent_id not in self.agents:
            raise ValueError(f"No agent with ID '{agent_id}' exists")

        # Remove the agent
        del self.agents[agent_id]

        # Update default agent if necessary
        if self.default_agent_id == agent_id:
            self.default_agent_id = next(iter(self.agents)) if self.agents else None

        logger.info(f"Removed agent with ID '{agent_id}'")

        return True

    def set_default_agent(self, agent_id: str) -> None:
        """
        Set the default agent.

        Args:
            agent_id: The ID of the agent to set as default.

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
        Run an agent on an input text.

        Args:
            input_text: The input text to process.
            agent_id: Optional ID of the agent to use. If None, the default agent will be used.
            use_memory: Whether to use memory for context.

        Returns:
            The agent's response as a string.

        Raises:
            ValueError: If no agent with the given ID exists, or if no default agent has been set.
        """
        # Get the agent
        agent = self.get_agent(agent_id)

        # Run the agent
        return await agent.run(input_text, use_memory=use_memory)

    def run(self, host="0.0.0.0", port=5050, reload=True, mcp=False) -> None:
        """
        Start the MUXI server with the current orchestrator.

        This method starts the server and displays API keys if they were auto-generated.

        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            reload: Whether to enable auto-reload for development
            mcp: Whether to enable MCP server functionality
        """
        try:
            # Import here to avoid circular imports
            from muxi.server.run import run_server, is_port_in_use

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
        Select the most appropriate agent for a given message.

        Args:
            message: The message to route.

        Returns:
            The ID of the selected agent.
        """
        # If there's only one agent, use it
        if len(self.agents) == 1:
            return next(iter(self.agents))

        # If there's no default agent and we have agents, set the first one as default
        if self.default_agent_id is None and self.agents:
            self.default_agent_id = next(iter(self.agents))
            logger.info(
                f"Set agent '{self.default_agent_id}' as default (only agent)"
            )

        # If there are no agents, raise an error
        if not self.agents:
            raise ValueError("No agents available")

        # Check if we've seen this message before
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

            # Cache the result
            self._routing_cache[message] = selected_agent_id

            return selected_agent_id

        except Exception as e:
            # If anything goes wrong, use the default agent
            logger.error(f"Error routing message: {str(e)}")
            return self.default_agent_id

    def _create_routing_prompt(self, message: str) -> str:
        """
        Create a prompt for the routing model.

        Args:
            message: The message to route.

        Returns:
            A prompt for the routing model.
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

        Args:
            response: The response from the routing model.

        Returns:
            The ID of the selected agent, or None if parsing failed.
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
        Chat with an agent, automatically routing if no agent is specified.

        Args:
            message: The message to send.
            agent_name: Optional name of the agent to use. If None, the best agent will be selected.
            user_id: Optional user ID for multi-user systems.

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

        Returns:
            A dictionary mapping agent IDs to their information.
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
        extraction_model: Optional[BaseModel] = None
    ) -> None:
        """
        Handle the process of extracting user information from conversation.

        This method centralizes extraction logic, managing message counting
        and running extraction asynchronously to avoid blocking the main flow.

        Args:
            user_message: The latest message from the user
            agent_response: The agent's response to the user
            user_id: The user's ID
            agent_id: The agent's ID that handled the conversation
            extraction_model: Optional model to use for extraction
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
                    extraction_model=extraction_model
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
        extraction_model: Optional[BaseModel] = None
    ) -> None:
        """
        Run the extraction process asynchronously.

        This internal method handles the actual extraction process,
        using the MemoryExtractor to process the conversation turn.

        Args:
            user_message: The user's message
            agent_response: The agent's response
            user_id: The user's ID
            agent_id: The agent's ID
            message_count: The current message count for this user
            extraction_model: Optional model to use for extraction
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
                    message_count=message_count
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
                message_count=message_count
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
        extraction_model: Optional[BaseModel] = None
    ):
        """
        Extract and store information about a user from a conversation turn.

        This method is kept for backward compatibility.
        New code should use handle_user_information_extraction instead.

        Args:
            user_message: The message from the user
            agent_response: The response from the agent
            user_id: The user's ID
            agent_id: Optional agent ID that handled this conversation
            message_count: Counter for this user's messages (for throttling)
            extraction_model: Optional model to use for extraction

        Returns:
            None, but extracts and stores user information in the background
        """
        await self.handle_user_information_extraction(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            agent_id=agent_id or self.default_agent_id or "",
            extraction_model=extraction_model
        )

    async def get_user_context_memory(
        self,
        user_id: int,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get context memory for a specific user.

        Args:
            user_id: The user's ID to get context for
            agent_id: Optional agent ID to scope the context

        Returns:
            Dictionary of user context information
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
        agent_id: Optional[str] = None
    ) -> List[str]:
        """
        Add context memory for a specific user.

        Args:
            user_id: The user's ID
            knowledge: Dictionary of information to store
            source: Where this knowledge came from
            importance: Importance score (0.0 to 1.0)
            agent_id: Optional agent ID that provided this information

        Returns:
            List of memory IDs for stored information
        """
        if not self.is_multi_user or not isinstance(self.long_term_memory, Memobase):
            return []

        return await self.long_term_memory.add_user_context_memory(
            user_id=user_id,
            knowledge=knowledge,
            source=source,
            importance=importance
        )

    async def clear_user_context_memory(
        self,
        user_id: int,
        keys: Optional[List[str]] = None,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Clear context memory for a specific user.

        Args:
            user_id: The user's ID
            keys: Optional list of specific keys to clear
            agent_id: Optional agent ID that's clearing the memory

        Returns:
            True if successful, False otherwise
        """
        if not self.is_multi_user or not isinstance(self.long_term_memory, Memobase):
            return False

        return await self.long_term_memory.clear_user_context_memory(
            user_id=user_id,
            keys=keys
        )

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

        Args:
            server_id: Unique identifier for the MCP server
            url: URL for HTTP/SSE MCP servers
            command: Command for command-line MCP servers
            credentials: Optional credentials for authentication
            model: Optional model to use for this MCP handler
            request_timeout: Optional timeout in seconds for requests.
                Defaults to orchestrator's timeout.

        Returns:
            The server_id of the registered server
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
            request_timeout=timeout
        )

    async def list_mcp_tools(
        self, server_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List available tools from MCP servers.

        Args:
            server_id: Optional server ID to list tools from a specific server

        Returns:
            Dictionary mapping server IDs to lists of available tools
        """
        return await self.mcp_service.list_tools(server_id=server_id)

    def get_mcp_service(self) -> MCPService:
        """
        Get the centralized MCP service.

        Returns:
            The MCP service instance
        """
        return self.mcp_service

    async def add_message_to_memory(
        self,
        content: str,
        role: str,
        timestamp: float,
        agent_id: str,
        user_id: Optional[int] = None
    ) -> None:
        """
        Add a message to appropriate memory stores based on configuration.

        This centralizes all memory operations that were previously split between
        Agent and Orchestrator classes.

        Args:
            content: The message content to store
            role: The role of the message sender (e.g. 'user', 'assistant')
            timestamp: The timestamp of the message
            agent_id: The ID of the agent involved
            user_id: Optional user ID for multi-user support
        """
        # Always add to buffer memory regardless of user context
        if self.buffer_memory:
            metadata = {
                "role": role,
                "timestamp": timestamp,
                "agent_id": agent_id
            }

            self.buffer_memory.add(content, metadata=metadata)

        # Add to long-term memory if we have a valid user_id and multi-user support
        if self.is_multi_user and user_id is not None and user_id != 0 and self.long_term_memory:
            metadata = {
                "role": role,
                "timestamp": timestamp,
                "agent_id": agent_id
            }

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
                            content=enhanced_content,
                            metadata=metadata,
                            user_id=user_id
                        )
                    else:
                        # Store the original content
                        await self.long_term_memory.add(
                            content=content,
                            metadata=metadata,
                            user_id=user_id
                        )
                except Exception as e:
                    # Log error and fall back to original message
                    error_msg = "Error enhancing message with user context:"
                    logger.error(f"{error_msg} {e}")  # noqa: E501
                    await self.long_term_memory.add(
                        content=content,
                        metadata=metadata,
                        user_id=user_id
                    )
            else:
                # For non-user messages, just store directly
                await self.long_term_memory.add(
                    content=content,
                    metadata=metadata,
                    user_id=user_id
                )

    def _generate_api_key(self, key_type: str) -> str:
        """
        Generate a new API key.

        Args:
            key_type: Type of key to generate ("user" or "admin")

        Returns:
            A new API key string
        """
        # Generate a random string
        alphabet = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(24))

        # Add the appropriate prefix
        if key_type == "user":
            return f"sk_muxi_user_{random_part}"
        else:
            return f"sk_muxi_admin_{random_part}"

    def _display_splash_screen(self, host: str, port: int, api_keys: bool = False) -> None:
        """
        Display the MUXI splash screen.

        Args:
            host: Host the server is running on
            port: Port the server is running on
        """
        # Get the package version
        try:
            from importlib import metadata
            version = metadata.version("muxi")
        except (metadata.PackageNotFoundError, ImportError):
            version = "1.0.0"

        # Calculate padding for the URL display
        padding = ' ' * (24 - len(host) - len(str(port)))

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
        """Display auto-generated API keys with a warning message."""
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
