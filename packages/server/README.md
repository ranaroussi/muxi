# MUXI Server

Server implementation of the MUXI Framework.

## Installation

```bash
pip install muxi-server
```

## Usage

```python
from muxi import muxi

# Create a new MUXI instance
app = muxi()

# Start the server
app.run(host="0.0.0.0", port=5050)
```

Or run directly as a module:

```bash
python -m muxi.server
```

## Features

- Complete server implementation
- Agent management
- Memory systems
- LLM integrations
- API and WebSocket server

## License

MIT
