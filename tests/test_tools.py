"""
Unit tests for the tools module.

This module contains tests for the tools implemented in the agent framework.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock

from src.tools.calculator import Calculator
from src.tools.web_search import WebSearch


class TestCalculator(unittest.TestCase):
    """Test cases for the Calculator tool."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = Calculator()

    def test_name_and_description(self):
        """Test that the name and description properties are set correctly."""
        self.assertEqual(self.calculator.name, "calculator")
        self.assertTrue(len(self.calculator.description) > 0)

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        test_cases = [
            ("2 + 2", "4"),
            ("10 - 5", "5"),
            ("3 * 4", "12"),
            ("10 / 2", "5"),
            ("2 ** 3", "8"),
            ("10 // 3", "3"),
            ("10 % 3", "1"),
            ("-5", "-5"),
            ("+5", "5")
        ]

        for expression, expected in test_cases:
            result = asyncio.run(self.calculator.execute(expression))
            self.assertIn("result", result)
            self.assertEqual(result["result"], expected)

    def test_math_functions(self):
        """Test mathematical functions."""
        test_cases = [
            ("sqrt(16)", "4"),
            ("sin(0)", "0"),
            ("cos(0)", "1"),
            ("abs(-5)", "5"),
            ("round(3.7)", "4"),
            ("pi", str(3.14159).rstrip('0').rstrip('.'))
        ]

        for expression, expected in test_cases:
            result = asyncio.run(self.calculator.execute(expression))
            self.assertIn("result", result)
            self.assertEqual(result["result"], expected)

    def test_invalid_expression(self):
        """Test handling of invalid expressions."""
        test_cases = [
            "import os",
            "os.system('ls')",
            "print('hello')",
            "def func(): pass",
            "1 + a",
            "unknown_func(5)"
        ]

        for expression in test_cases:
            result = asyncio.run(self.calculator.execute(expression))
            self.assertIn("error", result)

    def test_empty_input(self):
        """Test handling of empty input."""
        result = asyncio.run(self.calculator.execute(""))
        self.assertIn("error", result)

        result = asyncio.run(self.calculator.execute(None))
        self.assertIn("error", result)


class TestWebSearch(unittest.TestCase):
    """Test cases for the WebSearch tool."""

    def setUp(self):
        """Set up test fixtures."""
        # Create the WebSearch with direct parameters
        self.web_search = WebSearch(
            api_key="fake_api_key",
            search_engine_id="fake_engine_id"
        )

    def test_name_and_description(self):
        """Test that the name and description properties are set correctly."""
        self.assertEqual(self.web_search.name, "web_search")
        self.assertTrue(len(self.web_search.description) > 0)

    @patch("urllib.request.urlopen")
    def test_successful_search(self, mock_urlopen):
        """Test a successful web search."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = """
        {
            "items": [
                {
                    "title": "Test Result 1",
                    "link": "https://example.com/1",
                    "snippet": "This is the first test result."
                },
                {
                    "title": "Test Result 2",
                    "link": "https://example.com/2",
                    "snippet": "This is the second test result."
                }
            ]
        }
        """.encode()

        # Set up the mock to return our response
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_cm

        # Execute the search
        result = asyncio.run(self.web_search.execute("test query"))

        # Check the results
        self.assertIn("result", result)
        self.assertIn("search_results", result)
        self.assertEqual(len(result["search_results"]), 2)
        self.assertEqual(result["search_results"][0]["title"], "Test Result 1")
        self.assertEqual(result["search_results"][1]["link"], "https://example.com/2")

    @patch("src.tools.web_search.urllib.request.urlopen")
    def test_missing_credentials(self, mock_urlopen):
        """Test handling of missing API credentials."""
        # Create a WebSearch with no credentials
        web_search = WebSearch(api_key=None, search_engine_id=None)

        # Execute search
        result = asyncio.run(web_search.execute("test query"))

        # Verify response
        self.assertIn("error", result)
        self.assertIn("API key", result["error"])

    def test_empty_query(self):
        """Test handling of empty query."""
        result = asyncio.run(self.web_search.execute(""))
        self.assertIn("error", result)

        result = asyncio.run(self.web_search.execute(None))
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
