"""
Updated Agent implementation that uses the orchestrator's memory.

This module provides the Agent class, which utilizes memory systems
managed by its parent orchestrator.
"""

import datetime
import uuid
from typing import Any, Dict, List, Optional, Union

from muxi.core.mcp import MCPMessage
from muxi.core.mcp_service import MCPService
from muxi.core.tool_parser import ToolParser
from muxi.models.base import BaseModel
from muxi.knowledge.base import KnowledgeSource


# Simple class to represent an MCP server
class MCPServer:
    """Represents a connected MCP server."""

    def __init__(
        self,
        name: str,
        url: str,
        credentials: Optional[Dict[str, Any]] = None,
        request_timeout: int = 60
    ):
        """
        Initialize an MCP server.

        Args:
            name: The name of the server
            url: The URL of the server
            credentials: Optional credentials for authentication
            request_timeout: Timeout in seconds for requests to this server
        """
        self.name = name
        self.url = url
        self.credentials = credentials or {}
        self.server_id = f"server_{name.lower().replace(' ', '_')}"
        self.request_timeout = request_timeout


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
        mcp_server: Optional[MCPServer] = None,
        knowledge_sources: Optional[List[KnowledgeSource]] = None,
        request_timeout: Optional[int] = None,
    ):
        """
        Initialize the agent with a model, orchestrator, and optional parameters.

        Args:
            model: The language model for the agent to use.
            orchestrator: The orchestrator that manages this agent.
            system_message: Optional system message to set the agent's behavior.
            agent_id: Optional unique ID for the agent. If None, generates a UUID.
            name: Optional name for the agent (e.g., "Customer Service Bot").
            mcp_server: Optional MCP server for tool calling and external integrations.
            knowledge_sources: Optional list of knowledge sources to augment the agent.
            request_timeout: Optional timeout in seconds for MCP requests
                (default: use orchestrator's timeout).
        """
        self.model = model
        self.orchestrator = orchestrator

        # Set up agent identification
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent-{self.agent_id}"

        # Set up system message
        self.system_message = system_message or (
            "You are a helpful assistant that responds accurately to user queries. "
            "Provide detailed, factual responses and be transparent about uncertainty."
        )

        # Set up MCP integration
        self.mcp_server = mcp_server

        # Set request timeout (use orchestrator's if not specified)
        if request_timeout is not None:
            self.request_timeout = request_timeout
        elif hasattr(orchestrator, 'request_timeout'):
            self.request_timeout = orchestrator.request_timeout
        else:
            self.request_timeout = 60  # Default fallback

        # Set up knowledge sources
        self.knowledge_sources = knowledge_sources or []

        # Set up MCP service access
        self._mcp_service = MCPService.get_instance()

        # Initialize the context with system message
        self._messages = []
        if self.system_message:
            self._messages.append({"role": "system", "content": self.system_message})

    def get_mcp_service(self) -> MCPService:
        """
        Get the centralized MCP service.

        Returns:
            The MCP service instance
        """
        return self._mcp_service

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
            message_obj = MCPMessage(role="user", content=content)
        else:
            content = message.content
            message_obj = message

        # Let orchestrator handle memory management
        timestamp = datetime.datetime.now().timestamp()
        if self.orchestrator and hasattr(self.orchestrator, "add_message_to_memory"):
            await self.orchestrator.add_message_to_memory(
                content=content,
                role="user",
                timestamp=timestamp,
                agent_id=self.agent_id,
                user_id=user_id
            )

        # Add message to conversation context
        self._messages.append({"role": "user", "content": message_obj.content})

        # Process the message with the model directly
        raw_response = await self.model.chat(self._messages)

        # Parse the response to detect and handle tool calls
        cleaned_text, tool_calls = ToolParser.parse(raw_response)

        # If tool calls were found, process them
        if tool_calls and self.mcp_server:
            # Process each tool call
            for tool_call in tool_calls:
                try:
                    # Use the server_id from the MCP server configuration
                    server_id = self.mcp_server.server_id

                    # Invoke the tool using the MCP service
                    result = await self.invoke_tool(
                        server_id=server_id,
                        tool_name=tool_call.tool_name,
                        parameters=tool_call.parameters
                    )

                    # Store the result with the tool call
                    tool_call.set_result(result)
                except Exception as e:
                    error_msg = f"Error processing tool call {tool_call.tool_name}: {str(e)}"
                    tool_call.set_result({"error": error_msg, "status": "error"})

            # Replace tool calls with results in the response
            final_content = ToolParser.replace_tool_calls_with_results(raw_response, tool_calls)

            # Add an entry to the conversation history for each tool call
            for tool_call in tool_calls:
                tool_info = {
                    "role": "function",
                    "name": tool_call.tool_name,
                    "content": str(tool_call.result)
                }
                self._messages.append(tool_info)
        else:
            # No tool calls found, use the raw response
            final_content = raw_response

        # Create response message
        response = MCPMessage(role="assistant", content=final_content)

        # Add response to conversation context
        self._messages.append({"role": "assistant", "content": response.content})

        # Let orchestrator handle memory management for the response
        if self.orchestrator and hasattr(self.orchestrator, "add_message_to_memory"):
            timestamp = datetime.datetime.now().timestamp()
            await self.orchestrator.add_message_to_memory(
                content=response.content,
                role="assistant",
                timestamp=timestamp,
                agent_id=self.agent_id,
                user_id=user_id
            )

        # User information extraction is handled by the orchestrator
        if (
            user_id is not None
            and user_id != 0  # Skip extraction for anonymous users
            and self.orchestrator
            and hasattr(self.orchestrator, "handle_user_information_extraction")
        ):
            # Process this conversation turn for user information extraction
            await self.orchestrator.handle_user_information_extraction(
                user_message=content,
                agent_response=response.content,
                user_id=user_id,
                agent_id=self.agent_id
            )

        return response

    async def run(self, input_text: str, use_memory: bool = True) -> str:
        """
        Run the agent with the given input text.

        Args:
            input_text: The input text to process.
            use_memory: Whether to use memory for context.

        Returns:
            The agent's response text.
        """
        # Initialize context
        context = ""

        # Retrieve relevant memories if requested
        if use_memory:
            memories = await self.get_relevant_memories(input_text)
            if memories:
                memory_text = "\n".join([mem["text"] for mem in memories])
                context = f"Previous conversation context:\n{memory_text}\n\n"

        # Combine context with input
        full_input = f"{context}User: {input_text}"

        # Process with the model
        response = await self.process_message(full_input)

        return response.content

    async def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant memories for a user query.

        Args:
            query: The user query to find relevant memories for.
            limit: Maximum number of memories to retrieve.

        Returns:
            A list of relevant memories.
        """
        if not self.orchestrator or not hasattr(self.orchestrator, "search_buffer_memory"):
            return []

        memories = self.orchestrator.search_buffer_memory(
            query=query,
            limit=limit,
            agent_id=self.agent_id
        )

        return memories

    async def invoke_tool(
        self,
        server_id: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke a tool on a connected MCP server.

        Args:
            server_id: The server ID to send the tool call to
            tool_name: The name of the tool to call
            parameters: The parameters to pass to the tool

        Returns:
            The result of the tool call

        Raises:
            ValueError: If server_id is not valid
            Exception: Any error from the MCP service
        """
        if not server_id:
            raise ValueError("Invalid server_id provided")

        return await self._mcp_service.invoke_tool(
            server_id=server_id,
            tool_name=tool_name,
            parameters=parameters,
            request_timeout=self.request_timeout
        )
