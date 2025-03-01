# Command Line Interface (CLI)

The AI Agent Framework includes a powerful command-line interface (CLI) that allows you to interact with AI agents directly from your terminal. This document covers how to set up and use the CLI effectively.

## Overview

The CLI provides a rich terminal-based interface for:
- Creating and interacting with agents
- Managing API server and web UI
- Sending one-off messages to agents
- Viewing rich-formatted responses with markdown support

## Installation

The CLI is included with the AI Agent Framework. You can use it in two ways:

### As a module (before package installation)
```bash
# From the project root directory
python -m src.cli
```

### As a standalone command (after package installation)
```bash
# After installing the package from PyPI
muxi
```

## Command Structure

The CLI follows a command-based structure:

```bash
muxi [COMMAND] [OPTIONS] [ARGUMENTS]
```

Available commands:
- `chat`: Start an interactive chat session with an agent
- `api`: Run the API server
- `run`: Run both the API server and web UI
- `send`: Send a one-off message to an agent

### Examples

```bash
# Show help
python -m src.cli --help   # Before installation
muxi --help                # After installation

# Start a chat with the default agent
python -m src.cli chat
muxi chat

# Start a chat with a specific agent
python -m src.cli chat --agent-id researcher
muxi chat --agent-id researcher

# Send a one-off message to an agent
python -m src.cli send --agent-id assistant "What is the capital of France?"
muxi send --agent-id assistant "What is the capital of France?"

# Run the API server
python -m src.cli api
muxi api

# Run both the API server and web UI
python -m src.cli run
muxi run

# Alternatively, you can run both the API server and web UI with:
python -m src
```

## Chat Mode

The chat mode provides an interactive terminal-based chat interface with the selected agent. It supports:

- Markdown rendering in responses
- Syntax highlighting for code
- Rich text formatting
- Message history during the session
- Tool execution visualization

### Starting a Chat Session

```bash
python -m src.cli chat [OPTIONS]
```

Options:
- `--agent-id TEXT`: ID of the agent to chat with (default: "assistant")
- `--user-id TEXT`: User ID for multi-user agents (default: None)
- `--help`: Show this message and exit.

### Interactive Commands

During a chat session, you can use special commands:

- `/help`: Show available commands
- `/exit` or `/quit`: Exit the chat session
- `/clear`: Clear the chat history
- `/system <message>`: Update the agent's system message
- `/memory`: Show the current memory contents

Example:
```
You: What is the capital of France?
Assistant: The capital of France is Paris.

You: /system You are a helpful assistant who speaks like a pirate.
System message updated.

You: What is the capital of France?
Assistant: Arr, matey! The capital of France be Paris, ye landlubber!
```

## Send Mode

The send mode allows you to send a single message to an agent and get the response without starting an interactive session.

```bash
python -m src.cli send [OPTIONS] MESSAGE
```

Options:
- `--agent-id TEXT`: ID of the agent to chat with (default: "assistant")
- `--user-id TEXT`: User ID for multi-user agents (default: None)
- `--help`: Show this message and exit.

Example:
```bash
python -m src.cli send "What is the capital of France?"
```

## API Server Mode

The API server mode starts the REST API server, which provides endpoints for interacting with agents.

```bash
python -m src.cli api [OPTIONS]
```

Options:
- `--host TEXT`: Host to bind to (default: "0.0.0.0")
- `--port INTEGER`: Port to run on (default: 5050)
- `--help`: Show this message and exit.

Example:
```bash
python -m src.cli api --host 127.0.0.1 --port 8080
```

## Run Mode

The run mode starts both the API server and the web UI.

```bash
python -m src.cli run [OPTIONS]
```

Options:
- `--api-host TEXT`: Host for the API server (default: "0.0.0.0")
- `--api-port INTEGER`: Port for the API server (default: 5050)
- `--help`: Show this message and exit.

Example:
```bash
python -m src.cli run --api-port 8080
```

## Configuration

The CLI uses the same configuration as the rest of the framework. You can configure it using:

1. Environment variables
2. `.env` file in the project root
3. Configuration files in the `src/config` directory

Key configuration options that affect the CLI:

```env
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7

# Tools Configuration
ENABLE_WEB_SEARCH=true
ENABLE_CALCULATOR=true
```

## Advanced Usage

### Creating Custom Agents

You can create custom agents with specific capabilities by modifying the configuration files or by using the API server.

Example using the API to create a custom agent:
```bash
# Start the API server
python -m src.cli api

# In another terminal, create a custom agent
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "custom_agent",
    "system_message": "You are a helpful AI assistant specialized in Python programming."
  }'

# Now chat with the custom agent
python -m src.cli chat --agent-id custom_agent
```

### Using Multi-User Agents

For agents that support multiple users, you can specify the user ID:

```bash
python -m src.cli chat --agent-id multi_user_assistant --user-id 123
```

This ensures that the agent maintains separate memory contexts for different users.

## Troubleshooting

### Common Issues

1. **Port already in use**: If you get an error about port 5050 being already in use, you can specify a different port:
   ```bash
   python -m src.cli api --port 5051
   ```

2. **API key not found**: Ensure you've set up your API keys in the `.env` file or as environment variables.

3. **Rich text rendering issues**: Some terminals may not support all rich text features. You can try updating your terminal or using a different one.

### Debug Mode

You can enable debug logging to get more information about what's happening:

```bash
# Set environment variable
export DEBUG=1

# Run CLI
python -m src.cli chat
```

## Integration with Scripts

You can use the CLI programmatically in your Python scripts:

```python
from src.cli import run_cli, chat_with_agent

# Run CLI directly
run_cli()

# Or use specific functions
response = chat_with_agent("assistant", "Hello, how are you?")
print(response)
```

This allows you to build custom workflows that leverage the CLI's functionality.

## Implementation Details

The CLI is implemented using the Click library and provides the following features:

1. **Rich Text Interface**: Uses the `rich` library for formatted terminal output
2. **Memory Access**: Allows searching the agent's memory using natural language
3. **Tool Integration**: Access to configured tools like web search and calculator
4. **Configuration Loading**: Automatic loading from environment variables
5. **Async Communication**: Uses async/await for non-blocking agent interactions

## Example Session

Here's an example of a CLI session:

```
# AI Agent Framework CLI

You are now chatting with an AI agent (cli_agent).
Type `/help` for available commands or `/exit` to quit.

Available Tools
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name         ┃ Description                                         ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ web_search   │ Search the web for information                      │
│ calculator   │ Perform mathematical calculations                   │
└──────────────┴─────────────────────────────────────────────────────┘

You: Tell me about the AI Agent Framework

Agent:
The AI Agent Framework is a powerful, extensible system for building AI agents with memory, tools, and real-time communication capabilities. Here are the key features:

- **Multi-Agent Orchestration**: Create and manage multiple AI agents with different capabilities
- **Memory Systems**: Short-term buffer memory and long-term persistent memory
- **Tool Integration**: Extensible tool system with built-in utilities like web search and calculator
- **Real-Time Communication**: WebSocket support for instant messaging
- **REST API**: Comprehensive API for managing agents and conversations

The framework is designed to be modular and easy to extend, allowing developers to build sophisticated AI applications.

You: /tools

Available Tools
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name         ┃ Description                                         ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ web_search   │ Search the web for information                      │
│ calculator   │ Perform mathematical calculations                   │
└──────────────┴─────────────────────────────────────────────────────┘

You: /exit

Goodbye!
```

## Advanced Usage

### Modifying System Message

The system message defines the agent's persona and capabilities. You can customize it:

1. Via environment variable:
   ```
   SYSTEM_MESSAGE="You are an expert programmer specializing in Python..."
   ```

2. Via the configuration file:
   ```python
   # src/config/app.py
   system_message = "You are an expert programmer..."
   ```

### Adding Custom Tools

To add custom tools to the CLI agent, modify the `create_agent_from_config` function in `src/cli/app.py`:

```python
# Create tools
tools = []

# Load tools based on configuration
if config.tools.enable_calculator:
    tools.append(Calculator())

if config.tools.enable_web_search:
    tools.append(WebSearch())

# Add your custom tool
if config.tools.enable_custom_tool:
    tools.append(CustomTool())
```

## Troubleshooting

### LLM API Key Issues

If you encounter errors related to the LLM API key, make sure:
- You have set the correct API key in your `.env` file
- The API key has sufficient permissions and credits

### Memory Errors

If memory search doesn't work properly:
- Ensure you have a proper embedding dimension set up
- Check that you have enough previous messages for context

### Tool Execution Errors

If tools don't work correctly:
- Check if the tool's API key is properly set (if required)
- Verify the tool's dependencies are installed
