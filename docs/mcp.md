---
layout: default
title: MCPs
parent: Core Concepts
has_children: false
nav_order: 8
permalink: /mcp/
---
# Model Context Protocol (MCP)

The Model Context Protocol (MCP) is a standardized format for communication between applications and Large Language Models. It provides a structured way to send prompts, receive responses, and process tool calls.

## What is MCP?

MCP is a protocol that:

- Standardizes the format of messages sent to and received from language models
- Enables structured tool calling by language models
- Provides a consistent interface across different language model providers
- Improves the control and predictability of language model interactions
- Facilitates advanced features like parallel tool execution and multi-step reasoning

## MCP vs Tools: Understanding the Distinction

One common source of confusion is the relationship between MCP and tools. Let's clarify this important distinction:

### MCP is a Communication Protocol, Not the Tools

- **MCP (Model Context Protocol)**: A standardized message format and communication protocol for interacting with language models. It's the "language" your application uses to talk to models like GPT-4 or Claude.

- **Tools**: Specific capabilities that extend what your agent can do (like web search, calculations, database queries, etc.). Each tool has its own functionality that executes in your application environment.

### Tool Execution Flow

The complete flow of tool usage looks like this:

1. User sends a query to your agent
2. The agent passes this query to the language model via the MCP Handler
3. The language model determines a tool is needed and responds with a tool call request (in MCP format)
4. The MCP Handler parses this response and recognizes the tool call
5. **The framework (not the language model, not the MCP) passes the request to the appropriate tool**
6. **The tool executes in your application environment with access to your system resources**
7. The tool returns results to your framework
8. Results are formatted as an MCP message and sent back to the language model
9. The language model incorporates these results into its final response

```
┌───────────┐    Query     ┌──────────────┐     MCP format     ┌─────┐
│   User    ├─────────────►│ Agent/       ├───────────────────►│     │
└───────────┘              │ Orchestrator │                    │     │
                           └──────┬───────┘                    │     │
                                  │                            │     │
                                  │                            │ LLM │
                        ┌─────────▼────────┐                  │     │
┌─────────────┐         │                  │   Tool request   │     │
│ Application │         │   MCP Handler    │◄─────────────────┤     │
│ Environment │         │                  │                  └─────┘
│             │         └─────────┬────────┘
│    ┌────────▼─────┐             │
│    │              │    Tool     │
│    │     Tool     │◄────request─┘
│    │   Execution  │
│    │              │
│    └──────┬───────┘
│           │
│    Tool   │
│    result │
│           │
└───────────▼───────┐
               MCP  │
              format│
                    ▼
                 Results
                 to LLM
```

### Key Points to Remember

- **MCP is the messenger**: It formats messages between your application and the language model
- **Language model makes the decision**: The language model (not your code) decides when a tool is needed
- **Your framework executes tools**: Tools run in your application's environment, not inside the language model
- **MCP formats tool results**: The results are sent back to the language model through the MCP format

This clarifies that MCP is not the tools themselves—it's just the standardized way to communicate about tools with the language model.

## Message Structure

The `MCPMessage` class is the core data structure used for communication in the MCP system. It represents a message in a conversation, with attributes for the sender role, content, and additional metadata.

### Key Attributes

A proper MCPMessage contains the following key attributes:

- `role`: The role of the sender (e.g., "user", "assistant", "system", "function")
- `content`: The actual content of the message
- `name`: Optional name for function messages
- `context`: Optional context information

This structure ensures compatibility with various LLM providers like OpenAI, Anthropic, and others.

### Example Usage

```python
from src.core.mcp import MCPMessage

# Create a user message
user_msg = MCPMessage(
    role="user",
    content="What's the weather like in New York?"
)

# Create an assistant response
assistant_msg = MCPMessage(
    role="assistant",
    content="The weather in New York is currently sunny with a temperature of 72°F."
)

# Create a function message
function_msg = MCPMessage(
    role="function",
    content="The current temperature is 72°F with clear skies.",
    name="get_weather",
    metadata={"location": "New York", "unit": "fahrenheit"}
)
```

### Internal Processing

When messages are processed, they are converted to a format suitable for the language model:

```python
def _context_to_model_messages(context):
    """
    Convert MCPContext to a list of messages for the language model.

    This method processes each message in the context and extracts the
    appropriate attributes (role, content, name, etc.) to create a
    properly formatted message for the LLM.
    """
    model_messages = []

    for message in context.messages:
        # Create the base message with required attributes
        model_message = {
            "role": message.role,
            "content": message.content
        }

        # Add optional attributes if present
        if hasattr(message, "name") and message.name:
            model_message["name"] = message.name

        if hasattr(message, "context") and message.context:
            model_message["context"] = message.context

        model_messages.append(model_message)

    return model_messages
```

This ensures that messages maintain proper structure throughout the system.

## MCP Message Structure

The core of MCP is the message structure:

```python
class MCPMessage:
    def __init__(self, role, content=None, tool_calls=None, tool_call_id=None):
        self.role = role  # "user", "assistant", "system", or "tool"
        self.content = content  # Text content of the message
        self.tool_calls = tool_calls or []  # List of tool calls made by the assistant
        self.tool_call_id = tool_call_id  # ID of the tool call this message responds to
```

### Message Roles

MCP supports several message roles:

- **user**: Messages from the user to the language model
- **assistant**: Responses from the language model
- **system**: System instructions that guide the language model's behavior
- **tool**: Results returned from tool executions

### Tool Calls

Tool calls are structured as:

```python
class MCPToolCall:
    def __init__(self, tool_name, tool_id, tool_args):
        self.tool_name = tool_name  # Name of the tool to call
        self.tool_id = tool_id  # Unique identifier for this tool call
        self.tool_args = tool_args  # Arguments for the tool, as a dictionary
```

## Using MCP in the Framework

### Basic Message Exchange

```python
from src.mcp.message import MCPMessage
from src.models.openai import OpenAIModel

# Create messages
system_message = MCPMessage(role="system", content="You are a helpful assistant.")
user_message = MCPMessage(role="user", content="What's the weather in London?")

# Prepare messages for language model
messages = [system_message, user_message]

# Send to language model
model = OpenAIModel(model="gpt-4o")
response = await model.generate(messages)

# Process response
if isinstance(response, MCPMessage):
    if response.content:
        print(f"Assistant: {response.content}")

    # Handle any tool calls
    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"Tool Call: {tool_call.tool_name} with args {tool_call.tool_args}")
```

### Tool Calling Flow

The complete flow of a tool-enabled conversation:

```python
from src.mcp.message import MCPMessage, MCPToolCall
from src.models.openai import OpenAIModel
from src.tools.registry import ToolRegistry
from src.tools.weather import WeatherTool

# Set up language model and tools
model = OpenAIModel(model="gpt-4o")
registry = ToolRegistry()
registry.register(WeatherTool())

# Create initial messages
messages = [
    MCPMessage(role="system", content="You are a helpful assistant with access to tools."),
    MCPMessage(role="user", content="What's the weather in London?")
]

# Send to language model
response = await model.generate(messages)
messages.append(response)

# Process tool calls
if response.tool_calls:
    for tool_call in response.tool_calls:
        # Get the tool
        tool = registry.get_tool(tool_call.tool_name)
        if tool:
            # Execute the tool
            tool_result = await tool.execute(**tool_call.tool_args)

            # Create tool response message
            tool_message = MCPMessage(
                role="tool",
                content=str(tool_result),
                tool_call_id=tool_call.tool_id
            )

            # Add tool response to messages
            messages.append(tool_message)

    # Get final response from language model
    final_response = await model.generate(messages)
    messages.append(final_response)
    print(f"Assistant: {final_response.content}")
```

## MCP Handler

The framework provides an MCP handler to abstract the message processing:

```python
from src.mcp.handler import MCPHandler
from src.models.openai import OpenAIModel
from src.tools.registry import ToolRegistry
from src.tools.weather import WeatherTool

async def chat_with_tools():
    # Set up language model, tools, and handler
    model = OpenAIModel(model="gpt-4o")

    registry = ToolRegistry()
    registry.register(WeatherTool())

    handler = MCPHandler(model=model, tool_registry=registry)

    # Set system message
    handler.set_system_message("You are a helpful assistant with access to tools.")

    # Process a user message
    response = await handler.process_message("What's the weather in London?")
    print(f"Assistant: {response}")

    # Continue the conversation
    response = await handler.process_message("How about Paris?")
    print(f"Assistant: {response}")

# Run the chat
await chat_with_tools()
```

## Creating Custom MCP Servers

The MUXI framework provides a convenient utility for creating custom MCP servers through a CLI wizard:

```bash
# Generate a new MCP server with an interactive wizard
muxi create mcp-server

# Specify output directory and optional name
muxi create mcp-server --output-dir ./my_servers --name MyCustomMCP
```

The wizard guides you through:
1. Naming your MCP server
2. Providing a description
3. Adding custom tools with descriptions
4. Generating all necessary boilerplate code

### Generated Project Structure

The generator creates a complete MCP server project with the following structure:

```
my_custom_mcp/
├── __init__.py
├── my_custom_mcp_server.py
├── README.md
├── setup.py
├── tools/
│   ├── __init__.py
│   └── tool1.py
├── tests/
│   └── __init__.py
└── examples/
    └── example_client.py
```

This structure includes:
- A properly configured MCP server implementation
- Tool class templates
- Installation setup
- README documentation
- Example client code

### Using the Generated MCP Server

Once generated, you can install and run your custom MCP server:

```bash
# Install in development mode
cd my_custom_mcp
pip install -e .

# Run the server
python -m my_custom_mcp.my_custom_mcp_server
```

The server will be available at `http://localhost:5001` by default.

## Language Model Providers

The MCP standardizes interactions across different language model providers:

### OpenAI Implementation

```python
from src.mcp.message import MCPMessage
from src.models.openai import OpenAIModel

# Create an OpenAI language model
model = OpenAIModel(model="gpt-4o")

# Process MCP messages
messages = [
    MCPMessage(role="system", content="You are a helpful assistant."),
    MCPMessage(role="user", content="Who won the 2022 World Cup?")
]

response = await model.generate(messages)
print(response.content)
```

### Anthropic Implementation

```python
from src.mcp.message import MCPMessage
from src.models.anthropic import AnthropicModel

# Create an Anthropic language model
model = AnthropicModel(model="claude-3-opus")

# Process MCP messages (same format as OpenAI)
messages = [
    MCPMessage(role="system", content="You are a helpful assistant."),
    MCPMessage(role="user", content="Who won the 2022 World Cup?")
]

response = await model.generate(messages)
print(response.content)
```

## Advanced MCP Features

### Parallel Tool Execution

MCP allows for parallel execution of multiple tool calls:

```python
from src.mcp.handler import MCPHandler, execute_tool_calls_parallel

async def process_with_parallel_tools(handler, user_message):
    # Get response from language model
    response = await handler.model.generate([
        MCPMessage(role="system", content=handler.system_message),
        MCPMessage(role="user", content=user_message)
    ])

    if response.tool_calls:
        # Execute all tool calls in parallel
        tool_results = await execute_tool_calls_parallel(
            response.tool_calls,
            handler.tool_registry
        )

        # Add all tool results to the conversation
        tool_messages = []
        for tool_call_id, result in tool_results.items():
            tool_messages.append(MCPMessage(
                role="tool",
                content=str(result),
                tool_call_id=tool_call_id
            ))

        # Get final response with tool results
        messages = [
            MCPMessage(role="system", content=handler.system_message),
            MCPMessage(role="user", content=user_message),
            response,  # The assistant's response with tool calls
            *tool_messages  # All tool results
        ]

        final_response = await handler.model.generate(messages)
        return final_response.content

    return response.content
```

### Multi-Model Chain

You can chain different language models together using MCP as a common interface:

```python
from src.mcp.message import MCPMessage
from src.models.openai import OpenAIModel
from src.models.anthropic import AnthropicModel

async def multi_model_processing(query):
    # First model generates a detailed plan
    planning_model = OpenAIModel(model="gpt-4o")
    plan_messages = [
        MCPMessage(role="system", content="You are a planning assistant. Create a detailed plan."),
        MCPMessage(role="user", content=f"Create a research plan for: {query}")
    ]
    plan_response = await planning_model.generate(plan_messages)

    # Second model executes the plan
    execution_model = AnthropicModel(model="claude-3-opus")
    execution_messages = [
        MCPMessage(role="system", content="You are a research assistant. Execute the given plan."),
        MCPMessage(role="user", content=f"Execute this research plan:\n\n{plan_response.content}")
    ]
    execution_response = await execution_model.generate(execution_messages)

    # Third model summarizes the results
    summary_model = OpenAIModel(model="gpt-3.5-turbo")
    summary_messages = [
        MCPMessage(role="system", content="You are a summarization assistant. Create concise summaries."),
        MCPMessage(role="user", content=f"Summarize these research results:\n\n{execution_response.content}")
    ]
    summary_response = await summary_model.generate(summary_messages)

    return {
        "plan": plan_response.content,
        "execution": execution_response.content,
        "summary": summary_response.content
    }
```

## Custom MCP Extensions

You can extend the MCP format for custom needs:

```python
from src.mcp.message import MCPMessage

class ExtendedMCPMessage(MCPMessage):
    def __init__(self, role, content=None, tool_calls=None, tool_call_id=None, metadata=None):
        super().__init__(role, content, tool_calls, tool_call_id)
        self.metadata = metadata or {}  # Additional metadata for the message

# Example usage
message = ExtendedMCPMessage(
    role="user",
    content="What's the weather in London?",
    metadata={
        "timestamp": "2023-06-15T14:30:00Z",
        "user_id": "user_123",
        "session_id": "session_456",
        "client_info": {
            "device": "mobile",
            "browser": "chrome",
            "language": "en-US"
        }
    }
)
```

## MCP Message Serialization

For storing or transmitting MCP messages, you can serialize them:

```python
import json
from src.mcp.message import MCPMessage, MCPToolCall

def serialize_mcp_message(message):
    """Serialize an MCP message to a dictionary."""
    data = {
        "role": message.role,
        "content": message.content,
    }

    if message.tool_calls:
        data["tool_calls"] = [
            {
                "tool_name": tc.tool_name,
                "tool_id": tc.tool_id,
                "tool_args": tc.tool_args
            } for tc in message.tool_calls
        ]

    if message.tool_call_id:
        data["tool_call_id"] = message.tool_call_id

    return data

def deserialize_mcp_message(data):
    """Deserialize a dictionary to an MCP message."""
    tool_calls = None
    if "tool_calls" in data:
        tool_calls = [
            MCPToolCall(
                tool_name=tc["tool_name"],
                tool_id=tc["tool_id"],
                tool_args=tc["tool_args"]
            ) for tc in data["tool_calls"]
        ]

    return MCPMessage(
        role=data["role"],
        content=data.get("content"),
        tool_calls=tool_calls,
        tool_call_id=data.get("tool_call_id")
    )

# Example usage
message = MCPMessage(
    role="assistant",
    content="I'll check the weather for you.",
    tool_calls=[
        MCPToolCall(
            tool_name="weather",
            tool_id="call_123",
            tool_args={"location": "London"}
        )
    ]
)

# Serialize to JSON
serialized = json.dumps(serialize_mcp_message(message))

# Deserialize from JSON
deserialized_data = json.loads(serialized)
restored_message = deserialize_mcp_message(deserialized_data)
```

## Websocket Integration

MCP messages can be transmitted via WebSockets for real-time communication:

```python
# Server-side
from src.mcp.handler import MCPHandler
from src.mcp.message import MCPMessage
import json

async def handle_websocket(websocket, path):
    # Set up MCP handler
    handler = MCPHandler(model=model, tool_registry=registry)
    handler.set_system_message("You are a helpful assistant.")

    async for message in websocket:
        # Parse incoming message
        data = json.loads(message)

        if data["type"] == "chat":
            # Process the user message through MCP
            user_message = data["message"]

            # Add to conversation history
            handler.add_message(MCPMessage(role="user", content=user_message))

            # Process the message and get response
            response = await handler.process_current_messages()

            # Send response back
            await websocket.send(json.dumps({
                "type": "response",
                "message": response.content,
                "has_tool_calls": bool(response.tool_calls)
            }))

            # If there are tool calls, send their results
            if response.tool_calls:
                for tool_result in handler.last_tool_results:
                    await websocket.send(json.dumps({
                        "type": "tool_result",
                        "tool_name": tool_result["tool_name"],
                        "result": tool_result["result"]
                    }))
```

## Best Practices

1. **Consistent Message Format**: Always use the MCPMessage class for consistency

2. **Tool Result Handling**: Properly format tool results as MCPMessages with the "tool" role

3. **System Messages**: Use descriptive system messages to guide language model behavior

4. **Error Handling**: Implement robust error handling for tool calls

5. **Message History Management**: Keep message history manageable to avoid token limits

6. **Validation**: Validate incoming messages to ensure they conform to MCP structure

## Troubleshooting

### Tool Call Format Issues

- Ensure tool calls are correctly formatted with proper tool names and arguments
- Check that the tool implementation matches the expected parameter structure

### Message Handling Errors

- Verify that message roles are one of: "user", "assistant", "system", or "tool"
- Ensure that tool response messages include the correct tool_call_id

### Language Model Compatibility

- Different language models may have varying support for tool calling
- Check documentation for provider-specific limitations

## Next Steps

After understanding MCP, you might want to explore:

- Creating [agents](./agent) that leverage MCP for structured communication
- Implementing custom [tools](./tools) that integrate with the MCP format
- Setting up [WebSocket connections](./websocket) for real-time MCP communication
- Understanding [memory systems](./memory) and how they store MCP messages
