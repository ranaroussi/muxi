# Tools

Tools extend the capabilities of AI agents by enabling them to perform specific actions or retrieve information beyond their training data.

## What are Tools?

Tools are specialized functions that agents can use to:
- Access external data sources and APIs
- Perform calculations
- Execute code
- Interact with databases
- Manipulate files and documents
- And much more...

## Tools vs MCP: Understanding the Distinction

It's important to understand how tools relate to the Modern Control Protocol (MCP) in the agent framework:

### Tools are Functional Extensions, Not the Protocol

- **Tools**: Specific capabilities that execute in your application environment, allowing the agent to perform actions like web searches, calculations, or API calls.

- **MCP (Modern Control Protocol)**: The standardized communication protocol that enables the LLM to request tool execution and receive results.

### How Tools and MCP Work Together

When a tool is used in the agent framework, the process follows this flow:

1. The LLM (not your application code) decides a tool is needed to answer a query
2. The LLM sends a tool call request formatted according to the MCP standard
3. The MCP Handler in your application parses this request
4. Your application's Tool Registry locates the appropriate tool
5. **The tool executes in your application environment** (not in the LLM or MCP)
6. The tool's results are formatted as an MCP message
7. These results are sent back to the LLM via the MCP Handler
8. The LLM uses the results to generate its final response

This clarifies that tools are the actual functionality that gets executed, while MCP is just the communication protocol that enables the LLM to request tool execution and receive results.

For a more detailed explanation of this relationship, see the [MCP documentation](mcp.md).

## Built-in Tools

The framework includes several built-in tools that provide common functionality.

### Calculator Tool

The Calculator tool allows agents to evaluate mathematical expressions.

```python
from src.tools.calculator import CalculatorTool

# Create a calculator tool
calculator = CalculatorTool()

# Execute the tool
result = await calculator.execute(expression="2 * (3 + 4)")
print(result)  # Outputs: 14
```

### Web Search Tool

The Web Search tool enables agents to search the internet for information.

```python
from src.tools.web_search import WebSearchTool

# Create a web search tool
web_search = WebSearchTool()

# Execute the tool
results = await web_search.execute(query="latest AI developments 2023")
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}")
    print("---")
```

### File Operations Tool

The File Operations tool provides capabilities for reading and writing files.

```python
from src.tools.file_operations import FileOperationsTool

# Create a file operations tool
file_ops = FileOperationsTool()

# Read a file
content = await file_ops.execute(operation="read", path="data/example.txt")
print(content)

# Write to a file
await file_ops.execute(
    operation="write",
    path="data/output.txt",
    content="This is some example text."
)

# List files in a directory
files = await file_ops.execute(operation="list", path="data/")
print(files)
```

## Creating Custom Tools

You can create custom tools by inheriting from the `BaseTool` class and implementing the required methods.

### Tool Base Class

The `BaseTool` class defines the interface that all tools must implement:

```python
from src.tools.base import BaseTool

class MyCustomTool(BaseTool):
    @property
    def name(self) -> str:
        """Return the name of the tool."""
        return "my_custom_tool"

    @property
    def description(self) -> str:
        """Return a description of what the tool does."""
        return "A description of what my custom tool does"

    @property
    def parameters(self) -> dict:
        """Return the parameters that the tool accepts."""
        return {
            "param1": {
                "type": "string",
                "description": "Description of parameter 1"
            },
            "param2": {
                "type": "integer",
                "description": "Description of parameter 2"
            }
        }

    @property
    def required_parameters(self) -> list:
        """Return a list of parameters that are required."""
        return ["param1"]

    async def execute(self, **kwargs) -> any:
        """Execute the tool with the provided parameters."""
        param1 = kwargs.get("param1")
        param2 = kwargs.get("param2", 0)  # Default value for optional parameter

        # Implement your tool logic here
        result = f"Processed {param1} with value {param2}"

        return result
```

### Example: Weather Tool

Here's an example of a custom tool that retrieves weather information:

```python
import aiohttp
from src.tools.base import BaseTool

class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Gets current weather information for a specified location"

    @property
    def parameters(self) -> dict:
        return {
            "location": {
                "type": "string",
                "description": "The city and state/country (e.g., 'New York, NY')"
            },
            "units": {
                "type": "string",
                "description": "Temperature units: 'metric' (Celsius) or 'imperial' (Fahrenheit)"
            }
        }

    @property
    def required_parameters(self) -> list:
        return ["location"]

    async def execute(self, **kwargs) -> any:
        location = kwargs.get("location")
        units = kwargs.get("units", "metric")

        api_key = "YOUR_WEATHER_API_KEY"  # In production, use environment variables
        url = f"https://api.openweathermap.org/data/2.5/weather"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={
                "q": location,
                "units": units,
                "appid": api_key
            }) as response:
                if response.status == 200:
                    data = await response.json()

                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    wind_speed = data["wind"]["speed"]

                    unit_symbol = "°C" if units == "metric" else "°F"

                    return {
                        "temperature": f"{temp}{unit_symbol}",
                        "description": description,
                        "humidity": f"{humidity}%",
                        "wind_speed": wind_speed
                    }
                else:
                    error_data = await response.json()
                    return f"Error: {error_data.get('message', 'Unknown error')}"
```

### Example: Database Query Tool

Here's a tool that allows agents to run SQL queries against a database:

```python
import asyncpg
from src.tools.base import BaseTool

class DatabaseQueryTool(BaseTool):
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self._conn_pool = None

    async def _get_connection_pool(self):
        if self._conn_pool is None:
            self._conn_pool = await asyncpg.create_pool(self.connection_string)
        return self._conn_pool

    @property
    def name(self) -> str:
        return "database_query"

    @property
    def description(self) -> str:
        return "Runs SQL queries against a database and returns the results"

    @property
    def parameters(self) -> dict:
        return {
            "query": {
                "type": "string",
                "description": "The SQL query to execute"
            },
            "max_rows": {
                "type": "integer",
                "description": "Maximum number of rows to return"
            }
        }

    @property
    def required_parameters(self) -> list:
        return ["query"]

    async def execute(self, **kwargs) -> any:
        query = kwargs.get("query")
        max_rows = kwargs.get("max_rows", 100)

        # Basic SQL injection protection
        if any(keyword in query.lower() for keyword in ["insert", "update", "delete", "drop"]):
            return "Error: Only SELECT queries are allowed for safety reasons"

        pool = await self._get_connection_pool()

        try:
            async with pool.acquire() as conn:
                results = await conn.fetch(query)

                # Convert to a list of dictionaries
                formatted_results = []
                for row in results[:max_rows]:
                    formatted_results.append(dict(row))

                return {
                    "rows": formatted_results,
                    "row_count": len(results),
                    "truncated": len(results) > max_rows
                }
        except Exception as e:
            return f"Error executing query: {str(e)}"
```

## Registering Tools with Agents

To make tools available to an agent, they need to be registered when creating the agent:

```python
from src.core.orchestrator import Orchestrator
from src.models import OpenAIModel
from src.memory.buffer import BufferMemory
from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool

# Create custom tools
weather_tool = WeatherTool()
db_tool = DatabaseQueryTool("postgresql://user:password@localhost:5432/mydb")

# Create an agent with tools
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    tools=[CalculatorTool(), WebSearchTool(), weather_tool, db_tool],
    system_message="You are a helpful assistant with access to tools."
)
```

## Tool Management

### Tool Registry

The framework includes a tool registry for centralized tool management:

```python
from src.tools.registry import ToolRegistry
from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool

# Create a tool registry
registry = ToolRegistry()

# Register built-in tools
registry.register(CalculatorTool())
registry.register(WebSearchTool())

# Register custom tools
registry.register(WeatherTool())
registry.register(DatabaseQueryTool("postgresql://user:password@localhost:5432/mydb"))

# Get a tool by name
calculator = registry.get_tool("calculator")

# List all available tools
all_tools = registry.list_tools()
for tool_name in all_tools:
    print(tool_name)

# Check if a tool exists
if registry.has_tool("weather"):
    print("Weather tool is available")
```

### Configuring Tools via API

Tools can be configured and registered through the API:

```bash
# Register a tool via API
curl -X POST http://localhost:5050/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather",
    "class_path": "custom_tools.weather.WeatherTool",
    "config": {
      "api_key": "YOUR_API_KEY"
    }
  }'

# List available tools
curl -X GET http://localhost:5050/tools

# Get tool information
curl -X GET http://localhost:5050/tools/weather

# Update tool configuration
curl -X PATCH http://localhost:5050/tools/weather \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "api_key": "NEW_API_KEY"
    }
  }'
```

## Advanced Tool Features

### Tool Pipelines

You can create tool pipelines that chain multiple tools together:

```python
from src.tools.pipeline import ToolPipeline

# Create a pipeline of tools
pipeline = ToolPipeline([
    ("web_search", WebSearchTool()),
    ("summarize", TextSummarizationTool())
])

# Execute the pipeline
result = await pipeline.execute(
    web_search={"query": "latest developments in AI 2023"},
    summarize={"text": lambda outputs: "\n".join([r["snippet"] for r in outputs["web_search"]]),
               "max_length": 200}
)
print(result["summarize"])  # Final output from the pipeline
```

### Tool Authorization

Implement authorization for sensitive tools:

```python
from src.tools.base import BaseTool
from src.auth import check_user_permission

class SecureFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "secure_file"

    @property
    def description(self) -> str:
        return "Securely reads or writes files with permission checks"

    @property
    def parameters(self) -> dict:
        return {
            "operation": {
                "type": "string",
                "description": "The operation to perform (read/write)"
            },
            "path": {
                "type": "string",
                "description": "Path to the file"
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write operations)"
            },
            "user_id": {
                "type": "string",
                "description": "ID of the user making the request"
            }
        }

    @property
    def required_parameters(self) -> list:
        return ["operation", "path", "user_id"]

    async def execute(self, **kwargs) -> any:
        operation = kwargs.get("operation")
        path = kwargs.get("path")
        user_id = kwargs.get("user_id")

        # Check permissions
        has_permission = await check_user_permission(user_id, operation, path)
        if not has_permission:
            return "Error: Permission denied"

        # Proceed with operation
        if operation == "read":
            # Read file logic
            pass
        elif operation == "write":
            content = kwargs.get("content", "")
            # Write file logic
            pass
        else:
            return "Error: Invalid operation"
```

### Tool Error Handling

Implement robust error handling in your tools:

```python
from src.tools.base import BaseTool

class RobustTool(BaseTool):
    # ... other properties ...

    async def execute(self, **kwargs) -> any:
        try:
            # Main tool logic
            param = kwargs.get("param")
            if param is None:
                return {"error": "Missing required parameter", "error_code": "MISSING_PARAM"}

            # Business logic
            result = await self._process(param)
            return {"success": True, "result": result}

        except ConnectionError as e:
            # Handle connection issues
            return {
                "error": "Connection error",
                "error_code": "CONNECTION_ERROR",
                "details": str(e)
            }
        except TimeoutError as e:
            # Handle timeouts
            return {
                "error": "Operation timed out",
                "error_code": "TIMEOUT",
                "details": str(e)
            }
        except Exception as e:
            # Catch-all for unexpected errors
            return {
                "error": "An unexpected error occurred",
                "error_code": "UNKNOWN_ERROR",
                "details": str(e)
            }
```

## Best Practices

1. **Clear Documentation**: Provide clear descriptions and parameter documentation for each tool

2. **Input Validation**: Validate all inputs before processing to prevent errors and security issues

3. **Error Handling**: Implement robust error handling and provide meaningful error messages

4. **Statelessness**: Design tools to be stateless whenever possible to simplify scaling

5. **Security First**: Implement appropriate security checks for tools that access sensitive data

6. **Performance**: Keep tool execution efficient, especially for synchronous operations

7. **Testing**: Thoroughly test tools with various inputs to ensure reliability

## Troubleshooting

### Tool Not Being Found

- Check that the tool is correctly registered with the agent
- Verify that the tool name is consistent across registration and references

### Parameter Errors

- Ensure that all required parameters are being provided
- Check parameter types and formats match the tool's expectations

### Execution Failures

- Implement detailed logging in tool execution
- Check for connectivity issues with external services
- Verify that any required API keys or credentials are valid

## Next Steps

After implementing tools, you might want to explore:

- Creating [agents](./agent.md) that can effectively use your tools
- Setting up [memory systems](./memory.md) to retain information across tool executions
- Implementing [WebSocket support](./websocket.md) for real-time tool execution updates
- Exploring [orchestrator features](./orchestrator.md) for coordinating multiple tools and agents
