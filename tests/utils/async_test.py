"""
Helper module for running async tests with unittest.
"""

import asyncio
import functools
from typing import Callable, Any


def async_test(test_func: Callable) -> Callable:
    """
    Decorator for async test methods in unittest TestCase classes.

    This decorator ensures that async test methods are properly awaited
    when run by the unittest framework, which doesn't natively support async tests.

    Args:
        test_func: The async test function to be wrapped.

    Returns:
        A wrapper function that runs the async test in an event loop.
    """
    @functools.wraps(test_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create a new event loop if one doesn't exist
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(test_func(*args, **kwargs))
    return wrapper
