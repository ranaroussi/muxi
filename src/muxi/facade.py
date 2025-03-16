"""
MUXI Framework Facade

This module provides a simplified interface for interacting with the MUXI Framework.
It allows creating and managing agents through configuration files, setting up
MCP servers, and starting the API server with minimal code.
"""

import os
from typing import Any, Dict, List, Optional

from src.core.orchestrator import Orchestrator
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase
from src.models import OpenAIModel
from src.tools.calculator import Calculator
from src.tools.web_search import WebSearch

from .config_loader import ConfigLoader
from .credential_manager import CredentialManager


class Muxi:
    """
    Main facade for the MUXI Framework.

    This class provides a simplified interface for creating and managing agents,
    setting up MCP servers, and starting the API server with minimal code.
    """

    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Initialize the MUXI facade.

        Args:
            db_connection_string: Optional database connection string for
                                  credentials and long-term memory.
                                  If None, will be loaded from DATABASE_URL
                                  when needed.
        """
        # Initialize the orchestrator
        self.orchestrator = Orchestrator()

        # Initialize utilities
        self.config_loader = ConfigLoader()
        self.credential_manager = CredentialManager(db_connection_string)

        # Store the database connection string
        self._db_connection_string = db_connection_string

    @property
    def db_connection_string(self) -> Optional[str]:
        """
        Get the database connection string, fetching from environment if not set.

        Returns:
            Optional[str]: Database connection string if available
        """
        if self._db_connection_string is None:
            # Try to load from environment if not already set
            self._db_connection_string = os.environ.get("DATABASE_URL")

        return self._db_connection_string

    def _get_connection_string(self, required: bool = True) -> Optional[str]:
        """
        Get the database connection string for operations that may require it.

        Args:
            required: Whether the connection string is required

        Returns:
            Optional[str]: Database connection string

        Raises:
            ValueError: If required is True and no connection string is available
        """
        connection_string = self.db_connection_string

        if required and not connection_string:
            raise ValueError(
                "Database connection string is required for this operation. "
                "Please provide it when initializing Muxi or set DATABASE_URL "
                "in your environment."
            )

        return connection_string

    def add_agent(
        self,
        name: str,
        path: str,
        env_file: Optional[str] = None
    ) -> None:
        """
        Add an agent from a configuration file.

        Args:
            name: Name to assign to the agent (overrides the name in the config)
            path: Path to the configuration file (YAML or JSON)
            env_file: Optional path to an environment file to load

        Raises:
            ValueError: If the configuration is invalid
            FileNotFoundError: If the configuration file does not exist
        """
        # Load environment file if provided
        if env_file:
            from dotenv import load_dotenv
            load_dotenv(env_file)

        # Load and process the configuration
        config = self.config_loader.load_and_process(path)

        # Override the name if provided
        config["name"] = name

        # Create the model
        model_config = config.get("model", {})
        model = self._create_model(model_config)

        # Create the memory systems
        memory_config = config.get("memory", {})
        buffer_memory, long_term_memory = self._create_memory_systems(memory_config)

        # Create the tools
        tools = self._create_tools(config.get("tools", []))

        # Create the agent
        self.orchestrator.create_agent(
            agent_id=name,
            model=model,
            buffer_memory=buffer_memory,
            long_term_memory=long_term_memory,
            tools=tools,
            system_message=config.get("system_message", "")
        )

    def _create_model(self, model_config: Dict[str, Any]) -> Any:
        """
        Create a model from the configuration.

        Args:
            model_config: Model configuration dictionary

        Returns:
            The model instance

        Raises:
            ValueError: If the model provider is not supported
        """
        provider = model_config.get("provider", "openai").lower()

        if provider == "openai":
            return OpenAIModel(
                api_key=model_config.get("api_key"),
                model=model_config.get("model", "gpt-4o"),
                temperature=model_config.get("temperature", 0.7)
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    def _create_memory_systems(
        self,
        memory_config: Dict[str, Any]
    ) -> tuple:
        """
        Create memory systems from the configuration.

        Args:
            memory_config: Memory configuration dictionary

        Returns:
            tuple: (buffer_memory, long_term_memory)
        """
        # Create buffer memory - always enabled with configurable window size
        buffer_config = memory_config.get("buffer", {})
        buffer_memory = BufferMemory(
            max_size=buffer_config.get("window_size", 5)
        )

        # Create long-term memory if enabled
        long_term_config = memory_config.get("long_term", {})
        long_term_memory = None

        if long_term_config.get("enabled", False):
            # Get connection string only when needed and verify it exists
            connection_string = self._get_connection_string(required=True)

            # Create the long-term memory
            long_term_memory = LongTermMemory(
                connection_string=connection_string
            )

            # Always wrap with Memobase for multi-user support
            # (will use user_id=0 when none provided for backwards compatibility)
            long_term_memory = Memobase(long_term_memory=long_term_memory)

        return buffer_memory, long_term_memory

    def _create_tools(self, tool_list: List[str]) -> List[Any]:
        """
        Create tools from the configuration.

        Args:
            tool_list: List of tool identifiers

        Returns:
            List[Any]: List of tool instances
        """
        tools = []

        # Add built-in tools based on configuration
        if "enable_calculator" in tool_list:
            tools.append(Calculator())

        if "enable_web_search" in tool_list:
            tools.append(WebSearch())

        # TODO: Add support for custom tools

        return tools

    def chat(
        self,
        message: str,
        agent_name: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> str:
        """
        Chat with an agent.

        Args:
            message: Message to send to the agent
            agent_name: Optional name of the agent to chat with
                       (if None, the orchestrator will select the most appropriate agent)
            user_id: Optional user ID for multi-user support

        Returns:
            str: The agent's response

        Raises:
            ValueError: If no suitable agent is available
        """
        return self.orchestrator.chat(
            message=message,
            agent_id=agent_name,
            user_id=user_id
        )

    def add_user_domain_knowledge(
        self,
        user_id: int,
        knowledge: Dict[str, Any]
    ) -> None:
        """
        Add domain knowledge for a specific user.

        Args:
            user_id: User ID to associate the knowledge with
            knowledge: Knowledge to add (any serializable object)

        Raises:
            ValueError: If no agent with Memobase is available
        """
        # Make sure we have a connection string since this will need database access
        self._get_connection_string(required=True)

        # Find the first agent with Memobase
        for agent_id, agent in self.orchestrator.agents.items():
            if hasattr(agent, "long_term_memory") and isinstance(
                agent.long_term_memory, Memobase
            ):
                # Add domain knowledge
                agent.long_term_memory.add_domain_knowledge(user_id, knowledge)
                return

        raise ValueError(
            "No agent with Memobase found. Add at least one agent with long-term "
            "memory enabled before adding domain knowledge."
        )

    def start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        **kwargs
    ) -> None:
        """
        Start the API server.

        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional arguments to pass to the API server
        """
        from src.api.app import start_api

        # Start the API server
        start_api(host=host, port=port, **kwargs)

    def run(self, **kwargs) -> None:
        """
        Start both the API server and web UI.

        Args:
            **kwargs: Additional arguments to pass to the API server
        """
        # Import the main entry point
        from src.__main__ import main

        # Start the server
        main(**kwargs)
