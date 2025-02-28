"""
Test the version utility function.
"""

import unittest
from unittest.mock import patch, mock_open

from src.utils import get_version


class TestVersionUtil(unittest.TestCase):
    """Test the version utility function."""

    def test_get_version_file_exists(self):
        """Test get_version when the file exists."""
        test_version = "0.0.1"

        # Mock the open function
        with patch('builtins.open', mock_open(read_data=test_version)):
            # Mock os.path.join to return a predictable path
            with patch('os.path.join', return_value="/fake/path/src/.version"):
                version = get_version()
                self.assertEqual(version, test_version)

    def test_get_version_file_not_found(self):
        """Test get_version when the file doesn't exist."""
        # Mock open to raise FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError()):
            version = get_version()
            self.assertEqual(version, "0.0.0")  # Default version

    def test_get_version_strips_whitespace(self):
        """Test get_version properly strips whitespace."""
        test_version = "0.0.1\n"  # Version with newline

        # Mock the open function
        with patch('builtins.open', mock_open(read_data=test_version)):
            # Mock os.path.join to return a predictable path
            with patch(
                'os.path.join',
                return_value="/fake/path/src/.version"
            ):
                version = get_version()
                self.assertEqual(version, "0.0.1")  # Should be stripped


if __name__ == '__main__':
    unittest.main()
