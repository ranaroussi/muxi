# MCP Feature Implementation

We've implemented three key features to enhance the MCP handler implementation:

## 1. Transport Factory

The `MCPTransportFactory` class provides a centralized way to create different transport instances based on configuration parameters. This improves code organization and makes it easier to add new transport types in the future.

```python
class MCPTransportFactory:
    """Factory class for creating MCP transport instances."""

    @staticmethod
    def create_transport(type: str, url_or_command: str, **kwargs) -> BaseTransport:
        """Create a transport instance based on type."""
        logger.info(f"Creating transport of type '{type}'")

        if type == "http":
            request_timeout = kwargs.get('request_timeout', 60)
            return HTTPSSETransport(url_or_command, request_timeout)
        elif type == "command":
            return CommandLineTransport(url_or_command)
        else:
            error_details = {
                "type": type,
                "supported_types": ["http", "command"],
                "timestamp": datetime.now().isoformat()
            }
            raise ValueError(f"Unsupported transport type: {type}", error_details)
```

Benefits:
- Encapsulates transport creation logic in one place
- Makes it easier to add new transport types
- Simplifies client code that needs different transports
- Centralizes transport configuration

## 2. Cancellation Support

The `CancellationToken` class enables cancellation of in-progress MCP operations. This is especially important for long-running operations and streaming responses.

```python
class CancellationToken:
    """A token that can be used to cancel async operations."""

    def __init__(self):
        self.cancelled = False
        self._tasks = set()

    def cancel(self):
        """Mark the token as cancelled and cancel all registered tasks."""
        self.cancelled = True
        for task in self._tasks:
            if not task.done():
                task.cancel()

    def register(self, task):
        """Register a task to be cancelled when this token is cancelled."""
        self._tasks.add(task)

    def throw_if_cancelled(self):
        """Throw an exception if this token has been cancelled."""
        if self.cancelled:
            raise MCPCancelledError("Operation was cancelled")
```

Usage:
- The token is passed through the call chain from high-level operations to low-level ones
- Tasks register themselves with the token
- Cancellation can be initiated at any level
- The token can be checked periodically to see if cancellation was requested

Example:

```python
# Create a cancellation token
token = CancellationToken()

# Start a background task
task = asyncio.create_task(long_running_operation(token))
token.register(task)

# Later, cancel the operation
token.cancel()
```

Benefits:
- Allows users to cancel long-running operations
- Prevents resources from being wasted on unwanted operations
- Provides clean cancellation paths throughout the codebase
- Supports both user-initiated and timeout-based cancellation

## 3. Improved Diagnostic Information

We've enhanced error reporting and logging to make troubleshooting easier. This includes:

- Custom exception classes with detailed error information
- Structured error details for all failure cases
- Comprehensive logging at all levels
- Connection and request statistics

### Custom Exception Classes

```python
class MCPError(Exception):
    """Base exception class for MCP-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(f"{message}" + (f": {json.dumps(details)}" if details else ""))

class MCPConnectionError(MCPError):
    """Exception raised for connection-related errors."""
    pass

class MCPRequestError(MCPError):
    """Exception raised for errors when making requests to MCP servers."""
    pass

class MCPTimeoutError(MCPError):
    """Exception raised when MCP operations time out."""
    pass

class MCPCancelledError(MCPError):
    """Exception raised when an MCP operation is cancelled."""
    pass
```

### Detailed Error Information

Each error includes structured details about the error context:

```python
error_details = {
    "status_code": response.status_code,
    "url": self.sse_url,
    "headers": dict(response.headers),
    "response_text": response.text[:500],
    "connection_time_s": connection_time,
    "timestamp": datetime.now().isoformat()
}
raise MCPConnectionError(
    f"Failed to connect to SSE endpoint (status {response.status_code})",
    error_details
)
```

### Connection Statistics

The `get_connection_stats()` method provides detailed information about connections:

```python
def get_connection_stats(self) -> Dict[str, Any]:
    """Get statistics about this connection."""
    stats = {
        "connected": self.connected,
        "type": "http",
        "base_url": self.base_url,
        "session_id": self.session_id,
        "current_time": datetime.now().isoformat()
    }

    if self.connect_time:
        stats["connect_time"] = self.connect_time.isoformat()
        stats["connection_age_s"] = (datetime.now() - self.connect_time).total_seconds()

    if self.last_activity:
        stats["last_activity"] = self.last_activity.isoformat()
        stats["idle_time_s"] = (datetime.now() - self.last_activity).total_seconds()

    return stats
```

Benefits:
- Easier troubleshooting of connection issues
- More informative error messages
- Better logging for production deployments
- Detailed metrics for monitoring

## Integration with MCPHandler

These features are integrated into the `MCPHandler` class:

- `MCPTransportFactory` is used in `connect_server()` to create transports
- `CancellationToken` is used in `process_message()` and `execute_tool()` to support cancellation
- Custom exceptions and detailed error information are used throughout for better diagnostics
- Connection statistics are available through the `get_connection_stats()` method

## Command-Line Transport Implementation

We've also implemented a full `CommandLineTransport` class that manages subprocess communication with command-line MCP servers. This supports:

- Starting a subprocess with the specified command
- Sending requests via stdin
- Reading responses from stdout
- Proper handling of process lifecycle and termination
- Error handling and diagnostics

This enables MUXI to work with command-line MCP servers like the Brave Search and Calculator examples.

## Next Steps

1. **Testing**: These features need comprehensive testing with various MCP servers and error scenarios.
2. **Documentation**: Update user-facing documentation to explain cancellation support and transport options.
3. **Monitoring**: Add instrumentation for tracking connection health and request performance.
4. **UI Integration**: Provide UI components for cancelling operations and viewing diagnostics.
