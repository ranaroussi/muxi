#!/usr/bin/env python
"""
Run all version-related tests.
"""

import unittest
import sys
import os

# Add the parent directory to sys.path to make imports work
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Import the test modules
from tests.test_cli_version import TestCLIVersionParsing, TestCLIVersionAsync  # noqa: E402
from tests.test_api_version import TestAPIVersion  # noqa: E402
from tests.test_version_util import TestVersionUtil  # noqa: E402


def run_tests():
    """Run all version-related tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()

    # Add tests to the suite
    test_suite.addTest(unittest.makeSuite(TestVersionUtil))
    test_suite.addTest(unittest.makeSuite(TestCLIVersionParsing))
    test_suite.addTest(unittest.makeSuite(TestCLIVersionAsync))
    test_suite.addTest(unittest.makeSuite(TestAPIVersion))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Return the number of failures
    return len(result.failures) + len(result.errors)


if __name__ == '__main__':
    sys.exit(run_tests())
