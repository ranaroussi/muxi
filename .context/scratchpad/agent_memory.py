"""
Updated Agent implementation that uses orchestrator-level memory.

This module provides the Agent class, which represents an agent in the
MUXI Framework that utilizes orchestrator-level memory instead of per-agent memory.
"""

import asyncio
import datetime
import aiohttp
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from muxi.core.mcp import MCPMessage
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory
from muxi.server.memory.memobase import Memobase
from muxi.models.base import BaseModel
from muxi.knowledge.base import KnowledgeSource
from muxi.utils.id_generator import get_default_nanoid


class Agent:
    """
    Agent class that combines language model and MCP servers, using orchestrator-level memory.
    """

    def __init__(
        self,
        model: BaseModel,
        orchestrator=None,  # Reference to parent orchestrator for memory access
        system_message: Optional[str] = None,
        name: Optional[str] = None,
        agent_id: Optional[str] = None,
        knowledge: Optional[List[KnowledgeSource]] = None,
        # Legacy parameters - kept for compatibility but not used
        buffer_memory: Optional[BufferMemory] = None,
        long_term_memory: Optional[Union[LongTermMemory, Memobase]] = None,
    ):
        """
        Initialize an agent.

        Args:
            model: The language model to use for generating responses.
            orchestrator: Reference to parent orchestrator for memory access.
            system_message: Optional system message to set agent's behavior.
            name: Optional name for the agent.
            agent_id: Optional unique identifier for the agent.
            knowledge: Optional list of knowledge sources for the agent.
            buffer_memory: Legacy parameter, no longer used directly.
            long_term_memory: Legacy parameter, no longer used directly.
        """
        self.model = model
        self.name = name or "AI Assistant"
        self.agent_id = agent_id or get_default_nanoid()
        self.orchestrator = orchestrator  # Store reference to orchestrator

        # Log warning if legacy memory parameters are used
        if buffer_memory is not None or long_term_memory is not None:
            logger.warning(
                "Memory parameters provided directly to Agent are deprecated. "
                "Memory should be configured at the Orchestrator level."
            )

        # For backward compatibility, store legacy memory if orchestrator not available
        self._buffer_memory = buffer_memory
        self._long_term_memory = long_term_memory

        self.system_message = system_message or (
            "You are a helpful AI assistant."
        )

        # Initialize knowledge handler if knowledge sources are provided
        self.knowledge_handler = None
        if knowledge:
            self._initialize_knowledge(knowledge)

        # Initialize MCP handler with no tools - we'll use MCP servers instead
        from muxi.core.mcp_handler import MCPHandler
        self.mcp_handler = MCPHandler(self.model)
        # Update system message in MCP handler if method exists
        if hasattr(self.mcp_handler, 'set_system_message'):
            self.mcp_handler.set_system_message(self.system_message)

        # Keep track of connected MCP servers
        self.mcp_servers = {}

    # Compatibility properties to provide access to orchestrator memory

    @property
    def buffer_memory(self):
        """Compatibility property that returns orchestrator's buffer memory."""
        if self.orchestrator and hasattr(self.orchestrator, "buffer_memory"):
            return self.orchestrator.buffer_memory
        return self._buffer_memory  # Fallback to legacy memory

    @property
    def long_term_memory(self):
        """Compatibility property that returns orchestrator's long-term memory."""
        if self.orchestrator and hasattr(self.orchestrator, "long_term_memory"):
            return self.orchestrator.long_term_memory
        return self._long_term_memory  # Fallback to legacy memory

    @property
    def is_multi_user(self):
        """Compatibility property that returns whether long-term memory is multi-user."""
        if self.orchestrator and hasattr(self.orchestrator, "is_multi_user"):
            return self.orchestrator.is_multi_user
        # Legacy behavior
        has_memory = self._long_term_memory is not None
        is_memobase = isinstance(self._long_term_memory, Memobase)
        return has_memory and is_memobase

    async def process_message(self, message: str, user_id: Optional[int] = None) -> MCPMessage:
        """
        Process a user message and generate a response.

        Args:
            message: The user's message.
            user_id: Optional user ID for multi-user support.

        Returns:
            An MCPMessage containing the agent's response.
        """
        # Store the message in memory
        timestamp = datetime.datetime.now().timestamp()

        # Add message to memory systems - use orchestrator if available
        if self.orchestrator and hasattr(self.orchestrator, "add_to_buffer_memory"):
            # Use orchestrator's memory methods
            self.orchestrator.add_to_buffer_memory(
                message=message,
                metadata={"role": "user", "timestamp": timestamp},
                agent_id=self.agent_id
            )
        elif self.buffer_memory:
            # Fallback to direct memory access
            self.buffer_memory.add(message, {"role": "user", "timestamp": timestamp})

        # If using multi-user memory, also store there with user context
        if self.is_multi_user and user_id is not None:
            if self.orchestrator and hasattr(self.orchestrator, "add_to_long_term_memory"):
                # Use orchestrator's memory methods
                await self.orchestrator.add_to_long_term_memory(
                    content=message,
                    metadata={"role": "user", "timestamp": timestamp},
                    agent_id=self.agent_id,
                    user_id=user_id
                )
            elif self.long_term_memory:
                # Fallback to direct memory access
                await self.long_term_memory.add(
                    content=message,
                    metadata={"role": "user", "timestamp": timestamp},
                    user_id=user_id,
                )

        # Enhance message with context memory if available
        enhanced_message = await self._enhance_with_context_memory(message, user_id)

        # Create a user message using MCPMessage format
        user_message = MCPMessage(role="user", content=enhanced_message)

        # Process the message using the MCP handler
        # This will handle tool calls automatically if the model's response includes them
        response = await self.mcp_handler.process_message(user_message)

        # Store assistant response in memory if using multi-user support
        if self.is_multi_user and user_id is not None:
            if self.orchestrator and hasattr(self.orchestrator, "add_to_long_term_memory"):
                # Use orchestrator's memory methods
                await self.orchestrator.add_to_long_term_memory(
                    content=response.content,
                    metadata={"role": "assistant", "timestamp": timestamp},
                    agent_id=self.agent_id,
                    user_id=user_id
                )
            elif self.long_term_memory:
                # Fallback to direct memory access
                await self.long_term_memory.add(
                    content=response.content,
                    metadata={"role": "assistant", "timestamp": timestamp},
                    user_id=user_id,
                )

        return response

    async def _store_in_memory(self, input_text: str, response_text: str) -> None:
        """
        Store the interaction in memory.

        Args:
            input_text: The input text from the user.
            response_text: The response text from the agent.
        """
        # Create combined text for embedding
        combined_text = f"User: {input_text}\nAssistant: {response_text}"

        # Get embedding
        embedding = await self.model.embed(combined_text)

        # Store metadata
        metadata = {
            "input": input_text,
            "response": response_text,
            "type": "conversation",
        }

        # Use orchestrator's memory if available
        if self.orchestrator:
            # Store in orchestrator's buffer memory
            if hasattr(self.orchestrator, "add_to_buffer_memory"):
                self.orchestrator.add_to_buffer_memory(
                    message=embedding,
                    metadata=metadata,
                    agent_id=self.agent_id
                )

            # Store in orchestrator's long-term memory
            if hasattr(self.orchestrator, "add_to_long_term_memory"):
                await self.orchestrator.add_to_long_term_memory(
                    content=combined_text,
                    embedding=embedding,
                    metadata=metadata,
                    agent_id=self.agent_id
                )

            return

        # Legacy fallback: store in buffer memory directly
        if self._buffer_memory:
            self._buffer_memory.add(
                vector=embedding,
                metadata=metadata,
            )

        # Legacy fallback: store in long-term memory directly
        if self._long_term_memory:
            await asyncio.to_thread(
                self._long_term_memory.add,
                text=combined_text,
                embedding=embedding,
                metadata=metadata,
            )

    async def search_memory(
        self,
        query: str,
        k: int = 5,
        use_long_term: bool = True,
        user_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the agent's memory for relevant information.

        Args:
            query: The query to search for.
            k: The number of results to return.
            use_long_term: Whether to search long-term memory.
            user_id: Optional user ID for multi-user support.

        Returns:
            A list of relevant memory items.
        """
        # Use orchestrator's search_memory if available
        if self.orchestrator and hasattr(self.orchestrator, "search_memory"):
            return await self.orchestrator.search_memory(
                query=query,
                agent_id=self.agent_id,
                k=k,
                use_long_term=use_long_term,
                user_id=user_id
            )

        # Legacy implementation (copied from original Agent class)
        # If Memobase is available and user_id is provided, use it
        if self.is_multi_user and user_id is not None:
            return await self.long_term_memory.search(query=query, limit=k, user_id=user_id)

        # Otherwise, fall back to traditional memory search
        # Get embedding for query
        query_embedding = await self.model.embed(query)

        # Search buffer memory
        buffer_results = self.buffer_memory.search(query_vector=query_embedding, k=k)

        # Convert to standard format
        results = [
            {
                "text": (f"User: {item[1]['input']}\n" f"Assistant: {item[1]['response']}"),
                "metadata": item[1],
                "distance": item[0],
                "source": "buffer",
            }
            for item in buffer_results
        ]

        # Search long-term memory if available and enabled
        if self.long_term_memory and use_long_term:
            lt_results = await asyncio.to_thread(
                self.long_term_memory.search, query_embedding=query_embedding, k=k
            )

            # Add to results
            results.extend(
                [
                    {
                        "text": item[1]["text"],
                        "metadata": item[1]["metadata"],
                        "distance": item[0],
                        "source": "long_term",
                    }
                    for item in lt_results
                ]
            )

            # Sort by distance
            results.sort(key=lambda x: x["distance"])

            # Limit to k results
            results = results[:k]

        return results

    def clear_memory(self, clear_long_term: bool = False, user_id: Optional[int] = None) -> None:
        """
        Clear the agent's memory.

        Args:
            clear_long_term: Whether to clear long-term memory as well.
            user_id: Optional user ID for multi-user support.
        """
        # Use orchestrator's clear_memory if available
        if self.orchestrator and hasattr(self.orchestrator, "clear_memory"):
            self.orchestrator.clear_memory(
                clear_long_term=clear_long_term,
                agent_id=self.agent_id,
                user_id=user_id
            )
            return

        # Legacy implementation (copied from original Agent class)
        # If Memobase is available and user_id is provided, use it
        if self.is_multi_user and user_id is not None:
            self.long_term_memory.clear_user_memory(user_id)
            return

        # Otherwise, fall back to traditional memory clearing
        # Clear buffer memory
        if self.buffer_memory:
            self.buffer_memory.clear()

        # Clear long-term memory if available and enabled
        if self.long_term_memory and clear_long_term:
            # Create a new default collection
            self.long_term_memory.create_collection(
                self.long_term_memory.default_collection,
                "Default collection for memories",
            )

    # Other methods from the original Agent class would continue here...
    # Most would remain unchanged or have minimal changes

    async def _enhance_with_context_memory(
        self, message: str, user_id: Optional[int] = None
    ) -> str:
        """
        Enhance the message with user context memory if available.

        Args:
            message: The original message to enhance
            user_id: User ID to retrieve context memory for

        Returns:
            Enhanced message with user context information
        """
        # Implementation remains largely the same as original Agent
        # Skip if no long-term memory or no user ID
        if not self.long_term_memory or user_id is None:
            return message

        try:
            # Get context memory for the user - api remains the same whether using
            # orchestrator's memory or direct access
            knowledge = await self.long_term_memory.get_user_context_memory(user_id=user_id)

            # If no knowledge found, return original message
            if not knowledge:
                return message

            # Create context with user information - same logic as original implementation
            context = "Information about the user:\n"

            # Add basic information if available
            if "name" in knowledge:
                context += f"- Name: {knowledge['name']}\n"

            if "age" in knowledge:
                context += f"- Age: {knowledge['age']}\n"

            # Add location if available
            if "location" in knowledge and isinstance(knowledge['location'], dict):
                location = knowledge['location']
                city = location.get('city', '')
                country = location.get('country', '')
                if city and country:
                    context += f"- Location: {city}, {country}\n"
                elif city:
                    context += f"- Location: {city}\n"
                elif country:
                    context += f"- Location: {country}\n"

            # Add interests if available
            if "interests" in knowledge:
                interests = knowledge['interests']
                if isinstance(interests, list):
                    context += f"- Interests: {', '.join(interests)}\n"
                else:
                    context += f"- Interests: {interests}\n"

            # Add job if available
            if "job" in knowledge:
                context += f"- Job: {knowledge['job']}\n"

            # Add family information if available
            if "family" in knowledge and isinstance(knowledge['family'], dict):
                family = knowledge['family']
                if "spouse" in family:
                    context += f"- Spouse: {family['spouse']}\n"
                if "children" in family and isinstance(family['children'], list):
                    children = family['children']
                    child_str = ', '.join(children)
                    context += f"- Children: {child_str}\n"

            # Add preferences if available
            if "preferences" in knowledge and isinstance(knowledge['preferences'], dict):
                prefs = knowledge['preferences']
                context += "- Preferences:\n"
                for key, value in prefs.items():
                    context += f"  - {key}: {value}\n"

            # Include any other top-level keys that weren't specifically handled
            excluded_keys = [
                "name", "age", "location", "interests",
                "job", "family", "preferences"
            ]
            for key, value in knowledge.items():
                if key not in excluded_keys:
                    # Skip complex objects for generic handling
                    if not isinstance(value, (dict, list)):
                        context += f"- {key}: {value}\n"

            # Combine context with original message
            enhanced_message = f"{context}\nUser message: {message}"
            return enhanced_message

        except Exception as e:
            # If anything goes wrong, just return the original message
            logger.error(f"Error enhancing message with context memory: {e}")
            return message
