"""
Updated Orchestrator implementation with memory at the orchestrator level.

This module provides the updated Orchestrator class, which manages both agents
and memory systems centrally.
"""

import os
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from muxi.core.config import config
from muxi.core.agent import Agent
from muxi.core.mcp import MCPMessage
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
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
        long_term_memory: Optional[Union[LongTermMemory, Memobase]] = None
    ):
        """
        Initialize the orchestrator with optional centralized memory.

        Args:
            buffer_memory: Optional buffer memory for short-term context across all agents.
            long_term_memory: Optional long-term memory for persistent storage across all agents.
        """
        self.agents: Dict[str, Agent] = {}
        self.agent_descriptions: Dict[str, str] = {}
        self.default_agent_id: Optional[str] = None
        self._routing_cache: Dict[str, str] = {}

        # Store centralized memory systems
        self.buffer_memory = buffer_memory
        self.long_term_memory = long_term_memory

        # If long-term memory is a Memobase instance, mark as multi-user
        self.is_multi_user = isinstance(long_term_memory, Memobase)

        # Initialize the routing model if needed
        self._initialize_routing_model()

    def _initialize_routing_model(self):
        """Initialize the routing model from configuration."""
        # Existing implementation...
        pass

    def create_agent(
        self,
        agent_id: str,
        model: BaseModel,
        system_message: Optional[str] = None,
        description: Optional[str] = None,
        set_as_default: bool = False,
        # Legacy parameters (will be ignored but kept for compatibility)
        buffer_memory: Optional[BufferMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
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
            buffer_memory: Legacy parameter, ignored (agents use orchestrator's memory).
            long_term_memory: Legacy parameter, ignored (agents use orchestrator's memory).

        Returns:
            The created agent.
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent_id}' already exists")

        # Log warning if legacy memory parameters are provided
        if buffer_memory is not None or long_term_memory is not None:
            logger.warning(
                "Memory parameters provided to create_agent() are ignored. "
                "Memory is now managed at the orchestrator level."
            )

        # Create agent with reference to orchestrator for memory access
        agent = Agent(
            model=model,
            orchestrator=self,  # Pass reference to orchestrator
            system_message=system_message,
            agent_id=agent_id,
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
                logger.warning("Selective clearing by agent_id not fully implemented for long-term memory")
            else:
                # For standard long-term memory, recreate the default collection
                if hasattr(self.long_term_memory, "create_collection") and hasattr(self.long_term_memory, "default_collection"):
                    self.long_term_memory.create_collection(
                        self.long_term_memory.default_collection,
                        "Default collection for memories",
                    )

        action = "all" if clear_long_term else "buffer"
        scope = f"for agent '{agent_id}'" if agent_id else "for all agents"
        logger.info(f"Cleared {action} memories {scope}")

    # Existing methods continue below...

    def clear_all_memories(self, clear_long_term: bool = False) -> None:
        """
        Clear the memories for all agents.

        This is now a wrapper around clear_memory() without agent_id filter.

        Args:
            clear_long_term: Whether to clear long-term memories as well.
        """
        self.clear_memory(clear_long_term=clear_long_term)

    # Other methods from original Orchestrator class would continue here...
