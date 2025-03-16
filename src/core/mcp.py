"""
Model Context Protocol (MCP) implementation.

This module provides functionality for communicating with language models using the
Model Context Protocol (MCP) as defined at https://modelcontextprotocol.io/.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from loguru import logger

from src.models.base import BaseModel


@dataclass
class MCPToolCall:
    """Tool call information for MCP messages."""

    tool_name: str
    tool_id: str
    tool_args: Dict[str, Any]


class MCPMessage:
    """
    Represents a message in the Model Context Protocol.
    """

    def __init__(
        self,
        role: str,
        content: Union[str, Dict[str, Any], None],
        name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[MCPToolCall]] = None,
        tool_call_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ):
        """
        Initialize an MCP message.

        Args:
            role: The role of the message sender (e.g., "user", "assistant",
                "system", "tool").
            content: The content of the message. Can be a string or a
                structured object.
            name: Optional name for the sender (used for tools).
            context: Optional context information for the message.
            tool_calls: Optional list of tool calls in the message.
            tool_call_id: Optional ID of the tool call this message responds to.
            agent_id: Optional ID of the agent that generated this response.
        """
        self.role = role
        self.content = content
        self.name = name
        self.context = context or {}
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id
        self.agent_id = agent_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary representation.

        Returns:
            A dictionary representation of the message.
        """
        message = {"role": self.role, "content": self.content}

        if self.name:
            message["name"] = self.name

        if self.context:
            message["context"] = self.context

        if self.agent_id:
            message["agent_id"] = self.agent_id

        return message

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """
        Create a message from a dictionary representation.

        Args:
            data: The dictionary representation of the message.

        Returns:
            An MCPMessage instance.
        """
        return cls(
            role=data["role"],
            content=data["content"],
            name=data.get("name"),
            context=data.get("context", {}),
            tool_calls=[MCPToolCall(**tool_call) for tool_call in data.get("tool_calls", [])],
            tool_call_id=data.get("tool_call_id"),
            agent_id=data.get("agent_id"),
        )


class MCPContext:
    """
    Represents the context for an MCP interaction.
    """

    def __init__(
        self,
        messages: Optional[List[MCPMessage]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize an MCP context.

        Args:
            messages: The conversation history.
            metadata: Additional metadata for the context.
            tools: Available tools for the LLM to use.
        """
        self.messages = messages or []
        self.metadata = metadata or {}
        self.tools = tools or []

    def add_message(self, message: MCPMessage) -> None:
        """
        Add a message to the context.

        Args:
            message: The message to add.
        """
        self.messages.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary representation.

        Returns:
            A dictionary representation of the context.
        """
        return {
            "messages": [m.to_dict() for m in self.messages],
            "metadata": self.metadata,
            "tools": self.tools,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPContext":
        """
        Create a context from a dictionary representation.

        Args:
            data: The dictionary representation of the context.

        Returns:
            An MCPContext instance.
        """
        messages = [MCPMessage.from_dict(m) for m in data.get("messages", [])]

        return cls(
            messages=messages, metadata=data.get("metadata", {}), tools=data.get("tools", [])
        )


class MCPHandler:
    """
    Handles communication with LLMs using the Model Context Protocol.
    """

    def __init__(self, model: BaseModel, tool_handlers: Optional[Dict[str, Callable]] = None):
        """
        Initialize an MCP handler.

        Args:
            model: The language model to use for generating responses.
            tool_handlers: A dictionary mapping tool names to handler
                functions.
        """
        self.model = model
        self.tool_handlers = tool_handlers or {}
        self.context = MCPContext()

    async def process_message(
        self, message: MCPMessage, context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        Process a message and generate a response.

        Args:
            message: The message to process.
            context: Optional context to use. If None, the handler's context
                will be used.

        Returns:
            The response message.
        """
        # Use provided context or the handler's context
        ctx = context or self.context

        # Add message to context
        ctx.add_message(message)

        # Convert context to a format suitable for the language model
        model_messages = self._context_to_model_messages(ctx)

        # Generate a response
        response_content = await self.model.chat(model_messages)

        # Create a response message
        response = MCPMessage(
            role="assistant",
            content=response_content,
        )

        # Add response to context
        ctx.add_message(response)

        return response

    async def process_tool_call(
        self, tool_name: str, tool_input: Dict[str, Any], context: Optional[MCPContext] = None
    ) -> MCPMessage:
        """
        Process a tool call and generate a response.

        Args:
            tool_name: The name of the tool to call.
            tool_input: The input to the tool.
            context: Optional context to use. If None, the handler's context
                will be used.

        Returns:
            The response message.
        """
        # Use provided context or the handler's context
        ctx = context or self.context

        # Create a tool call message
        tool_call_message = MCPMessage(
            role="function",
            content="",
            name=tool_name,
            metadata={"input": tool_input}
        )

        # Add the tool call message to the context
        ctx.add_message(tool_call_message)

        # Check if we have a handler for this tool
        if tool_name not in self.tool_handlers:
            error_message = f"No handler for tool: {tool_name}"
            logger.error(error_message)

            # Create an error response
            response = MCPMessage(response=f"Error: {error_message}")

            # Add the response to the context
            ctx.add_message(response)

            return response

        try:
            # Call the tool handler
            handler = self.tool_handlers[tool_name]
            result = await handler(tool_input)

            # Create a response message
            response = MCPMessage(
                role="assistant",
                content=result,
            )

            # Add the response to the context
            ctx.add_message(response)

            return response
        except Exception as e:
            error_message = f"Error calling tool {tool_name}: {str(e)}"
            logger.error(error_message)

            # Create an error response
            response = MCPMessage(response=f"Error: {error_message}")

            # Add the response to the context
            ctx.add_message(response)

            return response

    def _context_to_model_messages(self, context: MCPContext) -> List[Dict[str, str]]:
        """
        Convert an MCP context to a format suitable for the language model.

        Args:
            context: The MCP context to convert.

        Returns:
            A list of messages in the format expected by the language model.
        """
        model_messages = []

        for message in context.messages:
            model_message = {
                "role": message.role,
                "content": message.content,
            }

            if message.name:
                model_message["name"] = message.name

            if message.context:
                model_message["context"] = message.context

            model_messages.append(model_message)

        return model_messages

    def register_tool_handler(self, tool_name: str, handler: Callable) -> None:
        """
        Register a handler for a tool.

        Args:
            tool_name: The name of the tool.
            handler: The handler function for the tool.
        """
        self.tool_handlers[tool_name] = handler

    def clear_context(self) -> None:
        """
        Clear the context.
        """
        self.context = MCPContext()

    def set_context(self, context: MCPContext) -> None:
        """
        Set the context.

        Args:
            context: The context to set.
        """
        self.context = context
