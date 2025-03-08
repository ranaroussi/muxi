"""
Orchestrator for managing agents and their interactions.

This module provides the Orchestrator class, which manages agents and
coordinates their interactions with users and other systems.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from src.core.agent import Agent
from src.core.mcp import MCPMessage
from src.memory.base import BaseMemory
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase
from src.models.base import BaseModel
from src.tools.base import BaseTool, ToolRegistry


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
        self.default_agent_id: Optional[str] = None
        self.tool_registry = ToolRegistry()

    def create_agent(
        self,
        agent_id: str,
        model: BaseModel,
        memory: Optional[BaseMemory] = None,
        buffer_memory: Optional[BufferMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
        memobase: Optional[Memobase] = None,
        tools: Optional[List[BaseTool]] = None,
        system_message: Optional[str] = None,
        set_as_default: bool = False,
    ) -> Agent:
        """
        Create a new agent.

        Args:
            agent_id: Unique identifier for the agent.
            model: The language model to use for the agent.
            memory: Optional memory for storing conversation history
                (for backward compatibility).
            buffer_memory: Optional buffer memory for short-term context.
            long_term_memory: Optional long-term memory for persistent storage.
            memobase: Optional Memobase instance for multi-user memory support.
            tools: Optional list of tools the agent can use.
            system_message: Optional system message to set agent's behavior.
            set_as_default: Whether to set this agent as the default.

        Returns:
            The created agent.
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent_id}' already exists")

        # Convert tools list to dictionary
        tools_dict = {}
        if tools:
            for tool in tools:
                tools_dict[tool.name] = tool

        # Create agent
        agent = Agent(
            model=model,
            buffer_memory=buffer_memory,
            long_term_memory=long_term_memory,
            memobase=memobase,
            tools=tools_dict,
            system_message=system_message,
        )

        # Store the agent
        self.agents[agent_id] = agent

        # Set as default if requested or if this is the first agent
        if set_as_default or self.default_agent_id is None:
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

    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool with the orchestrator.

        This makes the tool available to all agents.

        Args:
            tool: The tool to register.
        """
        self.tool_registry.register(tool)

        # Add the tool to all agents
        for agent in self.agents.values():
            agent.add_tool(tool)

        logger.info(f"Registered tool '{tool.name}'")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available tools.

        Returns:
            A list of tool descriptions.
        """
        return self.tool_registry.get_schema()["tools"]

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
