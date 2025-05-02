"""
MUXI Framework Facade with Orchestrator-Level Memory

This module provides a simplified interface for interacting with the MUXI Framework.
It allows creating and managing agents through configuration files, setting up
MCP servers, and starting the API server with minimal code.
"""

import os
import asyncio
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from muxi.core.agent import Agent
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.memory.sqlite import SQLiteMemory
from muxi.core.config.loader import ConfigLoader


class Muxi:
    """
    Main facade for the MUXI Framework.

    This class provides a simplified interface for creating and managing agents,
    setting up MCP servers, and starting the API server with minimal code.
    """

    def __init__(
        self,
        buffer_size: Optional[Union[int, BufferMemory]] = None,
        buffer_multiplier: int = 10,
        long_term_memory: Optional[Union[str, bool, LongTermMemory, Memobase]] = None,
        credential_db_connection_string: Optional[str] = None,
        user_api_key: Optional[str] = None,
        admin_api_key: Optional[str] = None
    ):
        """
        Initialize the declarative interface.

        Args:
            buffer_size: Context window size configuration
                - If an integer, specifies the number of messages to keep in the context window
                - If a BufferMemory instance, used directly
            buffer_multiplier: Multiplier for the buffer capacity (default: 10)
                - The actual buffer size will be buffer_size * buffer_multiplier
            long_term_memory: Long-term memory configuration
                - If a string, treated as a file path to an SQLite database
                - If True, creates a default SQLite database in the current directory
                - If an instance of LongTermMemory or Memobase, used directly
            credential_db_connection_string: Connection string for the credential database
                (can also be set via MUXI_DB_CONNECTION_STRING environment variable)
            user_api_key: Optional API key for user-level access
            admin_api_key: Optional API key for admin-level access
        """
        # Store connection string for memory systems
        self._credential_db_connection_string = credential_db_connection_string

        # Create memory systems from configurations
        buffer_mem, long_term_mem = self._create_memory_systems({
            "buffer_memory": buffer_size,
            "buffer_multiplier": buffer_multiplier,
            "long_term_memory": long_term_memory
        })

        # Create orchestrator with memory systems
        self.orchestrator = Orchestrator(
            buffer_memory=buffer_mem,
            long_term_memory=long_term_mem,
            user_api_key=user_api_key,
            admin_api_key=admin_api_key
        )

        # Initialize config loader
        self.config_loader = ConfigLoader()

    def _create_buffer_memory(
        self,
        buffer_config: Optional[Union[int, Dict[str, Any], BufferMemory]],
        buffer_multiplier: int = 10
    ) -> Optional[BufferMemory]:
        """
        Create a buffer memory object from configuration.

        Args:
            buffer_config: Buffer memory configuration. Can be:
                - An integer (context window size)
                - A dictionary with 'window_size' and optional 'buffer_multiplier'
                - A BufferMemory instance
                - None (no buffer memory)
            buffer_multiplier: Multiplier for the buffer capacity (default: 10)

        Returns:
            Configured BufferMemory instance or None.
        """
        if buffer_config is None:
            return None

        if isinstance(buffer_config, int):
            # Create buffer memory with specified size and multiplier
            return BufferMemory(
                max_size=buffer_config,
                buffer_multiplier=buffer_multiplier
            )

        if isinstance(buffer_config, dict):
            # Extract window_size and buffer_multiplier from dict
            window_size = buffer_config.get("window_size", 5)
            config_multiplier = buffer_config.get("buffer_multiplier", buffer_multiplier)

            # Create buffer with specified parameters
            return BufferMemory(
                max_size=window_size,
                buffer_multiplier=config_multiplier
            )

        # Assume it's already a BufferMemory instance
        return buffer_config

    def _create_long_term_memory(
        self,
        long_term_config: Optional[Union[str, bool, LongTermMemory, Memobase]],
        credential_db_connection_string: Optional[str] = None
    ) -> Optional[Union[LongTermMemory, Memobase]]:
        """
        Create a long-term memory object from configuration.

        Args:
            long_term_config: Long-term memory configuration. Can be:
                - A connection string (postgresql:// or sqlite://)
                - True (use default SQLite)
                - A LongTermMemory or Memobase instance
                - None (no long-term memory)
            credential_db_connection_string: Optional database connection string to use if
                long_term_config doesn't specify one.

        Returns:
            Configured memory instance or None.
        """
        if long_term_config is None:
            return None

        # If it's already a LongTermMemory or Memobase instance, use it directly
        if isinstance(long_term_config, (LongTermMemory, Memobase)):
            return long_term_config

        # Handle string connection specifications
        if isinstance(long_term_config, str):
            # Postgres connection string
            if long_term_config.startswith(('postgresql://', 'postgres://')):
                try:
                    # Create long-term memory with database connection
                    memory = LongTermMemory(connection_string=long_term_config)

                    # Wrap with Memobase for multi-user support
                    memobase = Memobase(long_term_memory=memory)
                    logger.info("Created Postgres long-term memory with connection string")
                    return memobase
                except Exception as e:
                    # Log the error but continue without long-term memory
                    logger.error(f"Error creating Postgres long-term memory: {e}")
                    return None

            # SQLite connection string format (sqlite:///path/to/db)
            elif long_term_config.startswith('sqlite:///'):
                try:
                    # Extract the path: remove 'sqlite:///' prefix
                    db_path = long_term_config[10:]
                    memory = SQLiteMemory(db_path=db_path)
                    logger.info(f"Created SQLite long-term memory at {db_path}")
                    return memory
                except Exception as e:
                    # Log the error but continue without long-term memory
                    logger.error(f"Error creating SQLite long-term memory: {e}")
                    return None

            # Plain SQLite path
            else:
                try:
                    memory = SQLiteMemory(db_path=long_term_config)
                    logger.info(f"Created SQLite long-term memory at {long_term_config}")
                    return memory
                except Exception as e:
                    # Log the error but continue without long-term memory
                    logger.error(f"Error creating SQLite long-term memory: {e}")
                    return None

        # Boolean true - use connection string or default SQLite database
        elif long_term_config is True:
            # First try to use provided connection string
            conn_str = credential_db_connection_string or self.credential_db_connection_string
            if conn_str and (
                conn_str.startswith('postgresql://') or
                conn_str.startswith('postgres://')
            ):
                try:
                    # Create long-term memory with database connection
                    memory = LongTermMemory(connection_string=conn_str)

                    # Wrap with Memobase for multi-user support
                    memobase = Memobase(long_term_memory=memory)
                    logger.info("Created Postgres long-term memory with provided connection string")
                    return memobase
                except Exception as e:
                    # Log the error but fall back to SQLite
                    logger.error(
                        f"Error creating Postgres long-term memory, falling back to SQLite: {e}"
                    )

            # Fall back to SQLite
            try:
                db_path = os.path.join(os.getcwd(), 'muxi.db')
                memory = SQLiteMemory(db_path=db_path)
                logger.info(f"Created default SQLite long-term memory at {db_path}")
                return memory
            except Exception as e:
                # Log the error but continue without long-term memory
                logger.error(f"Error creating default SQLite long-term memory: {e}")
                return None

        # If we get here, we don't know how to handle the configuration
        logger.warning(f"Unrecognized long-term memory configuration: {long_term_config}")
        return None

    @property
    def credential_db_connection_string(self) -> Optional[str]:
        """
        Get the credential database connection string, fetching from environment if not set.

        Returns:
            Optional[str]: Credential database connection string if available
        """
        if self._credential_db_connection_string is None:
            # Try to load from environment if not already set
            self._credential_db_connection_string = os.environ.get("POSTGRES_DATABASE_URL")

        return self._credential_db_connection_string

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
        connection_string = self.credential_db_connection_string

        if required and not connection_string:
            raise ValueError(
                "Database connection string is required for this operation. "
                "Please provide it when initializing Muxi or set POSTGRES_DATABASE_URL "
                "in your environment."
            )

        return connection_string

    async def add_agent(
        self,
        name: str,
        path: str,
        env_file: Optional[str] = None
    ) -> Agent:
        """
        Add an agent from a configuration file.

        Args:
            name: Name to assign to the agent (overrides the name in the config)
            path: Path to the configuration file (YAML or JSON)
            env_file: Optional path to an environment file to load

        Returns:
            The created Agent instance.

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

        # Extract description or use system message as fallback
        description = config.get("description", config.get("system_message", ""))

        # Create the agent
        agent = self.orchestrator.create_agent(
            agent_id=name,
            model=model,
            system_message=config.get("system_message", ""),
            description=description
        )

        # If we have buffer memory and it doesn't have a model set,
        # set the model to enable vector search capabilities
        if (self.orchestrator.buffer_memory and
                hasattr(self.orchestrator.buffer_memory, "model") and
                self.orchestrator.buffer_memory.model is None):
            self.orchestrator.buffer_memory.model = model
            logger.info(
                f"Enabled vector search in buffer memory using {model.__class__.__name__}"
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
        # Create buffer memory
        buffer_config = memory_config.get("buffer_memory")
        buffer_multiplier = memory_config.get("buffer_multiplier", 10)
        buffer_memory = self._create_buffer_memory(
            buffer_config=buffer_config,
            buffer_multiplier=buffer_multiplier
        )

        # Create long-term memory if enabled
        long_term_config = memory_config.get("long_term_memory")
        long_term_memory = self._create_long_term_memory(
            long_term_config,
            self.credential_db_connection_string
        )

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
                            f"Required credential {cred_id} for MCP server "
                            f"{name} not found"
                        )
                        continue

                # Connect to the MCP server
                try:
                    # Assuming agent has a method to connect to MCP server
                    # Replace with actual method if different
                    if hasattr(agent, "connect_mcp_server"):
                        await agent.connect_mcp_server(name, url, processed_credentials)
                        logger.info(f"Connected to MCP server: {name}")
                    else:
                        logger.warning(
                            f"Agent {agent.name} does not have connect_mcp_server method."
                        )

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
            ValueError: If orchestrator doesn't have multi-user memory
        """
        # Use orchestrator's long-term memory if it's multi-user
        if hasattr(self.orchestrator, "is_multi_user") and self.orchestrator.is_multi_user:
            if hasattr(self.orchestrator.long_term_memory, "add_user_context_memory"):
                # Assuming add_context_memory is async now based on Memobase
                asyncio.create_task(
                    self.orchestrator.long_term_memory.add_user_context_memory(user_id, knowledge)
                )
                return

        # Fallback removed as it's less likely to be correct with current structure

        raise ValueError(
            "No suitable long-term memory found for user context. Make sure Muxi is "
            "initialized with a Memobase-compatible memory (PostgreSQL connection)."
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
        # Import here to avoid circular imports
        from muxi.core.run import run_server

        # Start the server
        run_server(host=host, port=port, **kwargs)

    def run(self, **kwargs) -> None:
        """
        Start the MUXI server with the current configuration.

        This method displays a splash screen and shows API keys if they were auto-generated.

        Args:
            **kwargs: Additional arguments to pass to the server
                - host: Host to bind the server to (default: "0.0.0.0")
                - port: Port to bind the server to (default: 5050)
                - reload: Whether to enable auto-reload for development (default: True)
                - mcp: Whether to enable MCP functionality (default: False)
        """
        # Start the server using the orchestrator's run method
        self.orchestrator.run(**kwargs)

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
