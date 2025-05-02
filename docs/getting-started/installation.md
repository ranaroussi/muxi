---
title: Installation
nav_order: 1
parent: Getting Started
---

# Installation

The MUXI Framework can be installed through pip:

```bash
pip install muxi
```

For the latest development version:

```bash
pip install git+https://github.com/microsoft/muxi.git
```

## Dependencies

MUXI requires:

- Python 3.8+
- An LLM provider (OpenAI, Azure OpenAI, Anthropic, etc.)
- API keys for the chosen providers

## Development Setup

To set up a development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/microsoft/muxi.git
   cd muxi
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up environment variables:
   ```bash
   # For OpenAI
   export OPENAI_API_KEY=your_api_key

   # For Azure OpenAI
   export AZURE_OPENAI_API_KEY=your_api_key
   export AZURE_OPENAI_ENDPOINT=your_endpoint
   ```

## Configuration

Create a basic configuration file for your application:

```yaml
# configs/muxi_config.yaml
orchestrator:
  memory:
    buffer_size: 10
    buffer_multiplier: 10
    long_term:
      type: "sqlite"
      connection_string: "memory.db"

agents:
  - name: "assistant"
    model:
      type: "openai"
      model_name: "gpt-4"
      temperature: 0.7
    instructions: "You are a helpful assistant."
```

## Running Tests

To run the test suite:

```bash
pytest
```

## Next Steps

After installation, proceed to the [Quick Start Guide](../intro/quick-start.md) to create your first agent application.
