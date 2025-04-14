# MUXI Framework Tracing System PRD

## 1. Introduction

This PRD defines the requirements and design for a comprehensive tracing system in the MUXI Framework. The tracing system will provide detailed visibility into the flow of communication between users, the orchestrator, agents, and MCP servers, enabling debugging, auditing, and performance analysis.

### 1.1 Background

The MUXI Framework currently has basic logging through Loguru but lacks a specialized tracing system that can follow the complete flow of communication through the system. With the increasing complexity of agent interactions, particularly with MCP servers and multi-agent orchestration, a more robust tracing system is needed to understand the flow of messages and requests.

### 1.2 Current State

The current system uses Loguru for general-purpose logging but does not:

- Track the complete flow of a user interaction through the system
- Correlate messages across different components
- Provide a comprehensive view of agent decision-making
- Support streaming of logs to external systems
- Offer a CLI for monitoring agent activity in real-time

## 2. Goals and Objectives

### 2.1 Primary Goals

- Create a tracing system that captures the complete flow of user interactions
- Implement tracing at the core/orchestration level, not per agent
- Support multiple output formats including stdout and file logs
- Enable streaming to external services like Papertrail or Kafka (through extensions)
- Provide a CLI command to watch logs in real-time
- Maintain a consistent trace ID across all components

### 2.2 Success Metrics

- Complete visibility of the communication flow from user to agent and back
- No significant performance overhead (<50ms per traced operation)
- Ability to correlate all actions related to a single user request
- Clear, human-readable log format for debugging
- Structured data for machine processing and analysis

## 3. Requirements

### 3.1 Functional Requirements

1. **Trace Lifecycle Management**
   - Generate unique trace IDs for each conversation/request
   - Propagate trace IDs through all components
   - Support user ID association with traces
   - Maintain trace context across asynchronous operations

2. **Component Tracing**
   - Track user messages and their source
   - Record orchestrator routing decisions
   - Log agent processing steps and thinking
   - Capture MCP server tool calls and results
   - Trace final responses back to the user

3. **Output Options**
   - Log to stdout for development and debugging
   - Support file logging with rotation and compression
   - Enable pluggable external sinks for enterprise use cases
   - Format logs appropriately for each output method

4. **CLI Tooling**
   - Implement `muxi trace` command to view logs
   - Support filtering by component, operation, and trace ID
   - Enable log following (similar to `tail -f`)
   - Provide clear, readable output formatting

### 3.2 Non-Functional Requirements

1. **Performance**
   - Minimal impact on response times
   - Efficient log generation and storage
   - Asynchronous logging where appropriate
   - Support for sampling in high-traffic environments

2. **Configuration**
   - Environment variable-based configuration
   - Enable/disable tracing at a global level
   - Component-specific tracing controls
   - Configurable log formats and levels

3. **Compatibility**
   - Work alongside existing Loguru logging
   - Support both development and production environments
   - Compatible with containerized deployments
   - Work with various external logging platforms

4. **Extensibility**
   - Pluggable architecture for adding new sink types
   - Support for custom formatters
   - Ability to add new trace event types
   - Well-defined interfaces for third-party extensions

## 4. System Design

### 4.1 Architecture Overview

The tracing system will consist of:

1. **Trace Configuration**: Central configuration for trace settings
2. **Tracer**: Singleton class for generating and managing traces
3. **Trace Context**: Object that carries trace information between components
4. **Trace Sinks**: Pluggable outputs for trace data
5. **CLI Interface**: Command-line tools for viewing traces

### 4.2 Trace Data Model

Each trace event will include:
- Timestamp (with millisecond precision)
- Trace ID (unique per conversation)
- Component ID (user, orchestrator, agent name, etc.)
- Operation (message, route, process, tool_call, etc.)
- Descriptive message
- Additional context data (structured)

### 4.3 Component Integration Points

The tracing system will integrate at these key points:

1. **User Input**
   - When user messages are received (API, CLI, WebSocket)
   - When responses are sent back to users

2. **Orchestrator**
   - When the orchestrator receives messages
   - When routing decisions are made
   - When messages are forwarded to agents
   - When responses are received from agents

3. **Agent**
   - When an agent receives a message
   - When an agent makes tool calls
   - When an agent receives tool results
   - When an agent generates a response

4. **MCP Handler**
   - When tool calls are made to MCP servers
   - When responses are received from MCP servers

## 5. Implementation Details

### 5.1 Configuration Module

```python
# Configuration class for tracing
class TracingConfig(BaseModel):
    """Tracing configuration settings."""

    enabled: bool = Field(
        default_factory=lambda: os.getenv("TRACING_ENABLED", "true").lower() == "true"
    )

    stdout: bool = Field(
        default_factory=lambda: os.getenv("TRACING_STDOUT", "true").lower() == "true"
    )

    file: Optional[str] = Field(default_factory=lambda: os.getenv("TRACING_FILE"))

    format: str = Field(
        default_factory=lambda: os.getenv(
            "TRACING_FORMAT",
            "[{time:YYYY-MM-DD HH:mm:ss.SSS}] | {level: <8} | {trace_id} | {component}:{operation} - {message}"
        )
    )

    level: str = Field(default_factory=lambda: os.getenv("TRACING_LEVEL", "TRACE"))

    components: List[str] = Field(
        default_factory=lambda: os.getenv("TRACING_COMPONENTS", "").split(",") or []
    )

    external_sink: Optional[str] = Field(default_factory=lambda: os.getenv("TRACING_EXTERNAL_SINK"))
```

### 5.2 Tracer Class

```python
class Tracer:
    """
    Singleton tracer class for generating and managing traces.
    """

    def __init__(self):
        """Initialize the tracer."""
        self._enabled = tracing_config.enabled
        self._trace_ids = {}  # Map of user_id -> trace_id

        if self._enabled:
            self._setup_handlers()

    def trace(self, component, operation, message, trace_id=None, data=None):
        """Record a trace event."""
        if not self._enabled:
            return

        trace_id = trace_id or self._generate_trace_id()

        # Create extra fields for the logger
        extra = {
            "is_trace": True,
            "trace_id": trace_id,
            "component": component,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if data:
            extra["data"] = json.dumps(data) if not isinstance(data, str) else data

        # Log the trace event
        logger.bind(**extra).log("TRACE", message)

    # Component-specific trace methods
    def user_message(self, message, user_id=None):
        """Trace a user message."""
        # Implementation

    def orchestrator_route(self, message, agent_id, trace_id=None):
        """Trace an orchestrator routing decision."""
        # Implementation

    def agent_processing(self, agent_id, trace_id=None):
        """Trace an agent processing a message."""
        # Implementation

    def agent_tool_call(self, agent_id, server_name, tool_name, params, trace_id=None):
        """Trace an agent making a tool call."""
        # Implementation

    def agent_tool_result(self, agent_id, server_name, tool_name, result, trace_id=None):
        """Trace an agent receiving a tool result."""
        # Implementation

    def agent_response(self, agent_id, response, trace_id=None):
        """Trace an agent sending a response."""
        # Implementation

    def orchestrator_response(self, response, trace_id=None):
        """Trace the orchestrator sending a response to the user."""
        # Implementation
```

### 5.3 CLI Command

```python
@cli_main.command()
@click.option("--file", default=None, help="Path to log file (defaults to stdout logs)")
@click.option("--follow", "-f", is_flag=True, help="Follow the log output")
@click.option("--component", default=None, help="Filter by component")
@click.option("--operation", default=None, help="Filter by operation")
@click.option("--trace-id", default=None, help="Filter by trace ID")
def trace(file, follow, component, operation, trace_id):
    """
    Watch and filter trace logs from MUXI agents.
    """
    # Implementation using tail and grep for file logs
    # Or filtering stdout for console logs
```

## 6. Integration Plan

### 6.1 Required Changes

1. **Configuration Integration**
   - Add tracing config to core configuration
   - Update environment variable handling

2. **Orchestrator Modifications**
   - Add trace ID generation in chat method
   - Add tracing points in routing logic
   - Pass trace context to agents

3. **Agent Modifications**
   - Add tracing in message processing
   - Add tracing around tool calls
   - Add tracing for response generation

4. **MCP Handler Modifications**
   - Add tracing for tool execution
   - Add tracing for tool responses

5. **CLI Updates**
   - Add trace command implementation
   - Update help documentation

### 6.2 Future Extensions

1. **Distributed Tracing Integration**
   - Support for OpenTelemetry protocol
   - Integration with Jaeger/Zipkin

2. **Advanced Analytics**
   - Performance metrics collection
   - Response time tracking
   - Tool usage statistics

3. **Web Dashboard**
   - Real-time trace visualization
   - Searching and filtering interface
   - Performance analytics

## 7. Example Trace Flow

For a user message "Tell me about climate change", the trace might look like:

```
[2023-05-15 10:15:22.123] | TRACE    | 6f8d9e2a | user:message - User sent: Tell me about climate change
[2023-05-15 10:15:22.145] | TRACE    | 6f8d9e2a | orchestrator:route - Routing message to agent 'research_agent'
[2023-05-15 10:15:22.156] | TRACE    | 6f8d9e2a | agent:process_start - Agent 'research_agent' processing message
[2023-05-15 10:15:22.789] | TRACE    | 6f8d9e2a | agent:tool_call - Agent 'research_agent' calling tool 'web_search' on server 'search_server'
[2023-05-15 10:15:23.456] | TRACE    | 6f8d9e2a | agent:tool_result - Agent 'research_agent' received result from tool 'web_search'
[2023-05-15 10:15:24.123] | TRACE    | 6f8d9e2a | agent:response - Agent 'research_agent' responded: Climate change refers to long-term shifts in temperatures...
[2023-05-15 10:15:24.145] | TRACE    | 6f8d9e2a | orchestrator:response - Orchestrator responding to user: Climate change refers to long-term shifts...
```

## 8. Conclusion

The tracing system will significantly enhance the observability of the MUXI Framework, providing clear visibility into the flow of information through the system and enabling better debugging, monitoring, and performance analysis. By implementing tracing at the core/orchestration level, we ensure consistent tracing across all components without requiring per-agent configuration.

---

# 9. MUXI Cloud Integration

## 9.1 Data Collection Architecture

For MUXI Cloud deployments, the tracing system will follow a clean separation of concerns:

1. **MUXI Framework** will:
   - Output all trace data to stdout in structured JSON format
   - Not include any direct integrations with external storage systems
   - Maintain all trace context and correlation within log messages

2. **External Collector Service** will:
   - Run independently from the MUXI Framework
   - Collect stdout logs from MUXI instances
   - Forward data to persistent storage
   - Handle retry logic, buffering, and error handling

This separation allows for flexibility in deployment scenarios while keeping the MUXI Framework focused on its core functionality.

## 9.2 Recommended Collection Stack

For high-performance tracing in MUXI Cloud, we recommend:

1. **Vector** as the collection agent:
   - Lightweight, high-performance log router
   - Native ClickHouse integration
   - Efficient batching and compression
   - Robust error handling and retry logic
   - Simple configuration for reading from stdout/files

2. **ClickHouse** as the storage backend:
   - Column-oriented storage optimized for trace queries
   - Buffer tables for efficient ingestion without Kafka
   - High compression ratio for log data
   - Excellent query performance for trace analysis
   - TTL support for automatic data lifecycle management

## 9.3 Sample ClickHouse Schema

```sql
-- Buffer table for ingestion
CREATE TABLE muxi_traces_buffer AS muxi_traces
ENGINE = Buffer(database, muxi_traces, 16, 10, 100, 10000, 1000000, 10000000, 100000000);

-- Main traces table with optimized storage
CREATE TABLE muxi_traces (
    timestamp DateTime64(3),
    trace_id String,
    component String,
    operation String,
    message String,
    user_id String,
    data String, -- JSON stored as string
    agent_id String,

    -- For partitioning and performance
    event_date Date DEFAULT toDate(timestamp),

    -- For efficient queries
    INDEX idx_trace_id trace_id TYPE bloom_filter GRANULARITY 4,
    INDEX idx_component component TYPE set(0) GRANULARITY 4,
    INDEX idx_operation operation TYPE set(0) GRANULARITY 4
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (trace_id, timestamp)
TTL event_date + INTERVAL 30 DAY; -- Retention policy
```

## 9.4 Sample Vector Configuration

```toml
[sources.muxi_stdout]
type = "file"
include = ["/var/log/muxi/*.log"]  # Or configure to read from stdout pipe

[transforms.parse_json]
type = "remap"
inputs = ["muxi_stdout"]
source = '''
  . = parse_json!(string!(.message))
'''

[sinks.clickhouse]
type = "clickhouse"
inputs = ["parse_json"]
database = "logs"
table = "muxi_traces_buffer"
endpoint = "http://clickhouse:8123"
compression = "gzip"
```

This architecture provides:

- Clean separation between framework and infrastructure
- High-performance log collection and storage
- Flexibility to deploy in various environments
- No dependencies on external message queues
- Efficient storage and querying for large-scale deployments
