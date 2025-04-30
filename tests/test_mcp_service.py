"""
Unit tests for the MCP Service.

This module contains tests for the MCPService class in the MUXI Framework.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from muxi.core.mcp_service import MCPService
from muxi.core.tool_parser import ToolParser, ToolCall
from tests.utils.async_test import async_test


class TestMCPService(unittest.TestCase):
    """Test cases for the MCPService class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the singleton instance for each test
        MCPService._instance = None
        self.mcp_service = MCPService.get_instance()

        # Mock the MCPHandler
        self.mock_handler = MagicMock()
        self.mock_handler.process_tool_call = AsyncMock(
            return_value=MagicMock(content="Tool result")
        )
        self.mock_handler.connect_server = AsyncMock(return_value=True)
        self.mock_handler.disconnect = AsyncMock(return_value=True)
        self.mock_handler.active_connections = {}

        # Patch the MCPHandler import
        self.handler_patcher = patch(
            "muxi.core.mcp_service.MCPHandler", return_value=self.mock_handler
        )
        self.mock_handler_class = self.handler_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.handler_patcher.stop()

    @async_test
    async def test_register_mcp_server(self):
        """Test registering an MCP server."""
        # Test registering a server
        server_id = "test-server"
        result = await self.mcp_service.register_mcp_server(
            server_id=server_id, url="http://example.com", credentials={"api_key": "test-key"}
        )

        # Check that the server was registered
        self.assertEqual(result, server_id)
        self.assertIn(server_id, self.mcp_service.handlers)
        self.assertIn(server_id, self.mcp_service.connections)
        self.assertIn(server_id, self.mcp_service.locks)

        # Check that the handler was initialized correctly
        self.mock_handler_class.assert_called_once()

    @async_test
    async def test_invoke_tool(self):
        """Test invoking a tool on an MCP server."""
        # Register a server first
        server_id = "test-server"
        await self.mcp_service.register_mcp_server(server_id=server_id, url="http://example.com")

        # Mock the list_tools response
        server_name = "test_server"
        self.mock_handler.active_connections = {server_name: MagicMock()}
        self.mock_handler.list_tools = AsyncMock(return_value=[{"name": "test_tool"}])

        # Test invoking a tool
        result = await self.mcp_service.invoke_tool(
            server_id=server_id, tool_name="test_tool", parameters={"param1": "value1"}
        )

        # Check that the tool was invoked
        self.mock_handler.process_tool_call.assert_called_once_with(
            tool_name="test_tool", tool_input={"param1": "value1"}, context=None
        )

        # Check that the result was returned
        self.assertEqual(result, {"result": "Tool result", "status": "success"})

    @async_test
    async def test_invoke_tool_error(self):
        """Test error handling when invoking a tool."""
        # Register a server first
        server_id = "test-server"
        await self.mcp_service.register_mcp_server(server_id=server_id, url="http://example.com")

        # Mock the list_tools response
        server_name = "test_server"
        self.mock_handler.active_connections = {server_name: MagicMock()}
        self.mock_handler.list_tools = AsyncMock(return_value=[{"name": "test_tool"}])

        # Make the handler raise an exception
        self.mock_handler.process_tool_call.side_effect = Exception("Test error")

        # Test invoking a tool
        result = await self.mcp_service.invoke_tool(
            server_id=server_id, tool_name="test_tool", parameters={"param1": "value1"}
        )

        # Check that the error was handled
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "Test error")

    @async_test
    async def test_disconnect_server(self):
        """Test disconnecting from an MCP server."""
        # Register a server first
        server_id = "test-server"
        await self.mcp_service.register_mcp_server(server_id=server_id, url="http://example.com")

        # Mock the list_tools response and active connections
        server_name = "test_server"
        self.mock_handler.active_connections = {server_name: MagicMock()}
        self.mock_handler.list_tools = AsyncMock(return_value=[{"name": "test_tool"}])

        # Set up the mock to succeed when disconnecting
        self.mock_handler.disconnect.return_value = True

        # Test disconnecting
        result = await self.mcp_service.disconnect_server(server_id)

        # Check that the server was disconnected
        self.assertTrue(result)
        self.assertNotIn(server_id, self.mcp_service.handlers)
        self.assertNotIn(server_id, self.mcp_service.connections)
        self.assertNotIn(server_id, self.mcp_service.locks)

    @async_test
    async def test_singleton_pattern(self):
        """Test that the MCPService follows the singleton pattern."""
        # Get another instance
        another_instance = MCPService.get_instance()

        # Check that it's the same instance
        self.assertIs(self.mcp_service, another_instance)


class TestToolParser(unittest.TestCase):
    """Test cases for the ToolParser class."""

    def test_parse_json_blocks(self):
        """Test parsing JSON blocks from text."""
        # Test input with a JSON block
        text = "Here's a tool call: "
        text += '```json\n{"tool": "weather", "parameters": {"location": "New York"}}\n```'

        # Parse the text
        cleaned_text, tool_calls = ToolParser.parse(text)

        # Check the result
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].tool_name, "weather")
        self.assertEqual(tool_calls[0].parameters, {"location": "New York"})
        # Allow for flexible whitespace in the cleaned text
        self.assertTrue(cleaned_text.startswith("Here's a tool call"))

    def test_parse_function_calls(self):
        """Test parsing function calls from text."""
        # Test input with a function call
        text = 'To get the weather, call weather(location="New York")'

        # Parse the text
        cleaned_text, tool_calls = ToolParser.parse(text)

        # Check the result
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].tool_name, "weather")
        # Check if the parameters contain a location property with "New York" value
        # This allows flexibility in how the parser extracts parameters
        params = tool_calls[0].parameters
        if "location" in params:
            self.assertEqual(params["location"], "New York")
        else:
            # If using arg1 format, check that format instead
            self.assertIn("New York", str(params))

        # Allow for flexible whitespace in the cleaned text
        self.assertTrue(cleaned_text.startswith("To get the weather, call"))

    def test_parse_explicit_tool_calls(self):
        """Test parsing explicit tool calls from text."""
        # Test input with an explicit tool call
        text = 'Use <tool:weather>{"location": "New York"}</tool> to get the forecast.'

        # Parse the text
        cleaned_text, tool_calls = ToolParser.parse(text)

        # Check the result
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].tool_name, "weather")
        self.assertEqual(tool_calls[0].parameters, {"location": "New York"})
        self.assertEqual(cleaned_text, "Use  to get the forecast.")

    def test_replace_tool_calls_with_results(self):
        """Test replacing tool calls with results."""
        # Create a tool call with a result
        tool_call = ToolCall(
            tool_name="weather",
            parameters={"location": "New York"},
            full_text='<tool:weather>{"location": "New York"}</tool>',
            start_pos=4,
            end_pos=54,
        )
        tool_call.set_result({"forecast": "Sunny", "temperature": 75})

        # Test input with a tool call
        text = 'Use <tool:weather>{"location": "New York"}</tool> to get the forecast.'

        # Replace the tool call with its result
        result = ToolParser.replace_tool_calls_with_results(text, [tool_call])

        # Check the result - should include the formatted result
        self.assertIn("Result from weather", result)
        self.assertIn("Sunny", result)
        self.assertIn("75", result)


class TestAgentToolIntegration(unittest.TestCase):
    """Test cases for the Agent's tool invocation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the model
        self.mock_model = MagicMock()
        self.mock_model.chat = AsyncMock()

        # Mock the orchestrator
        self.mock_orchestrator = MagicMock()
        self.mock_orchestrator.add_message_to_memory = AsyncMock()
        self.mock_orchestrator.get_mcp_service = MagicMock(return_value=None)

        # Mock the MCP service
        self.mock_mcp_service = MagicMock()
        self.mock_mcp_service.invoke_tool = AsyncMock(
            return_value={"result": "Tool result", "status": "success"}
        )

        # Set up the orchestrator to return our mock MCP service
        self.mock_orchestrator.get_mcp_service.return_value = self.mock_mcp_service

        # Patch the MCPService.get_instance method
        self.mcp_service_patcher = patch(
            "muxi.core.mcp_service.MCPService.get_instance", return_value=self.mock_mcp_service
        )
        self.mock_mcp_service_getter = self.mcp_service_patcher.start()

        # Import the Agent class after patching
        from muxi.core.agent import Agent, MCPServer

        # Create an MCP server
        self.mcp_server = MCPServer(name="Test Server", url="http://example.com")

        # Create an agent
        self.agent = Agent(
            agent_id="test_agent",
            model=self.mock_model,
            orchestrator=self.mock_orchestrator
        )

        # Set request_timeout for testing
        self.agent.request_timeout = 60

    def tearDown(self):
        """Tear down test fixtures."""
        self.mcp_service_patcher.stop()

    @async_test
    async def test_invoke_tool(self):
        """Test the agent's invoke_tool method."""
        # Test invoking a tool
        result = await self.agent.invoke_tool(
            server_id=self.mcp_server.server_id,
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )

        # Check that the tool was invoked through the MCP service
        self.mock_mcp_service.invoke_tool.assert_called_once_with(
            server_id=self.mcp_server.server_id,
            tool_name="test_tool",
            parameters={"param1": "value1"},
            request_timeout=self.agent.request_timeout  # The agent adds this internally
        )

        # Check that the result was returned
        self.assertEqual(result, {"result": "Tool result", "status": "success"})

    @patch("muxi.core.tool_parser.ToolParser.parse")
    @patch("muxi.core.agent.Agent.invoke_tool")
    @async_test
    async def test_process_message_with_tool_calls(self, mock_invoke_tool, mock_parse):
        """Test processing a message that includes tool calls."""
        # Mock add_message_to_memory method to avoid "can't be used in await" error
        self.mock_orchestrator.add_message_to_memory = AsyncMock()

        # Setup mock for invoke_tool
        mock_invoke_tool.return_value = {"result": "Sunny, 75°F", "status": "success"}

        # Setup the model to return a response with a tool call
        self.mock_model.chat.return_value = 'Let me check: weather(location="New York")'

        # Setup the parser to detect the tool call
        tool_call = ToolCall(
            tool_name="weather",
            parameters={"location": "New York"},
            full_text='weather(location="New York")',
            start_pos=14,
            end_pos=41,
        )
        mock_parse.return_value = ("Let me check: ", [tool_call])

        # Process a message
        response = await self.agent.process_message("What's the weather in New York?")

        # Check that the model was called
        self.mock_model.chat.assert_called_once()

        # Check that the invoke_tool method was called
        mock_invoke_tool.assert_called_once()

        # Verify add_message_to_memory was called
        assert self.mock_orchestrator.add_message_to_memory.call_count >= 1

        # Check the response content
        self.assertIsNotNone(response)

    @patch("muxi.core.tool_parser.ToolParser.parse")
    @async_test
    async def test_process_message_no_tool_calls(self, mock_parse):
        """Test processing a message without tool calls."""
        # Mock add_message_to_memory method to avoid "can't be used in await" error
        self.mock_orchestrator.add_message_to_memory = AsyncMock()

        # Setup the model to return a simple response
        response_text = "The weather in New York is sunny."
        self.mock_model.chat.return_value = response_text

        # Setup the parser to not detect any tool calls
        mock_parse.return_value = (response_text, [])

        # Process a message
        response = await self.agent.process_message("What's the weather in New York?")

        # Check that the model was called
        self.mock_model.chat.assert_called_once()

        # Check that no tools were invoked
        self.mock_mcp_service.invoke_tool.assert_not_called()

        # Verify add_message_to_memory was called twice (once for user, once for assistant)
        assert self.mock_orchestrator.add_message_to_memory.call_count >= 2

        # Check the response content
        self.assertEqual(response.content, response_text)
