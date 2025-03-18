---
layout: default
title: Configuration Options
parent: Reference
nav_order: 2
permalink: /reference/configuration
---

# Configuration Options

MUXI Framework offers extensive configuration options to customize its behavior. This reference documents all available configuration parameters.

## Configuration Format

MUXI supports configuration via:
- YAML files (default)
- JSON files
- Environment variables
- Direct programmatic configuration

The default configuration file is located at `config.yaml` in the project root. You can specify an alternative configuration file using the `--config` command-line option.

## Core Configuration

### Application

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app.name` | string | `"MUXI Framework"` | Application name |
| `app.host` | string | `"127.0.0.1"` | Host to bind the server to |
| `app.port` | integer | `8000` | Port to bind the server to |
| `app.log_level` | string | `"info"` | Logging level (`debug`, `info`, `warning`, `error`, `critical`) |
| `app.environment` | string | `"development"` | Environment (`development`, `testing`, `production`) |
| `app.debug` | boolean | `false` | Enable debug mode |

### Security

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `security.secret_key` | string | N/A (Required) | Secret key for JWT tokens and encryption |
| `security.token_expiry` | integer | `3600` | JWT token expiry in seconds |
| `security.cors_origins` | list | `["*"]` | List of allowed CORS origins |
| `security.cors_methods` | list | `["*"]` | List of allowed CORS methods |
| `security.cors_headers` | list | `["*"]` | List of allowed CORS headers |
| `security.rate_limit.enabled` | boolean | `true` | Enable rate limiting |
| `security.rate_limit.limit` | integer | `60` | Default rate limit per minute |

## Database Configuration

### PostgreSQL

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `database.url` | string | `"postgresql://postgres:postgres@localhost:5432/muxi"` | Database connection URL |
| `database.pool_size` | integer | `5` | Connection pool size |
| `database.max_overflow` | integer | `10` | Maximum number of connections that can be created beyond pool_size |
| `database.pool_recycle` | integer | `300` | Connection recycle time in seconds |
| `database.echo` | boolean | `false` | Echo SQL queries for debugging |

## Memory Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `memory.buffer_size` | integer | `10` | Size of the buffer memory (number of messages) |
| `memory.search_k` | integer | `4` | Number of memories to retrieve in semantic search |
| `memory.similarity_threshold` | float | `0.7` | Minimum similarity score for memory matches |
| `memory.chunk_size` | integer | `1024` | Size of text chunks for embeddings |
| `memory.chunk_overlap` | integer | `200` | Overlap between text chunks |
| `memory.embedding_model` | string | `"text-embedding-ada-002"` | Model to use for text embeddings |

## Models Configuration

### OpenAI

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `models.openai.api_key` | string | N/A (Required) | OpenAI API key |
| `models.openai.organization` | string | `null` | OpenAI organization ID |
| `models.openai.default_model` | string | `"gpt-4"` | Default model to use |
| `models.openai.temperature` | float | `0.7` | Temperature for sampling |
| `models.openai.max_tokens` | integer | `1024` | Maximum tokens in completion |
| `models.openai.timeout` | integer | `120` | API timeout in seconds |
| `models.openai.retry_attempts` | integer | `3` | Number of retry attempts for API calls |

### Anthropic

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `models.anthropic.api_key` | string | N/A (Required) | Anthropic API key |
| `models.anthropic.default_model` | string | `"claude-3-opus-20240229"` | Default model to use |
| `models.anthropic.temperature` | float | `0.7` | Temperature for sampling |
| `models.anthropic.max_tokens` | integer | `1024` | Maximum tokens in completion |
| `models.anthropic.timeout` | integer | `120` | API timeout in seconds |

## MCP Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mcp.enabled` | boolean | `true` | Enable MCP system |
| `mcp.servers` | list | `[]` | List of MCP servers |
| `mcp.discovery.enabled` | boolean | `true` | Enable MCP server discovery |
| `mcp.discovery.interval` | integer | `300` | Server discovery interval in seconds |
| `mcp.timeout` | integer | `30` | Timeout for MCP server calls in seconds |
| `mcp.retry_attempts` | integer | `2` | Number of retry attempts for MCP calls |

### MCP Server Configuration Example

```yaml
mcp:
  servers:
    - id: "weather"
      name: "Weather Service"
      url: "https://api.example.com/mcp/weather"
      auth:
        type: "api_key"
        key_name: "X-API-Key"
        key_value: "${WEATHER_API_KEY}"
      functions:
        - name: "getCurrentWeather"
          description: "Get current weather for a location"
          parameters:
            location:
              type: "string"
              description: "City name or coordinates"
            units:
              type: "string"
              enum: ["metric", "imperial"]
              default: "metric"
```

## MCP Servers Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `mcp_servers.enabled` | boolean | `true` | Enable MCP servers system |
| `mcp_servers.search.url` | string | `"http://localhost:5001"` | URL for the search MCP server |
| `mcp_servers.search.api_key` | string | `null` | API key for the search MCP server |
| `mcp_servers.weather.url` | string | `"http://localhost:5002"` | URL for the weather MCP server |
| `mcp_servers.weather.api_key` | string | `null` | API key for the weather MCP server |
| `mcp_servers.calculator.url` | string | `"http://localhost:5003"` | URL for the calculator MCP server |

## WebSocket Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `websocket.enabled` | boolean | `true` | Enable WebSocket interface |
| `websocket.ping_interval` | integer | `30` | WebSocket ping interval in seconds |
| `websocket.ping_timeout` | integer | `10` | WebSocket ping timeout in seconds |
| `websocket.max_message_size` | integer | `1048576` | Maximum WebSocket message size in bytes |

## Environment Variables

All configuration options can be set via environment variables using the following format:

```
MUXI_[SECTION]_[PARAMETER]
```

For example:
- `MUXI_APP_PORT=9000`
- `MUXI_SECURITY_SECRET_KEY=mysecretkey`
- `MUXI_MODELS_OPENAI_API_KEY=sk-...`

Nested parameters use underscore as separator:
- `MUXI_SECURITY_RATE_LIMIT_ENABLED=false`

## Programmatic Configuration

When using MUXI programmatically, you can set configuration options during initialization:

```python
from muxi.core import MuxiApp

app = MuxiApp(
    config={
        "app": {
            "name": "My Custom MUXI App",
            "port": 9000
        },
        "models": {
            "openai": {
                "api_key": "sk-...",
                "default_model": "gpt-4"
            }
        }
    }
)
```

## Configuration Precedence

Configuration values are loaded in the following order, with later sources overriding earlier ones:

1. Default values
2. Configuration file
3. Environment variables
4. Programmatic configuration

## Sensitive Configuration

For security reasons, sensitive values like API keys should be provided through environment variables rather than in configuration files, especially in production environments.

When using a configuration file, you can reference environment variables using `${ENV_VAR}` syntax:

```yaml
models:
  openai:
    api_key: "${OPENAI_API_KEY}"
```

## Validation

MUXI validates configuration options at startup and will raise errors for required values that are missing or invalid. If you see configuration validation errors, check that:

1. All required values are provided
2. Values are of the correct type
3. Enum values are from the allowed set
4. Referenced files or directories exist and are readable
