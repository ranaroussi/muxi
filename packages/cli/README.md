# MUXI CLI

Command-line client interface for the MUXI Framework. This package provides a standalone CLI client for connecting to MUXI servers.

## Installation

```bash
pip install muxi-cli
```

This will install only the CLI client components, not the full MUXI server.

## Usage

```bash
# List available agents
muxi list agents

# Chat with an agent
muxi chat --agent my_assistant

# Connect to a remote server
muxi connect --url http://server-ip:5050 --key your_api_key
```

## Features

- Command-line interface
- Remote server connections
- Minimal dependencies
- Interactive mode

## Connecting to Servers

The CLI can connect to:
- Local MUXI servers
- Remote MUXI servers via API key authentication

## License

MIT
