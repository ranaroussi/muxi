"""
Configuration Loader for MUXI Framework

This module provides utilities for loading and processing configuration files
for the MUXI Framework. It supports YAML and JSON formats, and handles
environment variable substitution.
"""

import os
import re
import json
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Load and process configuration files for MUXI Framework."""

    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        """
        Load a configuration file from the given path.

        Args:
            path: Path to the configuration file (YAML or JSON)

        Returns:
            Dict[str, Any]: The loaded configuration

        Raises:
            ValueError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(file_path, "r") as f:
            content = f.read()

            if file_path.suffix.lower() in [".yaml", ".yml"]:
                try:
                    import yaml
                except ImportError:
                    raise ImportError(
                        "PyYAML is required to load YAML files. "
                        "Install it with: pip install pyyaml"
                    )
                return yaml.safe_load(content)

            elif file_path.suffix.lower() == ".json":
                return json.loads(content)

            else:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. "
                    "Supported formats: .yaml, .yml, .json"
                )

    @staticmethod
    def process_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process environment variables in the configuration.

        Replaces ${ENV_VAR} patterns in string values with the corresponding
        environment variable values.

        Args:
            config: The configuration dictionary

        Returns:
            Dict[str, Any]: The processed configuration
        """
        def replace_env_vars(obj: Any) -> Any:
            if isinstance(obj, str):
                # Find all ${ENV_VAR} patterns
                env_vars = re.findall(r'\${([^}]+)}', obj)
                result = obj

                # Replace each pattern with the environment variable value
                for var in env_vars:
                    env_value = os.environ.get(var, "")
                    result = result.replace(f"${{{var}}}", env_value)

                return result
            elif isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            else:
                return obj

        return replace_env_vars(config)

    @staticmethod
    def normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize configuration to standard format.

        This converts simplified memory configuration to the standard format.

        Args:
            config: The configuration dictionary

        Returns:
            Dict[str, Any]: Normalized configuration
        """
        # Create a copy to avoid modifying the original
        result = config.copy()

        # Normalize memory configuration
        if "memory" in result:
            memory = result["memory"].copy()

            # Handle the new buffer_size parameter if present (preferred)
            if "buffer_size" in memory:
                buffer_size = memory.pop("buffer_size")  # Remove and get the value
                # Create/update buffer config with the correct structure
                if isinstance(memory.get("buffer"), dict):
                    memory["buffer"] = memory.get("buffer")
                else:
                    memory["buffer"] = {}
                memory["buffer"]["enabled"] = True
                memory["buffer"]["window_size"] = int(buffer_size)
                if "buffer_multiplier" not in memory["buffer"]:
                    memory["buffer"]["buffer_multiplier"] = 10  # Default multiplier

            # Normalize buffer memory (number -> {enabled: true, window_size: number})
            if "buffer" in memory:
                if isinstance(memory["buffer"], (int, float)):
                    buffer_size = int(memory["buffer"])
                    memory["buffer"] = {
                        "enabled": True,
                        "window_size": buffer_size,
                        "buffer_multiplier": 10  # Default multiplier
                    }
                elif memory["buffer"] is True:
                    memory["buffer"] = {
                        "enabled": True,
                        "window_size": 5,  # Default window size
                        "buffer_multiplier": 10  # Default multiplier
                    }
                elif not isinstance(memory["buffer"], dict):
                    memory["buffer"] = {
                        "enabled": bool(memory["buffer"]),
                        "window_size": 5,  # Default window size
                        "buffer_multiplier": 10  # Default multiplier
                    }
                elif isinstance(memory["buffer"], dict):
                    # Set default multiplier if not provided
                    if "buffer_multiplier" not in memory["buffer"]:
                        memory["buffer"]["buffer_multiplier"] = 10
            else:
                # Ensure buffer memory is always available with default settings
                memory["buffer"] = {
                    "enabled": True,
                    "window_size": 5,  # Default window size
                    "buffer_multiplier": 10  # Default multiplier
                }

            # Normalize long-term memory (boolean -> {enabled: boolean})
            if "long_term" in memory:
                if isinstance(memory["long_term"], bool):
                    enabled = memory["long_term"]
                    memory["long_term"] = {
                        "enabled": enabled
                    }
                elif not isinstance(memory["long_term"], dict):
                    memory["long_term"] = {
                        "enabled": bool(memory["long_term"])
                    }
            else:
                # Default to disabled long-term memory
                memory["long_term"] = {
                    "enabled": False
                }

            # Update memory in the result
            result["memory"] = memory
        else:
            # If memory is not specified, create default configuration
            result["memory"] = {
                "buffer": {
                    "enabled": True,
                    "window_size": 5,  # Default window size
                    "buffer_multiplier": 10  # Default multiplier
                },
                "long_term": {
                    "enabled": False
                }
            }

        return result

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """
        Validate the configuration.

        Args:
            config: The configuration dictionary

        Raises:
            ValueError: If the configuration is invalid
        """
        # Required fields
        if not config.get("name"):
            raise ValueError("Missing required field: name")

        # Model validation
        model = config.get("model", {})
        if not model.get("provider"):
            raise ValueError("Missing required field: model.provider")
        if not model.get("model"):
            raise ValueError("Missing required field: model.model")

        # Agent metadata validation
        if "description" in config and not isinstance(config["description"], str):
            raise ValueError("Invalid field: description must be a string")
        if "system_message" in config and not isinstance(config["system_message"], str):
            raise ValueError("Invalid field: system_message must be a string")

        # Memory validation - simpler now as we already normalized it
        memory = config.get("memory", {})
        if not isinstance(memory, dict):
            raise ValueError("Invalid field: memory must be an object")

        # Buffer memory validation
        buffer = memory.get("buffer", {})
        if not isinstance(buffer, dict):
            raise ValueError("Invalid field: memory.buffer must be an object")

        # Long-term memory validation
        long_term = memory.get("long_term", {})
        if not isinstance(long_term, dict):
            raise ValueError("Invalid field: memory.long_term must be an object")

        # Tools validation
        tools = config.get("tools", [])
        if not isinstance(tools, list):
            raise ValueError("Invalid field: tools must be an array")

        # MCP servers validation
        mcp_servers = config.get("mcp_servers", [])
        if not isinstance(mcp_servers, list):
            raise ValueError("Invalid field: mcp_servers must be an array")

        for server in mcp_servers:
            if not server.get("name"):
                raise ValueError("Missing required field: mcp_servers[].name")
            if not server.get("url") and not server.get("command"):
                raise ValueError(
                    "Missing required field: mcp_servers[].url or mcp_servers[].command"
                )

    def load_and_process(self, path: str) -> Dict[str, Any]:
        """
        Load, validate, and process a configuration file.

        Args:
            path: Path to the configuration file

        Returns:
            Dict[str, Any]: The processed configuration

        Raises:
            ValueError: If the configuration is invalid
            FileNotFoundError: If the file does not exist
        """
        config = self.load(path)
        config = self.process_env_vars(config)
        config = self.normalize_config(config)
        self.validate_config(config)
        return config
