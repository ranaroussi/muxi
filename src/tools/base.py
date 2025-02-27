"""
Base tool class for the agent framework.

This module provides the abstract base class for tools that can be used by
agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseTool(ABC):
    """
    Abstract base class for tools.

    Tools are components that provide specific capabilities to agents, such as
    performing calculations, searching the web, or interacting with external
    APIs.
    """

    @property
    def name(self) -> str:
        """
        Return the name of the tool.

        This property must be implemented by all subclasses.
        """
        raise AttributeError("Tool must define a name property")

    @property
    def description(self) -> str:
        """
        Return a description of the tool.

        This property must be implemented by all subclasses.
        """
        raise AttributeError("Tool must define a description property")

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the provided parameters.

        Args:
            **kwargs: The parameters for the tool execution.

        Returns:
            A dictionary containing the results of the tool execution.
            The dictionary should always have a "result" key with the
            primary result of the tool. It may optionally include other
            keys with additional information.

            If there's an error, the dictionary should include an "error"
            key with a description of the error.
        """
        raise NotImplementedError("Tool must implement an execute method")


class ToolRegistry:
    """
    Registry for tools.

    This class is responsible for registering and retrieving tools.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Args:
            tool: The tool to register.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool with name '{tool.name}' already registered"
            )
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.

        Args:
            name: The name of the tool to get.

        Returns:
            The tool, or None if no tool with the given name is registered.
        """
        return self._tools.get(name)

    def list(self) -> List[BaseTool]:
        """
        Get a list of all registered tools.

        Returns:
            A list of all registered tools.
        """
        return list(self._tools.values())

    def get_schema(self) -> Dict[str, Any]:
        """
        Get a schema for all registered tools.

        This is useful for generating tool descriptions for LLMs.

        Returns:
            A schema describing all registered tools.
        """
        tools = []
        for tool in self._tools.values():
            tools.append({
                "name": tool.name,
                "description": tool.description
            })
        return {"tools": tools}


# Create a global tool registry
tool_registry = ToolRegistry()


def register_tool(tool: BaseTool) -> BaseTool:
    """
    Register a tool with the global registry.

    This can be used as a decorator.

    Args:
        tool: The tool to register.

    Returns:
        The registered tool.
    """
    tool_registry.register(tool)
    return tool


def get_tool(name: str) -> Optional[BaseTool]:
    """
    Get a tool by name from the global registry.

    Args:
        name: The name of the tool to get.

    Returns:
        The tool, or None if no tool with the given name is registered.
    """
    return tool_registry.get(name)


def list_tools() -> List[BaseTool]:
    """
    Get a list of all registered tools from the global registry.

    Returns:
        A list of all registered tools.
    """
    return tool_registry.list()


def get_tools_schema() -> Dict[str, Any]:
    """
    Get a schema for all registered tools from the global registry.

    Returns:
        A schema describing all registered tools.
    """
    return tool_registry.get_schema()


