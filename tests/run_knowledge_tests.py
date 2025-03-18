#!/usr/bin/env python
"""
Run Knowledge Tests

This script runs all tests related to the knowledge functionality.
"""

import asyncio
import time
import unittest


class AsyncTestRunner(unittest.TextTestRunner):
    """Test runner that handles async tests properly."""

    def run(self, test):
        """Run the test, handling async methods properly."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create a new test that wraps async methods
        result = self._makeResult()
        startTime = time.time()
        try:
            test(result)
        finally:
            stopTime = time.time()
            timeTaken = stopTime - startTime
            result.printErrors()
            self.stream.writeln(result.separator2)
            run = result.testsRun
            self.stream.writeln(f"Ran {run} test{'s' if run != 1 else ''} in {timeTaken:.3f}s")
            self.stream.writeln()

            if not result.wasSuccessful():
                self.stream.write("FAILED (")
                failed, errored = list(map(len, (result.failures, result.errors)))
                if failed:
                    self.stream.write(f"failures={failed}")
                if errored:
                    if failed:
                        self.stream.write(", ")
                    self.stream.write(f"errors={errored}")
                self.stream.writeln(")")
            else:
                self.stream.writeln("OK")

        return result


def run_tests():
    """Run all knowledge-related tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add knowledge tests
    from test_agent_knowledge import TestAgentKnowledge
    from test_knowledge_handler import TestKnowledgeHandler

    test_suite.addTest(unittest.makeSuite(TestAgentKnowledge))
    test_suite.addTest(unittest.makeSuite(TestKnowledgeHandler))

    # Run the tests
    runner = AsyncTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run tests
    success = run_tests()

    # Exit with appropriate status code
    exit(0 if success else 1)
