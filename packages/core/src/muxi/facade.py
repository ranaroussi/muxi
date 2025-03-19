"""
MUXI Framework Facade

This module provides a simplified interface for interacting with the MUXI Framework.
It allows creating and managing agents through configuration files, setting up
MCP servers, and starting the API server with minimal code.
"""

import os
from typing import Any, Dict, List, Optional

from loguru import logger

from muxi.core.agent import Agent
from muxi.core.orchestrator import Orchestrator
from muxi.models.providers.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory
from muxi.server.memory.memobase import Memobase
from muxi.config_loader import ConfigLoader
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

    async def add_agent(
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

        # Extract description or use system message as fallback
        description = config.get("description", config.get("system_message", ""))

        # Create the agent
        agent = self.orchestrator.create_agent(
            agent_id=name,
            model=model,
            buffer_memory=buffer_memory,
            long_term_memory=long_term_memory,
            system_message=config.get("system_message", ""),
            description=description
        )

        # Connect MCP servers if specified
        mcp_servers = config.get("mcp_servers", [])
        if mcp_servers:
            await self._connect_mcp_servers(agent, mcp_servers)

        return agent

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
        # Debug print
        print(f"Memory config: {memory_config}")

        # Create buffer memory
        buffer_size = memory_config.get("buffer", 10)
        if isinstance(buffer_size, dict):
            # If it's a dict, extract the window_size or max_size parameter
            buffer_size = buffer_size.get("window_size", buffer_size.get("max_size", 10))
        buffer_memory = BufferMemory(max_size=int(buffer_size))

        # Create long-term memory if enabled
        long_term_memory = None
        long_term_config = memory_config.get("long_term", False)

        # Support both boolean and dict configurations
        if isinstance(long_term_config, dict):
            enabled = long_term_config.get("enabled", False)
        else:
            enabled = bool(long_term_config)

        if enabled:
            # Get database connection string
            connection_string = self._get_connection_string(required=False)

            if connection_string:
                try:
                    # Create long-term memory with database connection
                    long_term_memory = LongTermMemory(connection_string=connection_string)

                    # Always wrap with Memobase for multi-user support
                    # (will use user_id=0 when none provided for backwards compatibility)
                    long_term_memory = Memobase(long_term_memory=long_term_memory)
                except Exception as e:
                    # Log the error but continue without long-term memory
                    print(f"Error creating long-term memory: {e}")
                    long_term_memory = None

        return buffer_memory, long_term_memory

    async def _connect_mcp_servers(self, agent: Agent, mcp_servers: List[Dict[str, Any]]) -> None:
        """
        Connect MCP servers to an agent.

        Args:
            agent: The agent to connect MCP servers to
            mcp_servers: List of MCP server configurations
        """
        for server in mcp_servers:
            name = server.get("name")
            url = server.get("url")
            credentials = server.get("credentials", [])

            if name and url:
                # Process credentials
                processed_credentials = {}
                for cred in credentials:
                    cred_id = cred.get("id")
                    param_name = cred.get("param_name")
                    required = cred.get("required", False)

                    # Check for env_fallback
                    env_var = cred.get("env_fallback")
                    if env_var:
                        import os
                        value = os.getenv(env_var)

                        if value:
                            processed_credentials[param_name] = value
                            continue

                    # Missing required credential
                    if required:
                        logger.warning(
                            f"Required credential {cred_id} for MCP server {name} not found"
                        )
                        continue

                # Connect to the MCP server
                try:
                    await agent.connect_mcp_server(name, url, processed_credentials)
                    print(f"Connected to MCP server: {name}")
                except Exception as e:
                    logger.error(f"Error connecting to MCP server {name}: {e}")
            else:
                logger.warning(f"Invalid MCP server configuration: {server}")

    async def chat(
        self,
        agent_name: Optional[str] = None,
        message: str = "",
        user_id: Optional[str] = None
    ) -> str:
        """
        Send a message to an agent and get a response.

        Args:
            agent_name: Optional name of the agent to use (if None, will select automatically)
            message: The message to send
            user_id: Optional user ID for multi-user support

        Returns:
            The agent's response as a string
        """
        # Process the message through the orchestrator
        response = await self.orchestrator.chat(
            agent_name=agent_name,
            message=message,
            user_id=user_id
        )

        # Return just the text response (content could be a string or dict)
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, dict) and "text" in response.content:
            return response.content["text"]
        else:
            # Fallback to string representation
            return str(response.content)

    def add_user_context_memory(
        self,
        user_id: int,
        knowledge: Dict[str, Any]
    ) -> None:
        """
        Add context memory for a specific user.

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
                # Add context memory
                agent.long_term_memory.add_context_memory(user_id, knowledge)
                return

        raise ValueError(
            "No agent with Memobase found. Add at least one agent with long-term "
            "memory enabled before adding context memory."
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
        from muxi.api.app import start_api

        # Start the API server
        start_api(host=host, port=port, **kwargs)

    def run(self, **kwargs) -> None:
        """
        Start both the API server and web UI.

        Args:
            **kwargs: Additional arguments to pass to the API server
        """
        # Import the main entry point
        from muxi.__main__ import main

        # Start the server
        main(**kwargs)

    def get_agent(self, agent_id: str) -> Agent:
        """
        Get an agent by ID.

        Args:
            agent_id: The ID of the agent to get.

        Returns:
            The requested agent.

        Raises:
            ValueError: If no agent with the given ID exists.
        """
        return self.orchestrator.get_agent(agent_id)
