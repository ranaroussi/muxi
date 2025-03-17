"""
Credential Manager for MUXI Framework

This module provides utilities for managing credentials for MCP servers.
It supports retrieving credentials from environment variables and databases.
"""

import os
from typing import Any, Dict, List, Optional


class CredentialManager:
    """Manage credentials for MCP servers."""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the credential manager.

        Args:
            connection_string: Database connection string for credential storage
                               (if None, only environment variables will be used)
        """
        self.connection_string = connection_string
        self.db_available = connection_string is not None

    def get_credential(
        self,
        credential_id: str,
        user_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Get a credential by ID, optionally for a specific user.

        Args:
            credential_id: ID of the credential to retrieve
            user_id: Optional user ID for user-specific credentials

        Returns:
            Optional[str]: The credential value, or None if not found
        """
        if not credential_id:
            return None

        # First try user-specific credential if user_id is provided
        if user_id is not None and self.db_available:
            user_credential = self._get_user_credential(credential_id, user_id)
            if user_credential:
                return user_credential

        # Then try system-wide credential from database
        if self.db_available:
            system_credential = self._get_system_credential(credential_id)
            if system_credential:
                return system_credential

        # Finally, try environment variable
        env_var = credential_id.upper()  # Convention: credential IDs map to uppercase env vars
        return os.environ.get(env_var)

    def _get_user_credential(self, credential_id: str, user_id: int) -> Optional[str]:
        """
        Get a user-specific credential from the database.

        Args:
            credential_id: ID of the credential
            user_id: User ID

        Returns:
            Optional[str]: The credential value, or None if not found
        """
        # This is a placeholder that should be replaced with actual database access code
        # In a real implementation, this would query the credentials table
        try:
            # Example of how this might work with a real database
            # query = "SELECT value FROM credentials WHERE credential_id = ? AND user_id = ?"
            # result = database.execute_query(query, (credential_id, user_id))
            # return result[0] if result else None
            return None
        except Exception:
            return None

    def _get_system_credential(self, credential_id: str) -> Optional[str]:
        """
        Get a system-wide credential from the database.

        Args:
            credential_id: ID of the credential

        Returns:
            Optional[str]: The credential value, or None if not found
        """
        # This is a placeholder that should be replaced with actual database access code
        # In a real implementation, this would query the credentials table
        try:
            # Example of how this might work with a real database
            # query = "SELECT value FROM credentials WHERE credential_id = ? AND user_id IS NULL"
            # result = database.execute_query(query, (credential_id,))
            # return result[0] if result else None
            return None
        except Exception:
            return None

    def resolve_mcp_credentials(
        self,
        mcp_config: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Resolve credentials for an MCP server.

        Args:
            mcp_config: MCP server configuration
            user_id: Optional user ID for user-specific credentials

        Returns:
            Dict[str, Any]: The MCP server configuration with resolved credentials

        Raises:
            ValueError: If a required credential is not found
        """
        if "credentials" not in mcp_config:
            return mcp_config

        # Get credentials configuration
        credentials_config = mcp_config["credentials"]
        result_args = mcp_config.get("args", {}).copy()

        # Handle single credential object
        if isinstance(credentials_config, dict):
            credentials_config = [credentials_config]

        # Handle list of credentials
        if isinstance(credentials_config, list):
            for cred_config in credentials_config:
                # Get credential details
                cred_id = cred_config.get("id")
                param_name = cred_config.get("param_name", cred_id)
                required = cred_config.get("required", False)

                # Get credential value
                value = self.get_credential(cred_id, user_id)

                # Handle required credential not found
                if required and value is None:
                    raise ValueError(f"Required credential not found: {cred_id}")

                # Add credential to args if found
                if value is not None:
                    result_args[param_name] = value

        # Update args in the result config
        result = mcp_config.copy()
        result["args"] = result_args

        return result

    def resolve_all_mcp_credentials(
        self,
        mcp_configs: List[Dict[str, Any]],
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Resolve credentials for multiple MCP servers.

        Args:
            mcp_configs: List of MCP server configurations
            user_id: Optional user ID for user-specific credentials

        Returns:
            List[Dict[str, Any]]: The MCP server configurations with resolved credentials
        """
        return [
            self.resolve_mcp_credentials(mcp_config, user_id)
            for mcp_config in mcp_configs
        ]
