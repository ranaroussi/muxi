---
layout: default
title: Testing Guide
parent: Contributing
has_children: false
nav_order: 3
permalink: /testing/
---

# Testing Guide

This guide covers the testing approach for the MUXI Framework, including automated tests, utilities for test environment setup, and best practices.

## Test Structure

The MUXI Framework uses Python's built-in `unittest` framework along with `pytest` for testing. Tests are organized by component and functionality:

- `tests/test_agent.py` - Tests for the Agent class
- `tests/test_memory.py` - Tests for memory systems
- `tests/test_mcp.py` - Tests for the Model Context Protocol
- `tests/test_orchestrator.py` - Tests for the Orchestrator
- `tests/test_tools.py` - Tests for the Tool system
- `tests/test_intelligent_routing.py` - Tests for agent routing

## Environment Setup for Tests

When running tests, particularly those involving LLM providers like OpenAI, you need to properly set up environment variables. The framework includes a utility to streamline this process:

### Using the Environment Setup Utility

The `env_setup.py` utility is designed to ensure consistent environment variable loading across all tests:

```python
from tests.utils.env_setup import load_api_keys

# At the beginning of your test
load_api_keys()
```

This utility:

1. Loads environment variables from the `.env` file with `override=True`
2. Forces API keys to be loaded directly from the `.env` file
3. Ensures consistency across different test modules

### Implementation Details

```python
def load_api_keys():
    """
    Load API keys from .env file and ensure they're correctly set in the environment.

    This function:
    1. Loads variables from .env with override=True
    2. Forces the OPENAI_API_KEY to be loaded directly from the .env file
    """
    # Load environment variables with override
    load_dotenv(override=True)

    # Force load the API key from .env file
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.readlines()
        for line in env_content:
            if line.strip().startswith("OPENAI_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["OPENAI_API_KEY"] = key
                break
            # Also load other API keys if needed
            elif line.strip().startswith("ANTHROPIC_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["ANTHROPIC_API_KEY"] = key
            elif line.strip().startswith("MISTRAL_API_KEY="):
                key = line.strip().split("=", 1)[1]
                os.environ["MISTRAL_API_KEY"] = key
```

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test module:

```bash
pytest tests/test_agent.py
```

To run a specific test function:

```bash
pytest tests/test_agent.py::test_create_agent
```

## Test Environment Configuration

Create a `.env` file in the project root with your API keys:

```
# LLM API Keys (use dummy keys for testing if needed)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/muxi_test
```

For automated testing environments, you may use dummy API keys for providers you don't need to test.

## Mocking External Services

When testing components that depend on external services (like LLM providers), use mocks to avoid actual API calls:

```python
import unittest
from unittest.mock import patch, MagicMock

class TestLLMModel(unittest.TestCase):
    @patch('src.models.providers.openai.OpenAIModel.chat')
    def test_chat_functionality(self, mock_chat):
        # Configure the mock
        mock_chat.return_value = "Mocked response from the LLM"

        # Test your component that uses the LLM
        # ...
```

## Best Practices

1. **Isolate tests**: Each test should be independent and not rely on the state from other tests
2. **Use fixtures**: Create reusable test fixtures for common setup code
3. **Clean up resources**: Always clean up resources (like database connections) after tests
4. **Test edge cases**: Include tests for error conditions and edge cases
5. **Use consistent API key handling**: Always use the environment setup utility for API keys

## Continuous Integration

The framework uses GitHub Actions for continuous integration. Tests are automatically run on pull requests and pushes to the main branch.
