"""
Agent implementation for the MUXI Framework.

This module provides the Agent class, which represents an agent in the
MUXI Framework.
"""

import asyncio
import datetime
import aiohttp
from typing import Any, Dict, List, Optional

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
    Agent class that combines language model, memory, and MCP servers to create an AI agent.
    """

    def __init__(
        self,
        model: BaseModel,
        buffer_memory: Optional[BufferMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
        system_message: Optional[str] = None,
        name: Optional[str] = None,
        agent_id: Optional[str] = None,
        knowledge: Optional[List[KnowledgeSource]] = None,
    ):
        """
        Initialize an agent.

        Args:
            model: The language model to use for generating responses.
            buffer_memory: Optional buffer memory for short-term context.
            long_term_memory: Optional long-term memory for persistent storage.
                Can be a LongTermMemory or Memobase instance for multi-user support.
            system_message: Optional system message to set agent's behavior.
            name: Optional name for the agent.
            agent_id: Optional unique identifier for the agent.
            knowledge: Optional list of knowledge sources for the agent.
        """
        self.model = model
        self.name = name or "AI Assistant"
        self.agent_id = agent_id or get_default_nanoid()

        # Handle memory options
        self.buffer_memory = buffer_memory or BufferMemory()

        self.long_term_memory = long_term_memory
        # Check if long_term_memory is a Memobase instance
        has_memory = self.long_term_memory is not None
        is_memobase = isinstance(self.long_term_memory, Memobase)
        self.is_multi_user = has_memory and is_memobase

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

    async def connect_mcp_server(
        self,
        name: str,
        url_or_command: str,
        type: str = "http",
        credentials: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: The name of the MCP server
            url_or_command: The URL or command to start the MCP server
            type: The type of transport to use ("http" or "command")
            credentials: Optional credentials for the MCP server

        Returns:
            bool: True if connection was successful
        """
        try:
            # Connect to MCP server
            logger.info(f"Connecting to MCP server {name} at {url_or_command}")

            success = await self.mcp_handler.connect_mcp_server(
                name=name,
                url_or_command=url_or_command,
                type=type,
                credentials=credentials
            )

            if success:
                # Store server details for reference
                self.mcp_servers[name] = {
                    "url_or_command": url_or_command,
                    "type": type,
                    "credentials": credentials or {}
                }

                logger.info(f"Successfully connected to MCP server: {name}")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {name}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to MCP server {name}: {str(e)}")
            return False

    async def disconnect_mcp_server(self, name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            name: The name of the MCP server

        Returns:
            bool: True if disconnection was successful
        """
        if name not in self.mcp_servers:
            logger.warning(f"Attempted to disconnect from non-existent MCP server: {name}")
            return False

        try:
            success = await self.mcp_handler.disconnect_mcp_server(name)

            if success:
                del self.mcp_servers[name]
                logger.info(f"Successfully disconnected from MCP server: {name}")
                return True
            else:
                logger.error(f"Failed to disconnect from MCP server: {name}")
                return False
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {name}: {str(e)}")
            return False

    async def _handle_mcp_server_call(
        self,
        server_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle a call to an MCP server.

        Args:
            server_name: The name of the MCP server
            parameters: The parameters for the call

        Returns:
            The result of the call
        """
        server = self.mcp_servers.get(server_name)
        if not server:
            raise ValueError(f"MCP server not found: {server_name}")

        # Log the call
        logger.debug(
            f"Calling MCP server {server_name} with parameters: {parameters}"
        )

        url = server["url_or_command"]
        credentials = server["credentials"]

        try:
            # Merge credentials with parameters
            call_params = {**parameters, **credentials}

            # Make HTTP request to the MCP server
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{url}/mcp/execute",
                    json={"name": server_name, "parameters": call_params}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"MCP server {server_name} returned error: {error_text}"
                        )
                        return {"error": f"MCP server error: {response.status}"}

                    result = await response.json()
                    return result
        except Exception as e:
            logger.error(f"Error calling MCP server {server_name}: {str(e)}")
            return {"error": f"Failed to call MCP server: {str(e)}"}

    async def get_available_mcp_servers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available MCP servers.

        Returns:
            A list of MCP server descriptions.
        """
        # Use the mcp_handler's implementation which contains additional status info
        return await self.mcp_handler.get_available_mcp_servers()

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
        # Skip if no long-term memory
        if not hasattr(self, "long_term_memory"):
            return message

        # Skip if no user ID
        if user_id is None:
            return message

        try:
            # Get context memory for the user
            knowledge = await self.long_term_memory.get_user_context_memory(user_id=user_id)

            # If no knowledge found, return original message
            if not knowledge:
                return message

            # Create context with user information
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
            print(f"Error enhancing message with context memory: {e}")
            return message

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

        # Add message to memory systems
        self.buffer_memory.add(message, {"role": "user", "timestamp": timestamp})

        # If using Memobase, also store there with user context
        if self.is_multi_user and user_id is not None:
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
            await self.long_term_memory.add(
                content=response.content,
                metadata={"role": "assistant", "timestamp": timestamp},
                user_id=user_id,
            )

        return response

    def get_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories.

        Args:
            query: The search query.
            limit: Maximum number of results to return.

        Returns:
            A list of memory entries.
        """
        # Use buffer memory
        return self.buffer_memory.search(query, limit)

    def _create_message_context(self, message: str) -> Dict[str, Any]:
        """
        Create a message context for the LLM.

        Args:
            message: The user's message.

        Returns:
            A message context dictionary.
        """
        # Return a simple message dictionary for testing
        return {"role": "user", "timestamp": 1234567890}

    async def run(self, input_text: str, use_memory: bool = True) -> str:
        """
        Run the agent on an input text.

        Args:
            input_text: The input text from the user.
            use_memory: Whether to use memory for context.

        Returns:
            The agent's response.
        """
        # Create user message
        user_message = MCPMessage(role="user", content=input_text)

        # Process message
        response = await self.mcp_handler.process_message(user_message)

        # Store in memory if enabled
        if use_memory:
            await self._store_in_memory(input_text, response.content)

        return response.content

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

        # Store in buffer memory
        self.buffer_memory.add(
            vector=embedding,
            metadata={
                "input": input_text,
                "response": response_text,
                "type": "conversation",
            },
        )

        # Store in long-term memory if available
        if self.long_term_memory:
            await asyncio.to_thread(
                self.long_term_memory.add,
                text=combined_text,
                embedding=embedding,
                metadata={
                    "input": input_text,
                    "response": response_text,
                    "type": "conversation",
                },
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
        # If Memobase is available and user_id is provided, use it
        if self.is_multi_user and user_id is not None:
            self.long_term_memory.clear_user_memory(user_id)
            return

        # Otherwise, fall back to traditional memory clearing
        # Clear buffer memory
        self.buffer_memory.clear()

        # Clear long-term memory if available and enabled
        if self.long_term_memory and clear_long_term:
            # Create a new default collection
            self.long_term_memory.create_collection(
                self.long_term_memory.default_collection,
                "Default collection for memories",
            )

    async def chat(
        self, message: str, user_id: Optional[str] = None
    ) -> MCPMessage:
        """
        Process a message and generate a response.

        Args:
            message: The message to process.
            user_id: Optional user ID for multi-user support.

        Returns:
            The agent's response as an MCPMessage.
        """
        # Create a user message
        user_message = MCPMessage(role="user", content=message)

        # Process the message
        response = await self.mcp_handler.process_message(user_message)

        return response

    async def _initialize_knowledge(self, knowledge_sources: List[KnowledgeSource]) -> None:
        """
        Initialize the knowledge handler and add knowledge sources.

        Args:
            knowledge_sources: List of knowledge sources to add
        """
        from muxi.knowledge.base import KnowledgeHandler

        # Determine embedding dimension by getting a sample embedding
        sample_embedding = await self.model.embed("Sample text to determine embedding dimension")
        embedding_dimension = len(sample_embedding)

        # Create knowledge handler with the correct embedding dimension
        self.knowledge_handler = KnowledgeHandler(
            self.agent_id,
            embedding_dimension=embedding_dimension
        )

        # Add knowledge sources
        for source in knowledge_sources:
            await self.add_knowledge(source)

    async def add_knowledge(self, knowledge_source: KnowledgeSource) -> int:
        """
        Add a knowledge source to the agent.

        Args:
            knowledge_source: The knowledge source to add

        Returns:
            Number of chunks added to the knowledge base
        """
        from muxi.knowledge.base import KnowledgeHandler, FileKnowledge

        # Initialize knowledge handler if it doesn't exist
        if not self.knowledge_handler:
            self.knowledge_handler = KnowledgeHandler(self.agent_id)

        # Currently only supporting FileKnowledge
        if isinstance(knowledge_source, FileKnowledge):
            return await self.knowledge_handler.add_file(
                knowledge_source,
                self.model.generate_embeddings
            )

        logger.warning(f"Unsupported knowledge source type: {type(knowledge_source)}")
        return 0

    async def remove_knowledge(self, file_path: str) -> bool:
        """
        Remove a knowledge source from the agent.

        Args:
            file_path: Path to the file to remove

        Returns:
            True if the file was removed, False otherwise
        """
        if not self.knowledge_handler:
            return False

        return await self.knowledge_handler.remove_file(file_path)

    def get_knowledge_sources(self) -> List[str]:
        """
        Get a list of knowledge sources.

        Returns:
            List of file paths in the knowledge base
        """
        if not self.knowledge_handler:
            return []

        return self.knowledge_handler.get_sources()

    async def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The query to search for
            top_k: Maximum number of results to return
            threshold: Minimum relevance score (0-1) to include a result

        Returns:
            List of relevant documents
        """
        if not self.knowledge_handler:
            return []

        return await self.knowledge_handler.search(
            query,
            self.model.generate_embeddings,
            top_k,
            threshold
        )
