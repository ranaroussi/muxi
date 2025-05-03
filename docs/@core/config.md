# Configuration System in Muxi Core

The Muxi Framework offers a flexible configuration system that allows developers to customize the behavior of various components through multiple methods. This document provides a comprehensive guide to the configuration options and approaches available in Muxi Core.

## Configuration Architecture

The configuration system in Muxi follows a hierarchical structure with specialized components for different aspects of the framework:

```mermaid
graph TD
    Config[Main Config]
    ConfigLoader[Config Loader]

    Config --> Routing[Routing Config]
    Config --> Memory[Memory Config]
    Config --> Model[Model Config]
    Config --> Database[Database Config]
    Config --> App[App Config]

    ConfigLoader --> YAML[YAML Config]
    ConfigLoader --> JSON[JSON Config]
    ConfigLoader --> ENV[Environment Variables]
    ConfigLoader --> Code[Programmatic Config]
```

### Core Configuration Components

1. **Config**: The main configuration class that combines all other configuration components
2. **RoutingConfig**: Settings for the intelligent message routing system
3. **MemoryConfig**: Configuration for buffer and long-term memory systems
4. **ModelConfig**: Default model settings and provider-specific configurations
5. **DatabaseConfig**: Database connection and performance settings
6. **AppConfig**: General application settings like host, port, and environment

## Configuration Methods

Muxi supports four primary methods for configuration, offering flexibility to developers:

### 1. Environment Variables

The simplest method is using environment variables, which is the default fallback for all configuration components:

```bash
# Routing configuration
export ROUTING_LLM=openai
export ROUTING_LLM_MODEL=gpt-4o-mini
export ROUTING_LLM_TEMPERATURE=0.0
export ROUTING_LLM_MAX_TOKENS=256
export ROUTING_USE_CACHING=true
export ROUTING_CACHE_TTL=3600

# Memory configuration
export BUFFER_SIZE=10
export BUFFER_MULTIPLIER=10
export LONG_TERM_ENABLED=true
export LONG_TERM_CONNECTION=postgresql://user:pass@localhost/muxi

# Model configuration
export OPENAI_API_KEY=your-api-key-here
export DEFAULT_MODEL=gpt-4o
export MODEL_TEMPERATURE=0.7
```

### 2. Configuration Files (YAML/JSON)

For more complex configurations, YAML or JSON files are recommended:

```yaml
# config.yaml
name: my_app
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"  # Can reference environment variables
  model: gpt-4o
  temperature: 0.7
memory:
  buffer_size: 10
  buffer_multiplier: 10
  long_term: true
routing:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.0
  max_tokens: 256
```

```python
# Using a config file
from muxi import muxi
from muxi.core.config.loader import ConfigLoader

# Load and process config file
loader = ConfigLoader()
config = loader.load_and_process("config.yaml")

# Use config with Muxi
app = muxi()
await app.add_agent("assistant", config)
```

### 3. Direct Parameters

You can provide configuration directly as parameters:

```python
from muxi import muxi

# Create a MUXI application with direct configuration
app = muxi(
    buffer_size=15,           # Override default buffer size
    buffer_multiplier=20,     # Override default buffer multiplier
    long_term_memory="postgresql://user:pass@localhost/muxi",  # Use PostgreSQL
    user_api_key="my-custom-api-key",   # Custom API key
    admin_api_key="my-custom-admin-key" # Custom admin key
)

# Create an agent with direct configuration
await app.add_agent(
    "assistant",
    model={
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.5,
        "api_key": "your-openai-key-here"  # Directly provide API key
    },
    system_message="Custom system message"
)
```

### 4. Programmatic Configuration

For maximum flexibility, you can create and customize configuration objects programmatically:

```python
from muxi.core.config.routing import RoutingConfig
from muxi import muxi
from muxi.core.orchestrator import Orchestrator

# Create a custom routing configuration
custom_routing = RoutingConfig(
    provider="openai",
    model="gpt-4",  # Override default gpt-4o-mini
    temperature=0.1,  # Override default 0.0
    max_tokens=512,  # Override default 256
    use_caching=True,
    cache_ttl=7200,  # Override default 3600
    system_prompt="Custom routing prompt that you specify directly in code"
)

# Create an orchestrator with custom routing configuration
orchestrator = Orchestrator()

# Set the custom routing configuration
orchestrator.routing_config = custom_routing

# Initialize the routing model with your custom configuration
orchestrator._initialize_routing_model()
```

## Configuration Component Details

### RoutingConfig

The `RoutingConfig` class configures the intelligent message routing system that directs user messages to the appropriate agent:

```python
from muxi.core.config.routing import RoutingConfig

routing_config = RoutingConfig(
    provider="openai",         # LLM provider for routing
    model="gpt-4o-mini",       # Model to use
    temperature=0.0,           # Keep deterministic for routing
    max_tokens=256,            # Maximum response tokens
    use_caching=True,          # Cache routing decisions
    cache_ttl=3600,            # Cache TTL in seconds
    system_prompt="You are a routing assistant..."  # Custom system prompt
)
```

### MemoryConfig

The `MemoryConfig` class configures both buffer and long-term memory systems:

```python
from muxi.core.config.memory import MemoryConfig

memory_config = MemoryConfig(
    buffer_size=10,            # Context window size
    buffer_multiplier=10,      # Buffer capacity multiplier
    buffer_recency_bias=0.3,   # Balance between recency and relevance
    long_term_enabled=True,    # Enable long-term memory
    connection_string="postgresql://user:pass@localhost/muxi"  # DB connection
)
```

### ModelConfig

The `ModelConfig` class provides default settings for language models:

```python
from muxi.core.config.model import ModelConfig

model_config = ModelConfig(
    default_provider="openai",     # Default provider
    default_model="gpt-4o",        # Default model
    default_temperature=0.7,       # Default temperature
    request_timeout=60,            # Request timeout in seconds
    max_retries=3,                 # Maximum retry attempts
    api_keys={                     # API keys for different providers
        "openai": "your-openai-key",
        "anthropic": "your-anthropic-key"
    }
)
```

### Full Configuration Example

Here's an example of a comprehensive programmatic configuration:

```python
from muxi.core.config import Config, RoutingConfig, MemoryConfig, ModelConfig, DatabaseConfig
from muxi.core.orchestrator import Orchestrator

# Create individual configurations
routing_config = RoutingConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.1
)

memory_config = MemoryConfig(
    buffer_size=15,
    buffer_multiplier=20,
    long_term_enabled=True,
    connection_string="postgresql://user:pass@localhost/muxi"
)

model_config = ModelConfig(
    default_provider="anthropic",
    default_model="claude-3-opus-20240229",
    default_temperature=0.7
)

database_config = DatabaseConfig(
    url="postgresql://user:pass@localhost/muxi",
    pool_size=10,
    max_overflow=20
)

# Create the main configuration
config = Config(
    routing=routing_config,
    memory=memory_config,
    model=model_config,
    database=database_config
)

# Use the configuration with an orchestrator
orchestrator = Orchestrator(config=config)
```

## Configuration Loading Process

The `ConfigLoader` class handles loading and processing configuration files:

1. **Loading**: Read YAML or JSON files into Python dictionaries
2. **Environment Variable Substitution**: Replace `${ENV_VAR}` patterns with actual environment variable values
3. **Normalization**: Convert simplified formats to standard structure
4. **Validation**: Ensure required fields are present and have valid values

```python
from muxi.core.config.loader import ConfigLoader

loader = ConfigLoader()

# Load a configuration file
config = loader.load("config.yaml")  # or .json

# Process environment variables
config = loader.process_env_vars(config)

# Normalize configuration
config = loader.normalize_config(config)

# Validate configuration
loader.validate_config(config)

# Or use the all-in-one method
config = loader.load_and_process("config.yaml")
```

## Configuration Best Practices

### 1. Environment Variables for Sensitive Data

Use environment variables for sensitive information like API keys and database credentials:

```yaml
# In configuration file
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o

database:
  url: "${DATABASE_URL}"
```

### 2. Configuration Files for Complex Settings

Use YAML or JSON files for complex configurations that might change between environments:

```bash
# Development
$ MUXI_CONFIG=config.dev.yaml python app.py

# Production
$ MUXI_CONFIG=config.prod.yaml python app.py
```

### 3. Programmatic Configuration for Dynamic Settings

Use programmatic configuration for settings that might change during runtime:

```python
# Adjust routing based on system load
if system_load > 0.8:
    orchestrator.routing_config.model = "gpt-4o-mini"  # Use faster model
    orchestrator.routing_config.cache_ttl = 7200       # Cache longer
    orchestrator._initialize_routing_model()           # Re-initialize with new config
else:
    orchestrator.routing_config.model = "gpt-4"        # Use more capable model
    orchestrator.routing_config.cache_ttl = 3600       # Standard cache
    orchestrator._initialize_routing_model()           # Re-initialize with new config
```

### 4. Configuration Layering

Implement a layering approach for configuration, with each layer overriding the previous:

1. Default values in code
2. Global configuration files
3. Environment-specific configuration files
4. Environment variables
5. Command-line arguments
6. Programmatic overrides

### 5. Validation and Documentation

Always validate configurations early and provide good error messages:

```python
try:
    config = loader.load_and_process("config.yaml")
except ValueError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

### 6. Version Control for Configuration Templates

Store configuration templates (without sensitive values) in version control:

```yaml
# config.template.yaml
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"  # Will be filled from environment
  model: gpt-4o
```

## Configuration Overrides

When multiple configuration sources are available, Muxi follows this precedence order (highest priority first):

1. Programmatic overrides via code
2. Direct parameters to Muxi or Orchestrator constructors
3. Configuration files explicitly provided
4. Environment variables
5. Default values hardcoded in the framework

This allows for flexible configuration management across different environments while maintaining the ability to override specific settings as needed.
