"""
Orchestrator for managing agents and their interactions.

This module provides the Orchestrator class, which manages agents and
coordinates their interactions with users and other systems.
"""

import os
from typing import Any, Dict, List, Optional

from loguru import logger

from muxi.server.config import config
from muxi.core.agent import Agent
from muxi.core.mcp import MCPMessage
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory
from muxi.models.base import BaseModel
from muxi.models.providers.openai import OpenAIModel


class Orchestrator:
    """
    Orchestrator for managing agents and their interactions.

    This class provides a high-level interface for creating and managing
    agents, as well as coordinating their interactions with users and
    other systems.
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[str, Agent] = {}
        self.agent_descriptions: Dict[str, str] = {}
        self.default_agent_id: Optional[str] = None
        self._routing_cache: Dict[str, str] = {}

        # Initialize the routing model if needed
        self._initialize_routing_model()

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
        buffer_memory: Optional[BufferMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
        system_message: Optional[str] = None,
        description: Optional[str] = None,
        set_as_default: bool = False,
    ) -> Agent:
        """
        Create a new agent.

        Args:
            agent_id: Unique identifier for the agent.
            model: The language model to use for the agent.
            buffer_memory: Optional buffer memory for short-term context.
            long_term_memory: Optional long-term memory for persistent storage.
                Can be a LongTermMemory or Memobase instance for multi-user support.
            system_message: Optional system message to set agent's behavior.
            description: Optional description of the agent's capabilities and purpose.
                Used for intelligent message routing. Defaults to system_message if not provided.
            set_as_default: Whether to set this agent as the default.

        Returns:
            The created agent.
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent_id}' already exists")

        # Create agent
        agent = Agent(
            model=model,
            buffer_memory=buffer_memory,
            long_term_memory=long_term_memory,
            system_message=system_message,
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

    async def run(
        self, input_text: str, agent_id: Optional[str] = None, use_memory: bool = True
    ) -> str:
        """
        Run an agent on an input text.

        Args:
            input_text: The input text from the user.
            agent_id: The ID of the agent to run. If None, the default agent
                will be used.
            use_memory: Whether to use memory for context.

        Returns:
            The agent's response.
        """
        agent = self.get_agent(agent_id)
        return await agent.run(input_text, use_memory=use_memory)

    async def search_memory(
        self, query: str, agent_id: Optional[str] = None, k: int = 5, use_long_term: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search an agent's memory for relevant information.

        Args:
            query: The query to search for.
            agent_id: The ID of the agent to search. If None, the default
                agent will be used.
            k: The number of results to return.
            use_long_term: Whether to search long-term memory.

        Returns:
            A list of relevant memory items.
        """
        agent = self.get_agent(agent_id)
        return await agent.search_memory(query, k=k, use_long_term=use_long_term)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a list of all agents.

        Returns:
            A dictionary mapping agent IDs to agent information.
        """
        return {
            agent_id: {
                "is_default": agent_id == self.default_agent_id,
                "tools_count": len(agent.tools) if hasattr(agent, "tools") else 0,
                "system_message": (
                    agent.system_message if hasattr(agent, "system_message") else None
                ),
            }
            for agent_id, agent in self.agents.items()
        }

    def clear_all_memories(self, clear_long_term: bool = False) -> None:
        """
        Clear the memories of all agents.

        Args:
            clear_long_term: Whether to clear long-term memories as well.
        """
        for agent in self.agents.values():
            if hasattr(agent, "clear_memory"):
                agent.clear_memory(clear_long_term=clear_long_term)

        logger.info(f"Cleared {'all' if clear_long_term else 'buffer'} memories " f"for all agents")

    async def select_agent_for_message(self, message: str) -> str:
        """
        Select the most appropriate agent to handle a message using LLM-based routing.

        Args:
            message: The message to process

        Returns:
            str: The ID of the selected agent

        Raises:
            ValueError: If no agents are available
        """
        if not self.agents:
            raise ValueError("No agents available")

        # If there's only one agent, use it (no need for routing)
        if len(self.agents) == 1:
            return next(iter(self.agents))

        # If there's a default agent and no routing model, use the default
        if self.default_agent_id is not None and self.routing_model is None:
            return self.default_agent_id

        # Check cache if enabled
        if config.routing.use_caching and message in self._routing_cache:
            cached_agent_id = self._routing_cache[message]
            # Verify the cached agent still exists
            if cached_agent_id in self.agents:
                return cached_agent_id

        # For multiple agents with a routing model, use LLM-based routing
        if self.routing_model is not None:
            try:
                # Create routing prompt
                routing_prompt = self._create_routing_prompt(message)

                # Query the routing model
                response = await self.routing_model.chat(
                    messages=[
                        {"role": "system", "content": config.routing.system_prompt},
                        {"role": "user", "content": routing_prompt}
                    ]
                )

                # Parse the response to extract agent ID
                selected_agent_id = self._parse_routing_response(response)

                # If we got a valid agent ID, use it
                if selected_agent_id and selected_agent_id in self.agents:
                    # Cache the result if caching is enabled
                    if config.routing.use_caching:
                        self._routing_cache[message] = selected_agent_id
                    return selected_agent_id

                # Log warning if parsing failed
                logger.warning(
                    f"Failed to parse routing response: '{response}'. "
                    f"Falling back to default agent."
                )
            except Exception as e:
                # If routing fails, log error but don't raise exception
                logger.error(f"Agent routing failed: {str(e)}")
                # Continue to fallbacks

        # If we're here, routing failed or no routing model is available

        # Try basic keyword matching if routing failed
        try:
            # For each agent, count the number of matching words between the message and description
            scores = {}
            message_words = set(message.lower().split())

            for agent_id, description in self.agent_descriptions.items():
                if description:
                    # Count matching words between message and agent description
                    description_words = set(description.lower().split())
                    scores[agent_id] = len(message_words & description_words)

            # Select the agent with the highest score, if any
            if scores:
                best_agent_id = max(scores.items(), key=lambda x: x[1])[0]
                # Only use if there's at least one matching word
                if scores[best_agent_id] > 0:
                    logger.info(f"Selected agent '{best_agent_id}' using keyword matching")
                    return best_agent_id
        except Exception as e:
            logger.error(f"Keyword matching failed: {str(e)}")
            # Continue to fallbacks

        # Fallbacks in order: default agent, first agent
        if self.default_agent_id is not None:
            return self.default_agent_id
        return next(iter(self.agents))

    def _create_routing_prompt(self, message: str) -> str:
        """
        Create a prompt for the routing model to select the appropriate agent.

        Args:
            message: The user message to route

        Returns:
            str: The routing prompt
        """
        # Build a routing prompt with all agent descriptions
        prompt = f"User message: \"{message}\"\n\nAvailable agents:\n\n"

        for agent_id, description in self.agent_descriptions.items():
            prompt += f"Agent ID: {agent_id}\nDescription: {description}\n\n"

        prompt += (
            "Based on the user message and agent descriptions above, which agent "
            "(specify agent ID only) would be best suited to handle this message? "
            "Reply with just the agent ID."
        )

        return prompt

    def _parse_routing_response(self, response: str) -> Optional[str]:
        """
        Extract the agent ID from the routing model's response.

        Args:
            response: The routing model's response

        Returns:
            Optional[str]: The extracted agent ID, or None if parsing failed
        """
        # Clean up the response
        response = response.strip().lower()

        # First try a direct match with one of the agent IDs
        for agent_id in self.agents.keys():
            if agent_id.lower() == response:
                return agent_id

        # Try finding the agent ID in the response
        for agent_id in self.agents.keys():
            if agent_id.lower() in response:
                return agent_id

        # Try using regex to find something that looks like an agent ID
        import re
        match = re.search(r"agent[_\s]?id:?\s*[\"']?([a-zA-Z0-9_-]+)[\"']?", response)
        if match:
            agent_id = match.group(1)
            if agent_id in self.agents:
                return agent_id

        # Return None if we couldn't identify an agent
        return None

    async def chat(
        self,
        message: str,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> MCPMessage:
        """
        Send a message to an agent and get a response.

        Args:
            message: The message to send to the agent.
            agent_name: Optional name of the agent to use. If not provided,
                the most appropriate agent will be selected automatically.
            user_id: Optional user ID for multi-user support.

        Returns:
            The agent's response.

        Raises:
            ValueError: If no agents are available or the specified agent
                does not exist.
        """
        if not self.agents:
            raise ValueError("No agents available")

        # If agent_name is provided, use that specific agent
        if agent_name:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' does not exist")
            selected_agent_id = agent_name
        else:
            # Otherwise, select the most appropriate agent for this message
            selected_agent_id = await self.select_agent_for_message(message)

        # Get the selected agent
        agent = self.agents[selected_agent_id]

        # Process the message with the selected agent
        response = await agent.chat(message, user_id=user_id)

        # Add the agent ID to the response for tracking
        response.agent_id = selected_agent_id

        return response
