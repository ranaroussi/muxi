"""
Reconnection utility for handling connection retries with exponential backoff.

This module provides classes and functions to handle reconnection with
exponential backoff for services that may experience transient failures.
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Any, Callable, Dict, TypeVar, Union

from loguru import logger

# Type variables
T = TypeVar('T')  # Return type for retried functions
ExceptionType = TypeVar('ExceptionType', bound=Exception)  # Type of exception to retry on


class RetryConfiguration:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        jitter_factor: float = 0.1
    ):
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Exponential backoff multiplier
            jitter: Whether to add random jitter to delay
            jitter_factor: Factor to determine jitter amount (0.0-1.0)
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.jitter_factor = jitter_factor

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a retry attempt.

        Args:
            attempt: Current retry attempt number (1-based)

        Returns:
            Delay in seconds
        """
        # Calculate base delay with exponential backoff
        delay = min(
            self.initial_delay * (self.backoff_factor ** (attempt - 1)),
            self.max_delay
        )

        # Add jitter if enabled
        if self.jitter:
            jitter_amount = delay * self.jitter_factor
            delay = delay + random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)  # Ensure delay is non-negative


class RetryStats:
    """Statistics for retry operations."""

    def __init__(self):
        """Initialize retry statistics."""
        self.attempts = 0
        self.failures = 0
        self.last_attempt_time = None
        self.last_success_time = None
        self.last_failure_time = None
        self.total_delay = 0.0
        self.success = False

    def record_attempt(self):
        """Record an attempt."""
        self.attempts += 1
        self.last_attempt_time = datetime.now()

    def record_success(self):
        """Record a successful attempt."""
        self.success = True
        self.last_success_time = datetime.now()

    def record_failure(self, delay: float):
        """
        Record a failed attempt.

        Args:
            delay: Delay until next retry in seconds
        """
        self.failures += 1
        self.last_failure_time = datetime.now()
        self.total_delay += delay

    def get_stats(self) -> Dict[str, Any]:
        """
        Get retry statistics.

        Returns:
            Dictionary with retry statistics
        """
        stats = {
            "attempts": self.attempts,
            "failures": self.failures,
            "success": self.success,
            "total_delay": self.total_delay
        }

        if self.last_attempt_time:
            stats["last_attempt_time"] = self.last_attempt_time.isoformat()

        if self.last_success_time:
            stats["last_success_time"] = self.last_success_time.isoformat()

        if self.last_failure_time:
            stats["last_failure_time"] = self.last_failure_time.isoformat()

        return stats


async def retry_async(
    func: Callable[..., Any],
    retry_config: RetryConfiguration = None,
    retry_exceptions: Union[type, tuple] = Exception,
    on_retry: Callable[[int, Exception, float], None] = None,
    *args, **kwargs
) -> Any:
    """
    Execute an async function with retry logic.

    Args:
        func: Async function to execute
        retry_config: Configuration for retry behavior
        retry_exceptions: Exception type(s) to retry on
        on_retry: Callback function for retry events
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function

    Raises:
        Exception: The last exception that occurred if all retries fail
    """
    # Use default configuration if none provided
    config = retry_config or RetryConfiguration()
    stats = RetryStats()

    # Try the operation with retries
    last_exception = None

    for attempt in range(1, config.max_retries + 2):  # +2 because range is exclusive and we want the initial try
        stats.record_attempt()

        try:
            result = await func(*args, **kwargs)
            stats.record_success()
            return result

        except retry_exceptions as e:
            last_exception = e

            # If this was the last attempt, don't retry
            if attempt > config.max_retries:
                part1 = f"Operation failed after {config.max_retries + 1} attempts: "
                part2 = str(e)
                msg = part1 + part2
                logger.warning(msg)
                raise

            # Calculate delay
            delay = config.calculate_delay(attempt)
            stats.record_failure(delay)

            # Call retry callback if provided
            if on_retry:
                on_retry(attempt, e, delay)

            logger.info(
                f"Retry {attempt}/{config.max_retries} after error: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            # Wait before retrying
            await asyncio.sleep(delay)

    # We should never reach here due to the raise in the loop
    # but this keeps type checkers happy
    assert last_exception is not None
    raise last_exception


async def with_retries(
    operation_name: str,
    func: Callable[..., Any],
    retry_config: RetryConfiguration = None,
    retry_exceptions: Union[type, tuple] = Exception,
    *args, **kwargs
) -> Any:
    """
    Convenience wrapper for retry_async with logging.

    Args:
        operation_name: Name of the operation (for logging)
        func: Async function to execute
        retry_config: Configuration for retry behavior
        retry_exceptions: Exception type(s) to retry on
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function
    """
    def log_retry(attempt: int, exception: Exception, delay: float):
        """Log retry events."""
        exc_name = type(exception).__name__
        exc_str = str(exception)
        retry_msg = f"Retrying in {delay:.2f} seconds..."

        warning_msg = (
            f"{operation_name}: Attempt {attempt} failed with "
            f"{exc_name}: {exc_str}. {retry_msg}"
        )
        logger.warning(warning_msg)

    logger.info(f"Starting {operation_name} with retry support")
    start_time = time.time()

    try:
        result = await retry_async(
            func,
            retry_config=retry_config,
            retry_exceptions=retry_exceptions,
            on_retry=log_retry,
            *args, **kwargs
        )

        elapsed = time.time() - start_time
        logger.info(f"{operation_name} completed successfully in {elapsed:.2f} seconds")
        return result

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = (
            f"{operation_name} failed after {elapsed:.2f} seconds with "
            f"{type(e).__name__}: {str(e)}"
        )
        logger.error(error_msg)
        raise
