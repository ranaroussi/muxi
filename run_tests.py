#!/usr/bin/env python
"""
Test runner for the AI Agent Framework.

This script runs all unit tests in the tests directory.
"""

import unittest
import os
import sys


def discover_and_run_tests():
    """
    Discover and run all tests in the tests directory.

    Returns:
        True if all tests pass, False otherwise.
    """
    # Ensure the src directory is in the path
    sys.path.insert(0, os.path.abspath('.'))

    # Create a test loader
    loader = unittest.TestLoader()

    # Discover all tests in the tests directory
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the tests
    result = runner.run(suite)

    # Return True if all tests pass, False otherwise
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running AI Agent Framework tests...")
    success = discover_and_run_tests()

    if success:
        print("\n\033[92mAll tests passed!\033[0m")
        sys.exit(0)
    else:
        print("\n\033[91mSome tests failed!\033[0m")
        sys.exit(1)
