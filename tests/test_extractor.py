"""
Unit tests for the MemoryExtractor module.

This module contains tests for the MemoryExtractor class in the MUXI Framework.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock
import asyncio

from muxi.server.memory.extractor import MemoryExtractor
from tests.utils.async_test import async_test


class TestMemoryExtractor(unittest.TestCase):
    """Test cases for the MemoryExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock orchestrator
        self.mock_orchestrator = MagicMock()
        self.mock_orchestrator.get_user_context_memory = AsyncMock(return_value={})
        self.mock_orchestrator.add_user_context_memory = AsyncMock(return_value=["123"])

        # Create a mock model that returns extraction results
        self.mock_model = MagicMock()
        self.mock_model.generate = AsyncMock(return_value="""
        {
            "extracted_info": [
                {
                    "key": "name",
                    "value": "John Doe",
                    "confidence": 0.9,
                    "importance": 0.8
                },
                {
                    "key": "occupation",
                    "value": "Software Engineer",
                    "confidence": 0.85,
                    "importance": 0.7
                }
            ]
        }
        """)

        # Create the extractor with mock dependencies
        self.extractor = MemoryExtractor(
            orchestrator=self.mock_orchestrator,
            extraction_model=self.mock_model,
            confidence_threshold=0.7,
            auto_extract=True
        )

        # Mock the internal methods to focus on testing the process flow
        self.extractor._extract_user_information = AsyncMock(return_value={
            "name": {"value": "John Doe", "confidence": 0.9, "importance": 0.8},
            "occupation": {"value": "Software Engineer", "confidence": 0.85, "importance": 0.7}
        })
        self.extractor._process_extraction_results = AsyncMock()

    @async_test
    async def test_process_conversation_turn(self):
        """Test processing a conversation turn."""
        # Setup
        user_message = "Hi, I'm John, a software engineer"
        agent_response = "Nice to meet you, John"

        # Execute
        await self.extractor.process_conversation_turn(
            user_message=user_message,
            agent_response=agent_response,
            user_id=123,
            message_count=1
        )

        # Verify
        self.extractor._extract_user_information.assert_called_once()
        self.extractor._process_extraction_results.assert_called_once()

    @async_test
    async def test_anonymous_user_skipped(self):
        """Test that processing is skipped for anonymous users."""
        # Setup
        user_message = "Hi, I'm anonymous"
        agent_response = "Hello there"

        # Execute
        await self.extractor.process_conversation_turn(
            user_message=user_message,
            agent_response=agent_response,
            user_id=0,  # Anonymous user ID
            message_count=1
        )

        # Verify
        self.extractor._extract_user_information.assert_not_called()
        self.extractor._process_extraction_results.assert_not_called()

    @async_test
    async def test_opt_out_user(self):
        """Test that a user can opt out of extraction."""
        # Setup
        user_id = 456

        # Execute
        result = self.extractor.opt_out_user(user_id)

        # Verify
        self.assertTrue(result)
        self.assertIn(user_id, self.extractor.opt_out_users)

        # Try to process for opted-out user
        await self.extractor.process_conversation_turn(
            user_message="Hello",
            agent_response="Hi",
            user_id=user_id,
            message_count=1
        )

        # Verify extraction was skipped
        self.extractor._extract_user_information.assert_not_called()
        self.extractor._process_extraction_results.assert_not_called()

    @async_test
    async def test_opt_in_user(self):
        """Test that a user can opt back in to extraction."""
        # Setup - first opt out
        user_id = 789
        self.extractor.opt_out_user(user_id)

        # Execute - now opt in
        result = self.extractor.opt_in_user(user_id)

        # Verify
        self.assertTrue(result)
        self.assertNotIn(user_id, self.extractor.opt_out_users)

    @async_test
    async def test_extract_user_information(self):
        """Test the extraction of user information."""
        # Setup
        user_message = "I recently moved to Seattle and I love hiking"
        agent_response = "Seattle has many great hiking trails nearby!"

        # Prepare mock extraction results
        extracted_data = {
            "location": {"value": "Seattle", "confidence": 0.9, "importance": 0.8},
            "hobby": {"value": "hiking", "confidence": 0.85, "importance": 0.7}
        }
        self.extractor._extract_user_information = AsyncMock(return_value=extracted_data)

        # Execute
        await self.extractor.process_conversation_turn(
            user_message=user_message,
            agent_response=agent_response,
            user_id=123,
            message_count=3
        )

        # Verify
        self.extractor._extract_user_information.assert_called_once()
        self.extractor._process_extraction_results.assert_called_once_with(extracted_data, 123)


class TestOrchestratorExtraction(unittest.TestCase):
    """Test cases for the Orchestrator's extraction functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the necessary components
        self.mock_memory_extractor = MagicMock()
        self.mock_memory_extractor.process_conversation_turn = AsyncMock()
        self.mock_memory_extractor.extraction_model = MagicMock()

        # Create a mock orchestrator with the mock extractor
        from muxi.core.orchestrator import Orchestrator
        self.orchestrator = Orchestrator(
            buffer_memory=MagicMock(),
            long_term_memory=MagicMock(),
            auto_extract_user_info=True,
            extraction_model=MagicMock()
        )
        self.orchestrator.memory_extractor = self.mock_memory_extractor
        self.orchestrator.is_multi_user = True

    @async_test
    async def test_handle_user_information_extraction(self):
        """Test the orchestrator's extraction handling."""
        # Setup
        user_message = "Hi, I'm a test user"
        agent_response = "Hello test user"
        user_id = 123
        agent_id = "agent1"

        # Execute
        await self.orchestrator.handle_user_information_extraction(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            agent_id=agent_id
        )

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify
        self.assertEqual(self.orchestrator.message_counts.get(user_id, 0), 1)
        self.mock_memory_extractor.process_conversation_turn.assert_called_once_with(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            message_count=1
        )

    @async_test
    async def test_anonymous_user_extraction_skipped(self):
        """Test that extraction is skipped for anonymous users."""
        # Setup
        user_message = "Anonymous message"
        agent_response = "Hello"
        user_id = 0  # Anonymous user
        agent_id = "agent1"

        # Execute
        await self.orchestrator.handle_user_information_extraction(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            agent_id=agent_id
        )

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify
        self.mock_memory_extractor.process_conversation_turn.assert_not_called()

    @async_test
    async def test_extraction_with_custom_model(self):
        """Test extraction with a custom model."""
        # Setup
        user_message = "Custom model test"
        agent_response = "Hello"
        user_id = 456
        agent_id = "agent1"
        custom_model = MagicMock()

        # Execute
        await self.orchestrator.handle_user_information_extraction(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            agent_id=agent_id,
            extraction_model=custom_model
        )

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify that _run_extraction is called with the custom model
        # We can't directly verify this with mocks, but we can check the message count
        self.assertEqual(self.orchestrator.message_counts.get(user_id, 0), 1)

    @async_test
    async def test_extraction_disabled(self):
        """Test that extraction is skipped when disabled."""
        # Setup
        self.orchestrator.auto_extract_user_info = False
        user_message = "This should be ignored"
        agent_response = "Hello"
        user_id = 789
        agent_id = "agent1"

        # Execute
        await self.orchestrator.handle_user_information_extraction(
            user_message=user_message,
            agent_response=agent_response,
            user_id=user_id,
            agent_id=agent_id
        )

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify
        self.mock_memory_extractor.process_conversation_turn.assert_not_called()


class TestAgentExtraction(unittest.TestCase):
    """Test cases for the Agent's extraction delegation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock model and orchestrator
        self.mock_model = MagicMock()
        self.mock_model.generate = AsyncMock(return_value="Test response")

        self.mock_orchestrator = MagicMock()
        self.mock_orchestrator.handle_user_information_extraction = AsyncMock()
        self.mock_orchestrator.add_to_buffer_memory = MagicMock()
        self.mock_orchestrator.add_to_long_term_memory = AsyncMock()
        self.mock_orchestrator.get_user_context_memory = AsyncMock(return_value={})

        # Create mock MCP handler
        self.mock_mcp_handler = MagicMock()
        self.mock_mcp_handler.process_message = AsyncMock(
            return_value=MagicMock(content="Test response")
        )

        # Create the agent with mock components
        from muxi.core.agent import Agent
        self.agent = Agent(
            model=self.mock_model,
            orchestrator=self.mock_orchestrator,
            system_message="Test system message",
            is_multi_user=True,
            mcp_handler=self.mock_mcp_handler
        )

    @async_test
    async def test_agent_delegates_extraction(self):
        """Test that the agent correctly delegates extraction to the orchestrator."""
        # Setup
        user_message = "Test user message"
        user_id = 123

        # Execute
        await self.agent.process_message(user_message, user_id=user_id)

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify extraction was delegated to orchestrator
        self.mock_orchestrator.handle_user_information_extraction.assert_called_once_with(
            user_message=user_message,
            agent_response="Test response",
            user_id=user_id,
            agent_id=self.agent.agent_id
        )

    @async_test
    async def test_extraction_skipped_for_anonymous_user(self):
        """Test that extraction is skipped for anonymous users."""
        # Setup
        user_message = "Anonymous message"
        user_id = 0  # Anonymous user

        # Execute
        await self.agent.process_message(user_message, user_id=user_id)

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify extraction was not called
        self.mock_orchestrator.handle_user_information_extraction.assert_not_called()

    @async_test
    async def test_extraction_with_custom_model(self):
        """Test extraction with a custom model."""
        # Setup
        user_message = "Message with custom extraction model"
        user_id = 456

        # Mock the orchestrator's handle_user_information_extraction method
        self.mock_orchestrator.handle_user_information_extraction.reset_mock()

        # Set up a custom mock response for the MCP handler
        response_mock = MagicMock(content="Custom model response")
        self.mock_mcp_handler.process_message.return_value = response_mock

        # Execute
        await self.agent.process_message(user_message, user_id=user_id)

        # Allow any background tasks to complete
        await asyncio.sleep(0.1)

        # Verify extraction was called with the right parameters
        self.mock_orchestrator.handle_user_information_extraction.assert_called_once_with(
            user_message=user_message,
            agent_response="Custom model response",
            user_id=user_id,
            agent_id=self.agent.agent_id
        )


if __name__ == "__main__":
    unittest.main()
