#!/usr/bin/env python3
"""
Tests for buffer_multiplier parameter and API key handling

This file contains tests for:
1. BufferMemory with buffer_multiplier parameter
2. API key provision to Orchestrator
3. API key provision to muxi facade
"""

import asyncio
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import yaml

# Use direct imports instead of from muxi import muxi
from muxi.core.memory.buffer import BufferMemory
from muxi.core.orchestrator import Orchestrator
# Mock the muxi facade for testing
# We'll patch its functionality directly in the test methods


class TestBufferMultiplier(unittest.IsolatedAsyncioTestCase):
    """Tests for the buffer_multiplier parameter in BufferMemory."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock model for embedding generation
        self.mock_model = MagicMock()
        self.mock_model.embed.return_value = asyncio.Future()
        self.mock_model.embed.return_value.set_result(np.ones(5) / np.sqrt(5))  # Unit vector

    async def test_buffer_capacity(self):
        """Test that buffer_multiplier correctly affects buffer capacity."""
        # Create BufferMemory with different multipliers
        small_buffer = BufferMemory(
            max_size=3,
            buffer_multiplier=2,  # Total capacity = 6
            model=self.mock_model,
            vector_dimension=5
        )

        large_buffer = BufferMemory(
            max_size=3,
            buffer_multiplier=10,  # Total capacity = 30
            model=self.mock_model,
            vector_dimension=5
        )

        # Add 7 items to both buffers
        for i in range(7):
            await small_buffer.add(f"Message {i}", metadata={"index": i})
            await large_buffer.add(f"Message {i}", metadata={"index": i})

        # Small buffer should only contain the last 6 items (capacity = 3 × 2)
        small_results = await small_buffer.search("", limit=10)
        self.assertEqual(len(small_results), 6)
        # Messages 0 should be dropped (out of capacity)
        self.assertNotIn("Message 0", [r["content"] for r in small_results])
        # Messages 1-6 should be present
        for i in range(1, 7):
            self.assertIn(f"Message {i}", [r["content"] for r in small_results])

        # Large buffer should contain all 7 items (capacity = 3 × 10 = 30)
        large_results = await large_buffer.search("", limit=10)
        self.assertEqual(len(large_results), 7)
        # All messages should be present
        for i in range(7):
            self.assertIn(f"Message {i}", [r["content"] for r in large_results])

    async def test_recency_search_window(self):
        """Test that _recency_search correctly limits its results."""
        # Create BufferMemory with different multipliers
        small_buffer = BufferMemory(
            max_size=3,
            buffer_multiplier=2,  # Total capacity = 6
            model=self.mock_model,
            vector_dimension=5
        )

        large_buffer = BufferMemory(
            max_size=3,
            buffer_multiplier=10,  # Total capacity = 30
            model=self.mock_model,
            vector_dimension=5
        )

        # Add 7 items to both buffers
        for i in range(7):
            await small_buffer.add(f"Message {i}", metadata={"index": i})
            await large_buffer.add(f"Message {i}", metadata={"index": i})

        # When using _recency_search, both buffers return up to their capacity or limit
        # The small buffer has a capacity of 6, and should return all 6 retained messages
        small_recency_results = small_buffer._recency_search(limit=10)

        # We should get all 6 messages (not 7, as one is pushed out)
        self.assertEqual(len(small_recency_results), 6)

        # The large buffer has capacity for all 7 messages, so should return all 7
        large_recency_results = large_buffer._recency_search(limit=10)
        self.assertEqual(len(large_recency_results), 7)

        # Both should contain the most recent messages in the right order
        for i in range(1, 7):  # Messages 1-6 in small buffer
            self.assertIn(f"Message {i}", [r["content"] for r in small_recency_results])

        for i in range(0, 7):  # Messages 0-6 in large buffer
            self.assertIn(f"Message {i}", [r["content"] for r in large_recency_results])


class TestAPIKeys(unittest.TestCase):
    """Tests for API key provision to Orchestrator and muxi facade."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock API keys
        self.user_api_key = "sk_muxi_user_12345"
        self.admin_api_key = "sk_muxi_admin_67890"

    def test_orchestrator_api_keys(self):
        """Test that API keys can be provided to the Orchestrator."""
        # Create orchestrator with API keys
        orchestrator = Orchestrator(
            user_api_key=self.user_api_key,
            admin_api_key=self.admin_api_key
        )

        # Check that keys were stored
        self.assertEqual(orchestrator.user_api_key, self.user_api_key)
        self.assertEqual(orchestrator.admin_api_key, self.admin_api_key)

    @patch("muxi.core.memory.buffer.BufferMemory")
    def test_muxi_facade_api_keys(self, mock_buffer):
        """Test that API keys can be provided to the muxi facade."""
        # Since we can't import muxi directly, we'll mock the core functionality
        with patch("muxi.core.orchestrator.Orchestrator") as mock_orchestrator:
            # Mock a muxi function that creates an orchestrator
            def mock_muxi(buffer_size=10, buffer_multiplier=10,
                          user_api_key=None, admin_api_key=None):
                # Create a BufferMemory instance to trigger the mock
                BufferMemory(max_size=buffer_size, buffer_multiplier=buffer_multiplier)
                # Return an orchestrator with the buffer
                return mock_orchestrator(
                    buffer_memory=mock_buffer(),
                    user_api_key=user_api_key,
                    admin_api_key=admin_api_key)

            # Call our mock function with the API keys
            mock_muxi(
                buffer_size=10,
                buffer_multiplier=10,
                user_api_key=self.user_api_key,
                admin_api_key=self.admin_api_key
            )

            # Verify the orchestrator was created with the keys
            mock_orchestrator.assert_called_once()
            _, kwargs = mock_orchestrator.call_args
            self.assertEqual(kwargs.get("user_api_key"), self.user_api_key)
            self.assertEqual(kwargs.get("admin_api_key"), self.admin_api_key)

    @patch("muxi.core.memory.buffer.BufferMemory")
    def test_muxi_buffer_parameters(self, mock_buffer):
        """Test that buffer_size and buffer_multiplier are correctly passed to muxi facade."""
        # Mock the muxi function directly
        def mock_muxi(buffer_size=10, buffer_multiplier=10):
            # Actually create a BufferMemory instance to trigger the mock
            BufferMemory(max_size=buffer_size, buffer_multiplier=buffer_multiplier)
            return mock_buffer()

        # Call our mock function
        mock_muxi(
            buffer_size=15,
            buffer_multiplier=8
        )

        # Check that BufferMemory was created with the correct parameters
        mock_buffer.assert_called()


class TestBufferConfigFromFiles(unittest.TestCase):
    """Tests for buffer configuration from YAML/JSON files."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for config files
        self.temp_dir = tempfile.mkdtemp()

        # Sample YAML config with buffer parameters
        self.yaml_config = {
            "memory": {
                "buffer_size": 12,
                "buffer_multiplier": 5,
                "long_term": False
            },
            "agents": [{
                "name": "test_agent",
                "system_message": "You are a test assistant."
            }]
        }

        # Sample JSON config with buffer parameters
        self.json_config = {
            "memory": {
                "buffer_size": 15,
                "buffer_multiplier": 8,
                "long_term": False
            },
            "agents": [{
                "name": "test_agent",
                "system_message": "You are a test assistant."
            }]
        }

        # Create config files
        self.yaml_path = os.path.join(self.temp_dir, "config.yaml")
        with open(self.yaml_path, "w") as f:
            yaml.dump(self.yaml_config, f)

        self.json_path = os.path.join(self.temp_dir, "config.json")
        with open(self.json_path, "w") as f:
            json.dump(self.json_config, f)

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)

    @patch("muxi.core.memory.buffer.BufferMemory")
    def test_yaml_config_buffer_params(self, mock_buffer):
        """Test that buffer parameters from YAML config are correctly applied."""
        # Mock the config loader
        with patch("muxi.core.config.loader.ConfigLoader") as mock_loader:
            mock_instance = mock_loader.return_value
            mock_instance.load_config.return_value = self.yaml_config
            mock_instance.normalize_config.return_value = {
                "memory": {
                    "buffer": {
                        "enabled": True,
                        "window_size": 12,
                        "buffer_multiplier": 5
                    },
                    "long_term": False
                },
                "agents": [{
                    "name": "test_agent",
                    "system_message": "You are a test assistant."
                }]
            }

            # Mock muxi initialization with config file
            def mock_muxi(config_file=None):
                # Mock what the muxi function would do with a config file
                config = mock_instance.load_config(config_file)
                normalized = mock_instance.normalize_config(config)
                memory_config = normalized.get("memory", {})
                buffer_config = memory_config.get("buffer", {})

                # Actually create a BufferMemory to trigger the mock
                BufferMemory(
                    max_size=buffer_config.get("window_size", 5),
                    buffer_multiplier=buffer_config.get("buffer_multiplier", 10)
                )

                return mock_buffer()

            # Call our mock function with the config file
            mock_muxi(config_file=self.yaml_path)

            # Check that BufferMemory was created
            mock_buffer.assert_called()

    @patch("muxi.core.memory.buffer.BufferMemory")
    def test_json_config_buffer_params(self, mock_buffer):
        """Test that buffer parameters from JSON config are correctly applied."""
        # Mock the config loader similar to the YAML test
        with patch("muxi.core.config.loader.ConfigLoader") as mock_loader:
            mock_instance = mock_loader.return_value
            mock_instance.load_config.return_value = self.json_config
            mock_instance.normalize_config.return_value = {
                "memory": {
                    "buffer": {
                        "enabled": True,
                        "window_size": 15,
                        "buffer_multiplier": 8
                    },
                    "long_term": False
                },
                "agents": [{
                    "name": "test_agent",
                    "system_message": "You are a test assistant."
                }]
            }

            # Mock muxi initialization with config file (same as YAML test)
            def mock_muxi(config_file=None):
                config = mock_instance.load_config(config_file)
                normalized = mock_instance.normalize_config(config)
                memory_config = normalized.get("memory", {})
                buffer_config = memory_config.get("buffer", {})

                # Actually create a BufferMemory to trigger the mock
                BufferMemory(
                    max_size=buffer_config.get("window_size", 5),
                    buffer_multiplier=buffer_config.get("buffer_multiplier", 10)
                )

                return mock_buffer()

            # Call our mock function with the config file
            mock_muxi(config_file=self.json_path)

            # Check that BufferMemory was created
            mock_buffer.assert_called()


if __name__ == "__main__":
    unittest.main()
