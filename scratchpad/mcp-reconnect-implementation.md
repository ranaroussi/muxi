# MCP Reconnection Implementation

## Overview

We've successfully implemented and tested a robust reconnection system for MCP connections with the following features:

1. **Exponential backoff** for retry attempts
2. **Jitter support** to prevent thundering herd problems
3. **Automatic reconnection** in case of disconnection
4. **Detailed statistics** for monitoring and diagnostics
5. **Comprehensive test suite** to validate behavior

## Implementation Details

### Retry Configuration

The `RetryConfiguration` class centralizes all retry behavior parameters:

```python
class RetryConfiguration:
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        jitter_factor: float = 0.1
    )
```

This allows for fine-tuning of the retry behavior:

- `max_retries`: Maximum number of retry attempts
- `initial_delay`: Initial delay in seconds
- `max_delay`: Maximum delay cap to prevent excessive waits
- `backoff_factor`: Exponential factor for increasing delays
- `jitter`: Whether to add random jitter to delays
- `jitter_factor`: Factor to control jitter amount

### Reconnection Utilities

The `reconnection.py` module provides core utilities:

1. **RetryConfiguration**: Parameters for retry behavior
2. **RetryStats**: Statistics for tracking retry attempts
3. **retry_async**: Low-level retry mechanism for async functions
4. **with_retries**: High-level wrapper with logging

### Enhanced MCP Handler

The `ReconnectingMCPHandler` extends `MCPHandler` with automatic reconnection capabilities:

```python
class ReconnectingMCPHandler(MCPHandler):
    def __init__(self, retry_config=None):
        self.retry_config = retry_config or RetryConfiguration()
        self._reconnection_in_progress = {}
```

Key improvements:

1. **connect_server**: Uses retry mechanism with exponential backoff
2. **execute_tool**: Automatically retries on connection errors
3. **list_tools**: Adds retry support for tool listing
4. **get_retry_stats**: Provides detailed statistics about retry operations

### Retry Process Flow

The retry process follows this flow:

1. Operation is attempted
2. If successful, return the result
3. If failed with a retriable exception:
   - Calculate delay with exponential backoff and jitter
   - Wait for the calculated delay
   - Retry the operation
4. Continue until success or max retries exceeded

### Automatic Reconnection

The handler can automatically reconnect when:

1. A disconnection is detected during tool execution
2. The server is not connected when a tool execution is requested

The reconnection process is protected against multiple concurrent reconnection attempts with a locking mechanism.

## Testing

The test suite in `tests/test_reconnection.py` validates the reconnection behavior:

1. **Connection tests**:
   - Basic connection with retry
   - Multiple retries before success
   - Exceeding max retries

2. **Tool execution tests**:
   - Execute tool with reconnection when connected
   - Execute tool when disconnected
   - List tools with retry

3. **Statistics tests**:
   - Verify retry statistics

The test suite uses a specially designed `UnstableTransport` mock that can simulate various connection failure patterns.

## Usage Example

```python
# Create a handler with custom retry configuration
retry_config = RetryConfiguration(
    max_retries=5,
    initial_delay=0.5,
    max_delay=30.0,
    backoff_factor=2.0,
    jitter=True
)
handler = ReconnectingMCPHandler(retry_config=retry_config)

# Connect to server with retry support
await handler.connect_server(
    server_id="my_server",
    server_url="https://mcpify.ai/v1",
    type="http"
)

# Execute tools with automatic reconnection
result = await handler.execute_tool(
    tool_name="weather_tool",
    params={"location": "San Francisco"}
)

# Get retry statistics
stats = handler.get_retry_stats()
print(f"Retry configuration: {stats['retry_config']}")
print(f"Connection stats: {stats.get('connection_stats', {})}")
```

## Future Improvements

1. **Advanced Retry Policies**:
   - Custom retry decision logic
   - Per-server retry configurations
   - Different retry policies for different error types

2. **Enhanced Monitoring**:
   - Real-time retry statistics
   - Alerts for excessive retries
   - Integration with monitoring systems

3. **Circuit Breaker Pattern**:
   - Automatic suspension of retries when a server consistently fails
   - Gradual recovery testing
   - Fallback mechanisms
