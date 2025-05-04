# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Agent - AI Agent Implementation
# Description:  Core implementation of AI agents with memory and tool use
# Role:         Primary interface for language model interactions
# Usage:        Created and managed by the Orchestrator to process user messages
# Author:       Muxi Framework Team
#
# The Agent class is a fundamental component in the Muxi framework that:
#
# 1. Handles Direct Interactions
#    - Processes user messages and generates responses
#    - Maintains conversation context for coherent exchanges
#    - Integrates with memory systems for contextual awareness
#
# 2. Tool Integration
#    - Connects to external tools via MCP (Model Control Protocol)
#    - Parses and processes tool calls from language model responses
#    - Manages tool invocation and result incorporation
#
# 3. Memory Usage
#    - Delegates memory storage to the orchestrator
#    - Retrieves relevant context from memory systems
#    - Works with orchestrator for information extraction
#
# Agents are typically created and managed by the Orchestrator:
#
# Programmatic creation:
#   agent = orchestrator.create_agent(
#       agent_id="assistant",
#       model=model,
#       system_message="You are a helpful assistant."
#   )
#
# Direct usage:
#   response = await agent.process_message("Hello, how can you help me?")
#
# This file defines both the Agent class and the supporting MCPServer class
# for external tool integration.
# =============================================================================

import datetime
import uuid
from typing import Any, Dict, List, Optional, Union

from muxi.core.mcp import MCPMessage, ToolParser, MCPService
from muxi.core.models.base import BaseModel


# Simple class to represent an MCP server
class MCPServer:
    """
    Represents a connected MCP server.

    This class encapsulates the configuration for connecting to an external MCP
    (Model Control Protocol) server that provides tool functionality to agents.
    """

    def __init__(
        self,
        name: str,
        url: str,
        credentials: Optional[Dict[str, Any]] = None,
        request_timeout: int = 60,
    ):
        """
        Initialize an MCP server configuration.

        Args:
            name: The name of the server. Used for human-readable identification
                and generating the server_id.
            url: The URL of the server. Endpoint where MCP requests will be sent.
            credentials: Optional credentials for authentication with the server.
                Format depends on the server's requirements.
            request_timeout: Timeout in seconds for requests to this server.
                Controls how long to wait before considering a request failed.
        """
        self.name = name
        self.url = url
        self.credentials = credentials or {}
        self.server_id = f"server_{name.lower().replace(' ', '_')}"
        self.request_timeout = request_timeout


class Agent:
    """
    An agent that interacts with users and tools.

    The Agent class manages interactions between users and language models,
    using its orchestrator's memory systems for context retention and retrieval.
    It can process messages, invoke tools via MCP, and maintain conversation state.
    """

    def __init__(
        self,
        model: BaseModel,
        orchestrator: Any,  # Forward reference to Orchestrator
        system_message: Optional[str] = None,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        mcp_server: Optional[MCPServer] = None,
        request_timeout: Optional[int] = None,
    ):
        """
        Initialize the agent with a model, orchestrator, and optional parameters.

        Args:
            model: The language model for the agent to use. This model handles
                the core intelligence of the agent.
            orchestrator: The orchestrator that manages this agent. Provides
                access to memory systems and coordinates multi-agent systems.
            system_message: Optional system message to set the agent's behavior
                and persona. Defines the agent's role and capabilities.
            agent_id: Optional unique ID for the agent. If None, generates a UUID.
                Used for identification in memory systems and routing.
            name: Optional name for the agent (e.g., "Customer Service Bot").
                Used for display purposes.
            mcp_server: Optional MCP server for tool calling and external integrations.
                Enables the agent to use external tools.
            request_timeout: Optional timeout in seconds for MCP requests.
                Defaults to orchestrator's timeout if not specified.
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
        elif hasattr(orchestrator, "request_timeout"):
            self.request_timeout = orchestrator.request_timeout
        else:
            self.request_timeout = 60  # Default fallback

        # Set up MCP service access
        self._mcp_service = MCPService.get_instance()

        # Initialize the context with system message
        self._messages = []
        if self.system_message:
            self._messages.append({"role": "system", "content": self.system_message})

    def get_mcp_service(self) -> MCPService:
        """
        Get the centralized MCP service for tool integrations.

        Returns:
            The MCPService instance used by this agent for connecting to
            and interacting with external tools.
        """
        return self._mcp_service

    async def process_message(
        self, message: Union[str, MCPMessage], user_id: Optional[int] = None
    ) -> MCPMessage:
        """
        Process a message from the user and generate a response.

        This method handles:
        1. Converting input to MCPMessage format
        2. Adding the message to memory via the orchestrator
        3. Updating conversation context
        4. Processing the message with the model
        5. Handling any tool calls in the response
        6. Storing the response in memory

        Args:
            message: The message from the user, either as a string or an MCPMessage.
                Contains the content to be processed by the agent.
            user_id: Optional user ID for multi-user support. Used for memory
                isolation and user-specific context.

        Returns:
            The agent's response as an MCPMessage, possibly including tool call results.
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
                user_id=user_id,
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
                        parameters=tool_call.parameters,
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
                    "content": str(tool_call.result),
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
                user_id=user_id,
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
                agent_id=self.agent_id,
            )

        return response

    async def run(self, input_text: str, use_memory: bool = True) -> str:
        """
        Run the agent with the given input text and return a text response.

        This is a simplified interface that handles:
        1. Retrieving relevant context from memory (if use_memory=True)
        2. Processing the input with context
        3. Returning just the text content of the response

        Args:
            input_text: The input text to process. The user's message or query.
            use_memory: Whether to use memory for context enhancement. When True,
                relevant memories will be retrieved and included in the prompt.

        Returns:
            The agent's response as a plain text string.
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
        Get relevant memories for a user query from the orchestrator's memory systems.

        Args:
            query: The user query to find relevant memories for. Used for semantic
                search to find related context.
            limit: Maximum number of memories to retrieve. Controls the amount of
                context included.

        Returns:
            A list of relevant memories, each as a dictionary with metadata.
            Returns an empty list if memory retrieval is not available.
        """
        if not self.orchestrator or not hasattr(self.orchestrator, "search_buffer_memory"):
            return []

        memories = self.orchestrator.search_buffer_memory(
            query=query, limit=limit, agent_id=self.agent_id
        )

        return memories

    async def invoke_tool(
        self, server_id: str, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke a tool on a connected MCP server.

        This method sends a tool call to an external MCP server and returns the result.
        It handles the communication details and error handling.

        Args:
            server_id: The server ID to send the tool call to. Identifies which
                MCP server should handle the request.
            tool_name: The name of the tool to call. Must match a tool provided
                by the target MCP server.
            parameters: The parameters to pass to the tool. Must match the
                expected parameters for the specified tool.

        Returns:
            The result of the tool call as a dictionary.

        Raises:
            ValueError: If server_id is not valid
            Exception: Any error from the MCP service during tool invocation
        """
        if not server_id:
            raise ValueError("Invalid server_id provided")

        return await self._mcp_service.invoke_tool(
            server_id=server_id,
            tool_name=tool_name,
            parameters=parameters,
            request_timeout=self.request_timeout,
        )
