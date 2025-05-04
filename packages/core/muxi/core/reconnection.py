# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Reconnection - Robust Connection Retry Utilities
# Description:  Utilities for handling connection retries with exponential backoff
# Role:         Provides resilience for network operations and external connections
# Usage:        Used by any component that connects to external services
# Author:       Muxi Framework Team
#
# The reconnection module provides robust retry logic for external service
# connections that may experience transient failures. It features:
#
# 1. Sophisticated Retry Logic
#    - Configurable exponential backoff strategy
#    - Jitter to prevent thundering herd problems
#    - Detailed statistics tracking for monitoring
#
# 2. Async First Design
#    - Built for asyncio environments
#    - Non-blocking delays between retries
#    - Integration with the event loop
#
# 3. Comprehensive Logging
#    - Detailed operation tracking
#    - Time measurement for performance analysis
#    - Structured error reporting
#
# This module is used by many components in the framework that need to establish
# resilient connections to external services like databases, APIs, or model providers.
# It implements industry best practices for handling transient connection issues.
#
# Example usage:
#
#   result = await with_retries(
#       "database_connection",
#       connect_to_database,
#       retry_config=RetryConfiguration(max_retries=5),
#       retry_exceptions=(ConnectionError, TimeoutError)
#   )
# =============================================================================

import asyncio
import random
import time
from datetime import datetime
from typing import Any, Callable, Dict, TypeVar, Union

from loguru import logger

# Type variables
T = TypeVar("T")  # Return type for retried functions
ExceptionType = TypeVar("ExceptionType", bound=Exception)  # Type of exception to retry on


class RetryConfiguration:
    """
    Configuration for retry behavior.

    This class encapsulates the parameters that control the retry behavior,
    including the number of retries, delays between attempts, and jitter settings.
    It provides methods to calculate appropriate delays between retry attempts.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        jitter_factor: float = 0.1,
    ):
        """
        Initialize retry configuration with customizable parameters.

        Creates a configuration object that controls how retries are performed.
        All parameters have sensible defaults that work well for most scenarios,
        but can be customized for specific requirements.

        Args:
            max_retries: Maximum number of retry attempts before giving up.
                Default of 3 means up to 4 total attempts (initial + 3 retries).
            initial_delay: Initial delay in seconds before the first retry.
                This is the base delay that gets multiplied for subsequent retries.
            max_delay: Maximum delay in seconds between retries, caps exponential growth.
                Prevents extremely long delays after many retries.
            backoff_factor: Exponential backoff multiplier (how quickly delay increases).
                A factor of 2.0 doubles the delay with each retry.
            jitter: Whether to add random jitter to delay to prevent thundering herd problems.
                Recommended to keep enabled for distributed systems.
            jitter_factor: Factor to determine jitter amount as a proportion of delay (0.0-1.0).
                Higher values add more randomness to the delays.
        """
        # Store configuration parameters
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.jitter_factor = jitter_factor

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a retry attempt using exponential backoff with optional jitter.

        The delay increases exponentially with each attempt, optionally adding random
        jitter to prevent synchronized retry storms in distributed systems.

        Args:
            attempt: Current retry attempt number (1-based). The first retry has attempt=1.

        Returns:
            Delay in seconds to wait before the next retry attempt.
            The actual delay follows the formula:
            min(initial_delay * (backoff_factor^(attempt-1)), max_delay)
            with optional jitter applied within the range of ±(delay * jitter_factor).
        """
        # Calculate base delay with exponential backoff
        # Formula: initial_delay * (backoff_factor ^ (attempt-1))
        # Example: 1.0 * (2.0 ^ (3-1)) = 4.0 seconds for the 3rd attempt with default settings
        delay = min(self.initial_delay * (self.backoff_factor ** (attempt - 1)), self.max_delay)

        # Add jitter if enabled to prevent synchronized retries across multiple clients
        if self.jitter:
            # Calculate jitter amount based on current delay and jitter factor
            jitter_amount = delay * self.jitter_factor
            # Add random jitter within range [-jitter_amount, +jitter_amount]
            delay = delay + random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)  # Ensure delay is non-negative, even with negative jitter


class RetryStats:
    """
    Statistics for retry operations.

    This class tracks and stores metrics about retry attempts, including counts of
    attempts and failures, timestamps of events, and accumulated delay time.
    It provides a comprehensive view of how a retry operation performed.
    """

    def __init__(self):
        """
        Initialize retry statistics with default values.

        Sets up counters and timestamps to track the retry process from start to finish.
        All timestamps start as None until their respective events occur.
        All counters start at zero.
        """
        self.attempts = 0  # Counter for total number of attempts made
        self.failures = 0  # Counter for failed attempts
        self.last_attempt_time = None  # Timestamp of most recent attempt
        self.last_success_time = None  # Timestamp of most recent successful attempt
        self.last_failure_time = None  # Timestamp of most recent failed attempt
        self.total_delay = 0.0  # Accumulated delay time between retries in seconds
        self.success = False  # Flag indicating if operation eventually succeeded

    def record_attempt(self):
        """
        Record a retry attempt.

        Increments the attempt counter and updates the timestamp for the most recent attempt.
        This should be called before each attempt is made, including the initial attempt.
        """
        self.attempts += 1  # Increment the attempt counter
        self.last_attempt_time = datetime.now()  # Store current time as the attempt time

    def record_success(self):
        """
        Record a successful attempt.

        Sets the success flag to True and updates the timestamp for the successful attempt.
        This should be called when an attempt succeeds and the retry process completes.
        """
        self.success = True  # Mark the operation as successful
        self.last_success_time = datetime.now()  # Store current time as the success time

    def record_failure(self, delay: float):
        """
        Record a failed attempt and the delay until the next retry.

        Increments the failure counter, updates the timestamp for the most recent failure,
        and adds the delay time to the total accumulated delay.

        Args:
            delay: Delay until next retry in seconds, used to calculate total wait time.
                This is the actual delay that will be applied before the next attempt.
        """
        self.failures += 1  # Increment the failure counter
        self.last_failure_time = datetime.now()  # Store current time as the failure time
        self.total_delay += delay  # Add the delay to the total accumulated delay

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive retry statistics as a dictionary.

        Compiles all tracked statistics into a dictionary format suitable for logging,
        monitoring, or debugging purposes. Timestamps are converted to ISO format strings.

        Returns:
            Dictionary with retry statistics including counts, flags, and timestamps.
            Keys include:
            - attempts: Total number of attempts made
            - failures: Number of failed attempts
            - success: Whether the operation eventually succeeded
            - total_delay: Total time spent waiting between retries
            - Various timestamps if set (last_attempt_time, last_success_time, last_failure_time)
        """
        # Create base dictionary with numeric values and success flag
        stats = {
            "attempts": self.attempts,
            "failures": self.failures,
            "success": self.success,
            "total_delay": self.total_delay,
        }

        # Add timestamps to the dictionary if they exist
        # Convert datetime objects to ISO format strings for better readability and serialization
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
    *args,
    **kwargs,
) -> Any:
    """
    Execute an async function with retry logic.

    This function attempts to execute the provided async function and retries it
    if it fails with specified exceptions. It uses exponential backoff with optional
    jitter to space out retry attempts.

    Args:
        func: Async function to execute. This is the operation that may fail.
        retry_config: Configuration for retry behavior. If None, uses default settings.
        retry_exceptions: Exception type(s) to retry on. Can be a single exception type
            or a tuple of exception types. Default is base Exception which retries on any error.
        on_retry: Callback function for retry events. Called after each failed attempt with
            the attempt number, exception, and delay until next retry.
        *args: Arguments for the function being retried.
        **kwargs: Keyword arguments for the function being retried.

    Returns:
        Result of the successful function call.

    Raises:
        Exception: The last exception that occurred if all retries fail.
            This will be an instance of one of the retry_exceptions types.
    """
    # Use default configuration if none provided
    config = retry_config or RetryConfiguration()

    # Initialize statistics tracking for this retry operation
    stats = RetryStats()

    # Try the operation with retries
    last_exception = None

    # Loop through attempts (initial attempt + retries)
    for attempt in range(1, config.max_retries + 2):
        # +2 because range is exclusive and we want the initial try plus all retries

        # Record this attempt in our statistics
        stats.record_attempt()

        try:
            # Attempt to execute the function
            result = await func(*args, **kwargs)

            # If successful, record success in statistics
            stats.record_success()

            # Return the successful result
            return result

        except retry_exceptions as e:
            # Store the exception in case this is the last attempt
            last_exception = e

            # If this was the last attempt, don't retry
            if attempt > config.max_retries:
                # Construct a detailed error message
                part1 = f"Operation failed after {config.max_retries + 1} attempts: "
                part2 = str(e)
                msg = part1 + part2

                # Log the final failure
                logger.warning(msg)

                # Re-raise the last exception to signal failure to caller
                raise

            # Calculate delay using the retry configuration (implements backoff strategy)
            delay = config.calculate_delay(attempt)

            # Record this failure in our statistics
            stats.record_failure(delay)

            # Call retry callback if provided (allows for custom handling of retries)
            if on_retry:
                on_retry(attempt, e, delay)

            # Log the retry attempt with details
            logger.info(
                f"Retry {attempt}/{config.max_retries} after error: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            # Wait before retrying - using asyncio.sleep to not block the event loop
            # This allows other tasks to run during the delay period
            await asyncio.sleep(delay)

    # We should never reach here due to the raise in the loop
    # but this keeps type checkers happy by ensuring we always either return or raise
    assert last_exception is not None
    raise last_exception


async def with_retries(
    operation_name: str,
    func: Callable[..., Any],
    retry_config: RetryConfiguration = None,
    retry_exceptions: Union[type, tuple] = Exception,
    *args,
    **kwargs,
) -> Any:
    """
    Convenience wrapper for retry_async with logging.

    This function provides a higher-level interface to retry_async with additional
    logging and timing information. It's useful for operations that need to be
    retried with proper logging of attempts and outcomes.

    Args:
        operation_name: Name of the operation (for logging). This string appears
            in all log messages to identify the operation.
        func: Async function to execute. This is the operation that may fail.
        retry_config: Configuration for retry behavior. If None, uses default settings.
        retry_exceptions: Exception type(s) to retry on. Can be a single exception type
            or a tuple of exception types.
        *args: Arguments for the function being retried.
        **kwargs: Keyword arguments for the function being retried.

    Returns:
        Result of the successful function call.

    Raises:
        Exception: Re-raises any exception that occurs after all retries fail.
            This will be an instance of one of the retry_exceptions types.
    """

    def log_retry(attempt: int, exception: Exception, delay: float):
        """
        Log retry events.

        This inner function provides consistent logging for retry attempts.
        It formats and logs warning messages with details about the retry attempt.

        Args:
            attempt: The current retry attempt number
            exception: The exception that triggered the retry
            delay: The delay before the next retry attempt
        """
        # Extract exception details for logging
        exc_name = type(exception).__name__
        exc_str = str(exception)
        retry_msg = f"Retrying in {delay:.2f} seconds..."

        # Format a comprehensive warning message
        warning_msg = (
            f"{operation_name}: Attempt {attempt} failed with "
            f"{exc_name}: {exc_str}. {retry_msg}"
        )
        # Log at warning level to highlight the retry event
        logger.warning(warning_msg)

    # Log the start of the operation
    logger.info(f"Starting {operation_name} with retry support")
    # Record the start time for calculating total operation duration
    start_time = time.time()

    try:
        # Attempt the operation with retry logic
        # Pass our custom log_retry function to handle retry notifications
        result = await retry_async(
            func,
            retry_config=retry_config,
            retry_exceptions=retry_exceptions,
            on_retry=log_retry,  # Use our custom logging function
            *args,
            **kwargs,
        )

        # Calculate and log the total elapsed time on success
        elapsed = time.time() - start_time
        logger.info(f"{operation_name} completed successfully in {elapsed:.2f} seconds")
        # Return the successful result to the caller
        return result

    except Exception as e:
        # If all retries failed, we'll end up here
        # Calculate and log the total elapsed time on failure
        elapsed = time.time() - start_time
        # Create a detailed error message with exception information
        error_msg = (
            f"{operation_name} failed after {elapsed:.2f} seconds with "
            f"{type(e).__name__}: {str(e)}"
        )
        # Log at error level since this is a complete failure after all retries
        logger.error(error_msg)
        raise  # Re-raise the exception to the caller
