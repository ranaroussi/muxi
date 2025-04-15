"""
Updated Agent implementation that uses the orchestrator's memory.

This module provides the Agent class, which utilizes memory systems
managed by its parent orchestrator.
"""

import datetime
import uuid
from typing import Any, Dict, List, Optional, Set, Union

from loguru import logger

from muxi.core.mcp import MCPMessage
from muxi.models.base import BaseModel
from muxi.knowledge.base import KnowledgeSource


# Simple class to represent an MCP server
class MCPServer:
    """Represents a connected MCP server."""

    def __init__(self, name: str, url: str, credentials: Optional[Dict[str, Any]] = None):
        """
        Initialize an MCP server.

        Args:
            name: The name of the server
            url: The URL of the server
            credentials: Optional credentials for authentication
        """
        self.name = name
        self.url = url
        self.credentials = credentials or {}


class Agent:
    """
    An agent that interacts with users and tools.

    Uses its orchestrator's memory for context retention and retrieval.
    """

    def __init__(
        self,
        model: BaseModel,
        orchestrator: Any,  # Forward reference to Orchestrator
        system_message: Optional[str] = None,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        knowledge: Optional[List[KnowledgeSource]] = None,
    ):
        """
        Initialize an agent.

        Args:
            model: The language model to use for generating responses.
            orchestrator: The orchestrator managing this agent, providing memory access.
            system_message: Optional system message to set the agent's behavior.
            agent_id: Optional unique identifier for the agent.
            name: Optional name for the agent.
            knowledge: Optional list of knowledge sources for the agent.
        """
        self.model = model
        self.orchestrator = orchestrator
        self.name = name or "AI Assistant"
        self.agent_id = agent_id or str(uuid.uuid4())

        self.system_message = system_message or (
            "You are a helpful AI assistant."
        )

        # Initialize knowledge handler if knowledge sources are provided
        self.knowledge_handler = None
        if knowledge:
            # Initialize knowledge handler synchronously
            from muxi.knowledge.handler import KnowledgeHandler
            sources_len = len(knowledge) if knowledge else 0
            self.knowledge_handler = KnowledgeHandler(
                knowledge_sources=knowledge if knowledge else None,
                agent_id=self.agent_id if not knowledge else None
            )
            logger.info(f"Initialized knowledge handler with {sources_len} sources")

            # Store knowledge sources for async processing later
            self._pending_knowledge_sources = knowledge

        # Initialize MCP handler with no tools - we'll use MCP servers instead
        from muxi.core.mcp_handler import MCPHandler
        self.mcp_handler = MCPHandler(self.model)
        # Update system message in MCP handler if method exists
        if hasattr(self.mcp_handler, 'set_system_message'):
            self.mcp_handler.set_system_message(self.system_message)

        # Keep track of connected MCP servers
        self.mcp_servers = []
        self._active_mcp_servers: Set[MCPServer] = set()

    async def _initialize_knowledge(self, knowledge_sources: List[KnowledgeSource]) -> None:
        """
        Initialize knowledge sources for the agent.

        Args:
            knowledge_sources: List of knowledge sources to initialize.
        """
        from muxi.knowledge.handler import KnowledgeHandler
        # Initialize with either knowledge sources or agent_id
        sources_len = len(knowledge_sources) if knowledge_sources else 0
        self.knowledge_handler = KnowledgeHandler(
            knowledge_sources=knowledge_sources if knowledge_sources else None,
            agent_id=self.agent_id if not knowledge_sources else None
        )
        logger.info(f"Initialized knowledge handler with {sources_len} sources")

        # Initialize with any pending sources
        has_pending = hasattr(self.knowledge_handler, "_pending_sources")
        sources = self.knowledge_handler._pending_sources if has_pending else []

        if has_pending and sources:
            for source in sources:
                await self.add_knowledge(source)

    async def initialize_pending_knowledge(self) -> None:
        """Process any pending knowledge sources that were provided during initialization."""
        if hasattr(self, '_pending_knowledge_sources') and self._pending_knowledge_sources:
            for source in self._pending_knowledge_sources:
                await self.add_knowledge(source)
            delattr(self, '_pending_knowledge_sources')

    @property
    def buffer_memory(self):
        """Returns orchestrator's buffer memory."""
        return self.orchestrator.buffer_memory if self.orchestrator else None

    @property
    def long_term_memory(self):
        """Returns orchestrator's long-term memory."""
        return self.orchestrator.long_term_memory if self.orchestrator else None

    @property
    def is_multi_user(self):
        """Returns whether long-term memory is multi-user."""
        if self.orchestrator and hasattr(self.orchestrator, "is_multi_user"):
            return self.orchestrator.is_multi_user
        return False

    def use_mcp_server(self, mcp_server: MCPServer) -> None:
        """
        Configure the agent to use an MCP server.

        Args:
            mcp_server: The MCP server to use.
        """
        self.mcp_servers.append(mcp_server)

    async def process_message(
        self, message: Union[str, MCPMessage], user_id: Optional[int] = None
    ) -> MCPMessage:
        """
        Process a message from the user.

        Args:
            message: The message from the user (string or MCPMessage).
            user_id: Optional user ID for multi-user support.

        Returns:
            The agent's response as an MCPMessage.
        """
        # Convert string message to MCPMessage if needed
        if isinstance(message, str):
            content = message
            # Enhance message with context memory if available
            enhanced_message = await self._enhance_with_context_memory(content, user_id)
            message = MCPMessage(role="user", content=enhanced_message)
        else:
            content = message.content
            # Store original content before processing
            timestamp = datetime.datetime.now().timestamp()

            # Add message to buffer memory through orchestrator
            if self.orchestrator and hasattr(self.orchestrator, "add_to_buffer_memory"):
                self.orchestrator.add_to_buffer_memory(
                    message=content,
                    metadata={"role": "user", "timestamp": timestamp},
                    agent_id=self.agent_id
                )

            # If using multi-user memory, also store there with user context
            if self.is_multi_user and user_id is not None and self.orchestrator:
                await self.orchestrator.add_to_long_term_memory(
                    content=content,
                    metadata={"role": "user", "timestamp": timestamp},
                    agent_id=self.agent_id,
                    user_id=user_id
                )

        # Process the message using the MCP handler
        # This will handle tool calls automatically if the model's response includes them
        response = await self.mcp_handler.process_message(message)

        # Store assistant response in memory through orchestrator
        if self.orchestrator and hasattr(self.orchestrator, "add_to_buffer_memory"):
            timestamp = datetime.datetime.now().timestamp()
            self.orchestrator.add_to_buffer_memory(
                message=response.content,
                metadata={"role": "assistant", "timestamp": timestamp},
                agent_id=self.agent_id
            )

        # Also store in long-term memory if multi-user
        if self.is_multi_user and user_id is not None and self.orchestrator:
            timestamp = datetime.datetime.now().timestamp()
            await self.orchestrator.add_to_long_term_memory(
                content=response.content,
                metadata={"role": "assistant", "timestamp": timestamp},
                agent_id=self.agent_id,
                user_id=user_id
            )

        return response

    async def run(self, input_text: str, use_memory: bool = True) -> str:
        """
        Run the agent with the given input text.

        Args:
            input_text: The text to process.
            use_memory: Whether to use memory for retrieving context.

        Returns:
            The agent's response as a string.
        """
        # Get relevant memories if enabled
        context = ""
        if use_memory:
            memories = await self.get_relevant_memories(input_text)
            if memories:
                memory_text = "\n".join([mem["text"] for mem in memories])
                context = f"Previous conversation context:\n{memory_text}\n\n"

        # Combine context with input
        full_input = f"{context}User: {input_text}"

        # Process with MCP to handle any tool calls
        response = await self.process_message(full_input)

        # Store the interaction in memory for future reference
        await self._store_in_memory(input_text, response.content)

        return response.content

    async def _store_in_memory(self, input_text: str, response_text: str) -> None:
        """
        Store the interaction in memory.

        Args:
            input_text: The input text from the user.
            response_text: The response text from the agent.
        """
        if not self.orchestrator:
            return

        # Create combined text for embedding
        combined_text = f"User: {input_text}\nAssistant: {response_text}"

        # Get embedding if model supports it
        embedding = None
        if hasattr(self.model, 'embed'):
            embedding = await self.model.embed(combined_text)

        # Store metadata
        metadata = {
            "input": input_text,
            "response": response_text,
            "type": "conversation",
        }

        # Store in orchestrator's buffer memory
        if hasattr(self.orchestrator, "add_to_buffer_memory"):
            msg = combined_text if embedding is None else embedding
            self.orchestrator.add_to_buffer_memory(
                message=msg,
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

    def clear_memory(self, clear_long_term: bool = False, user_id: Optional[int] = None) -> None:
        """
        Clear the agent's memory.

        Args:
            clear_long_term: Whether to clear long-term memory as well.
            user_id: Optional user ID for multi-user support.
        """
        if not self.orchestrator:
            return

        # Use orchestrator's memory clearing
        if hasattr(self.orchestrator, "clear_memory"):
            self.orchestrator.clear_memory(
                clear_long_term=clear_long_term,
                agent_id=self.agent_id,
                user_id=user_id
            )

    async def get_relevant_memories(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories relevant to the given query.

        Args:
            query: The query to search for.
            k: The maximum number of memories to return.

        Returns:
            A list of relevant memory items.
        """
        # Only use orchestrator's search method
        if self.orchestrator and hasattr(self.orchestrator, "search_memory"):
            return await self.orchestrator.search_memory(
                query=query,
                agent_id=self.agent_id,
                k=k
            )
        return []

    async def connect_mcp_server(
        self,
        name: str,
        url: str,
        credentials: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Connect to an MCP server to access tools.

        This method integrates with MCP servers that provide tools for the agent.

        Args:
            name: The name to assign to the server connection.
            url: The URL of the MCP server.
            credentials: Optional credentials for authentication.

        Returns:
            True if connected successfully, False otherwise.
        """
        try:
            # Import MCPHandler for MCP server connections
            from muxi.core.mcp_handler import MCPHandler

            # Create MCP client if it doesn't exist yet
            if not hasattr(self, 'mcp_handler'):
                self.mcp_handler = MCPHandler(self.model)

            # Connect to the MCP server
            await self.mcp_handler.connect(name, url, credentials or {})

            # Add to active servers
            server = MCPServer(name=name, url=url)
            self._active_mcp_servers.add(server)

            logger.info(f"Connected to MCP server '{name}' at {url}")
            return True

        except Exception as e:
            logger.error(f"Error connecting to MCP server '{name}': {str(e)}")
            return False

    async def disconnect_mcp_server(self, name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            name: The name of the server connection to disconnect.

        Returns:
            True if disconnected successfully, False otherwise.
        """
        if not hasattr(self, 'mcp_handler'):
            logger.warning(f"No MCP handler to disconnect from server '{name}'")
            return False

        try:
            await self.mcp_handler.disconnect(name)

            # Remove from active servers
            self._active_mcp_servers = {
                server for server in self._active_mcp_servers
                if server.name != name
            }

            logger.info(f"Disconnected from MCP server '{name}'")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server '{name}': {str(e)}")
            return False

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
        # Skip if any required component is missing
        if not self.orchestrator:
            return message
        if not self.long_term_memory:
            return message
        if user_id is None:
            return message
        if not self.is_multi_user:
            return message

        try:
            # Get context memory for the user via orchestrator
            if hasattr(self.orchestrator, "get_user_context_memory"):
                knowledge = await self.orchestrator.get_user_context_memory(
                    user_id=user_id,
                    agent_id=self.agent_id
                )
            else:
                # Fallback to direct access if orchestrator doesn't have the method
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
            logger.error(f"Error enhancing message with context memory: {e}")
            return message

    # Knowledge-related methods
    async def add_knowledge(self, knowledge_source: KnowledgeSource) -> int:
        """
        Add a knowledge source to the agent.

        Args:
            knowledge_source: The knowledge source to add.

        Returns:
            Number of chunks added to the knowledge base.
        """
        # Initialize knowledge handler if not already created
        if self.knowledge_handler is None:
            from muxi.knowledge.handler import KnowledgeHandler
            self.knowledge_handler = KnowledgeHandler(self.agent_id)
            logger.info(f"Initialized knowledge handler for agent {self.agent_id}")

        # Add knowledge to handler
        if hasattr(self.model, 'generate_embeddings'):
            return await self.knowledge_handler.add_file(
                knowledge_source, self.model.generate_embeddings
            )
        elif hasattr(self.model, 'embed'):
            # Adapt the embed method to match generate_embeddings signature
            async def generate_embeddings_adapter(texts):
                return [await self.model.embed(text) for text in texts]

            return await self.knowledge_handler.add_file(
                knowledge_source, generate_embeddings_adapter
            )
        else:
            logger.error("Model does not support embeddings, cannot add knowledge")
            return 0

    async def remove_knowledge(self, file_path: str) -> bool:
        """
        Remove a knowledge source from the agent.

        Args:
            file_path: Path to the file to remove.

        Returns:
            True if the file was removed, False otherwise.
        """
        if self.knowledge_handler is None:
            return False

        return await self.knowledge_handler.remove_file(file_path)

    def get_knowledge_sources(self) -> List[str]:
        """
        Get a list of knowledge sources.

        Returns:
            List of file paths in the knowledge base.
        """
        if self.knowledge_handler is None:
            return []

        return self.knowledge_handler.get_sources()

    async def search_knowledge(
        self, query: str, top_k: int = 5, threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The query to search for.
            top_k: Maximum number of results to return.
            threshold: Minimum relevance score (0-1) to include a result.

        Returns:
            List of relevant documents.
        """
        if self.knowledge_handler is None:
            return []

        # Use the appropriate embedding function
        if hasattr(self.model, 'generate_embeddings'):
            return await self.knowledge_handler.search(
                query, self.model.generate_embeddings, top_k, threshold
            )
        elif hasattr(self.model, 'embed'):
            return await self.knowledge_handler.search(
                query, self.model.embed, top_k, threshold
            )
        else:
            logger.error("Model does not support embeddings, cannot search knowledge")
            return []
