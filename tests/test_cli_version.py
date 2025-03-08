"""
Test the CLI version flag functionality.
"""

import io
import unittest
from unittest.mock import MagicMock, patch

from src.cli.app import parse_args, run_cli_async


class TestCLIVersionParsing(unittest.TestCase):
    """Test the CLI version flag parsing."""

    @patch("sys.argv", ["cli.py", "--version"])
    @patch("src.utils.get_version")
    def test_version_flag_parsing(self, mock_get_version):
        """Test that the --version flag is properly parsed."""
        mock_get_version.return_value = "0.0.1"
        args = parse_args()
        self.assertTrue(args.version)


class TestCLIVersionAsync(unittest.IsolatedAsyncioTestCase):
    """Test the CLI version flag async functionality."""

    @patch("asyncio.run")
    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("src.utils.get_version")
    @patch("src.cli.app.parse_args")
    async def test_version_flag_output(
        self, mock_parse_args, mock_get_version, mock_stdout, mock_run
    ):
        """Test that the version is printed when --version flag is used."""
        # Setup mocks
        test_version = "0.0.1"
        mock_get_version.return_value = test_version
        mock_args = MagicMock()
        mock_args.version = True
        mock_parse_args.return_value = mock_args

        # Call the function
        await run_cli_async()

        # Verify that we show the version information
        output = mock_stdout.getvalue()
        self.assertIn("MUXI Framework version", output)

        # Remove ANSI color codes and check for version
        clean_output = output.replace("\x1b[1;36m", "")
        clean_output = clean_output.replace("\x1b[0m", "")
        clean_output = clean_output.replace("\x1b[1m", "")
        self.assertIn(test_version, clean_output)

        # Ensure we don't proceed further when --version is specified
        mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
