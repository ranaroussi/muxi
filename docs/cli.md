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
python -m src.cli chat     # Before installation
muxi chat                  # After installation

# Start a chat with a specific agent
python -m src.cli chat --agent-id researcher  # Before installation
muxi chat --agent-id researcher               # After installation

# Run the API server on a specific port
python -m src.cli api --port 8000  # Before installation
muxi api --port 8000               # After installation

# Run both API server and web UI
python -m src.cli run  # Before installation
muxi run               # After installation

# Send a message to an agent (non-interactive)
python -m src.cli send my_agent "What is the weather today?"  # Before installation
muxi send my_agent "What is the weather today?"               # After installation

# Send a message to a multi-user agent
python -m src.cli send multi_user_agent --user-id 123 "Remember my preferences"  # Before installation
muxi send multi_user_agent --user-id 123 "Remember my preferences"               # After installation
```

## Command-Line Arguments

Each command supports different options:

### Global Options
| Option | Description |
|--------|-------------|
| `--help` | Show help for a command |
| `--version` | Show the version and exit |

### Chat Command
| Option | Description |
|--------|-------------|
| `--agent-id AGENT_ID` | Specify the ID for the agent (default: "cli_agent") |
| `--no-config` | Don't use configuration file, use defaults instead |

### API Command
| Option | Description |
|--------|-------------|
| `--host HOST` | Host to bind the API server to (default: "0.0.0.0") |
| `--port PORT` | Port to bind the API server to (default: 5050) |
| `--reload` | Enable auto-reload for development |

### Send Command
| Option | Description |
|--------|-------------|
| `--user-id USER_ID` | User ID for multi-user agents |

## Interactive Chat Commands

Once in the interactive chat mode, you can use the following commands:

| Command | Description |
|---------|-------------|
| `/exit`, `/quit`, `/bye` | Exit the chat |
| `/help` | Show help message |
| `/clear` | Clear the screen |
| `/memory <query>` | Search the agent's memory |
| `/tools` | List available tools |

## Configuration

The CLI uses the AI Agent Framework's configuration system. It loads settings from:

1. Environment variables (from `.env` file)
2. Default values defined in the configuration classes

### Key Environment Variables

Create a `.env` file in the project root with the following variables:

```
# LLM API Keys (required)
OPENAI_API_KEY=your_openai_api_key_here

# Agent Settings
DEFAULT_AGENT_ID=cli_agent
SYSTEM_MESSAGE=You are a helpful AI assistant...

# Memory Configuration
BUFFER_MAX_SIZE=1000
VECTOR_DIMENSION=1536

# Tool Configuration
SERPER_API_KEY=your_serper_api_key_here  # For web search
```

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
