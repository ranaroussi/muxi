# MUXI Framework

A framework for creating AI agents with memory, tools, and orchestration.

## Installation

```bash
pip install muxi
```

This installs the complete MUXI system (excluding web interface):
- Core functionality
- Server implementation
- Command-line interface

For headless servers, this is the recommended installation.

## Client-Only Installation

If you only need clients to connect to existing MUXI servers:

```bash
# Command-line client only
pip install muxi-cli

# Web interface only
pip install muxi-web
```

## Usage

```python
from muxi import muxi

# Create a new MUXI instance
app = muxi()

# Add an agent from a configuration file
app.add_agent("my_assistant", "configs/assistant.yaml")

# Chat with a specific agent
response = app.chat("Hello, who are you?", agent_name="my_assistant")
print(response)

# Start the server mode
app.run()
```

## License

MIT
