# MUXI Framework API Specification

This document outlines the REST API for the MUXI Framework, providing a standard interface for interacting with agents, memories, and MCP servers.

## API Overview

The MUXI API follows REST principles and uses JSON for request and response bodies. All endpoints return appropriate HTTP status codes and consistent response structures.

### Base URL

```
https://your-muxi-server.com/api/v1
```

For local development:

```
http://localhost:5050/api/v1
```

## Authentication

All API requests require authentication using API keys passed in the `Authorization` header.

### Authentication Header

```
Authorization: Bearer sk_muxi_YOUR_API_KEY
```

### API Key Generation

API keys are generated when starting the server through
`app.run(api_key=True)` or can be provided explicitly through `app.run(api_key="your_custom_key")`.

To start a server without an API key (not recommended, unless during development), start the server using `app.run(api_key=False)`.

### API Key Management

For production systems, it is recommended to rotate API keys periodically and restrict them by scope and IP address. Future versions will include API key management endpoints.

### Response for Unauthorized Requests

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid or missing API key"
  }
}
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

Common error codes:

- `unauthorized`: Authentication failed
- `not_found`: Resource not found
- `bad_request`: Invalid request parameters
- `rate_limited`: Too many requests
- `internal_error`: Server error

## Endpoints

### Agent Management

#### List Agents

```http
GET /agents
```

**Response**:

```json
{
  "agents": [
    {
      "id": "assistant",
      "description": "General-purpose assistant",
      "model": {
        "provider": "openai",
        "model": "gpt-4o"
      },
      "created_at": "2023-07-15T10:30:45Z",
      "stats": {
        "conversations": 42,
        "total_messages": 156
      }
    },
    {
      "id": "weather_expert",
      "description": "Weather forecasting assistant",
      "model": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229"
      },
      "created_at": "2023-07-16T14:22:10Z",
      "stats": {
        "conversations": 18,
        "total_messages": 67
      }
    }
  ]
}
```

#### Get Agent Details

```http
GET /agents/{agent_id}
```

**Response**:

```json
{
  "id": "assistant",
  "description": "General-purpose assistant",
  "model": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "top_p": 0.9
  },
  "created_at": "2023-07-15T10:30:45Z",
  "system_message": "You are a helpful assistant...",
  "memory": {
    "buffer": 10,
    "long_term": true
  },
  "stats": {
    "conversations": 42,
    "total_messages": 156,
    "active_users": 12
  },
  "mcp_servers": [
    {
      "name": "calculator",
      "type": "command",
      "connected": true
    },
    {
      "name": "web_search",
      "type": "http",
      "connected": true
    }
  ],
  "knowledge_sources": [
    {
      "id": "products",
      "description": "Product information",
      "document_count": 5
    }
  ]
}
```

#### Create Agent

```http
POST /agents
```

**Request Body**:

```json
{
  "id": "finance_expert",
  "description": "Financial advice assistant",
  "model": {
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4o",
    "temperature": 0.2
  },
  "system_message": "You are a financial advisor...",
  "memory": {
    "buffer": 15,
    "long_term": true
  }
}
```

**Response**:

```json
{
  "id": "finance_expert",
  "description": "Financial advice assistant",
  "created_at": "2023-07-18T09:15:30Z",
  "status": "created"
}
```

#### Update Agent

```http
PATCH /agents/{agent_id}
```

**Request Body** (partial updates supported):

```json
{
  "description": "Updated description",
  "system_message": "Updated system message",
  "model": {
    "temperature": 0.5
  }
}
```

**Response**:

```json
{
  "id": "finance_expert",
  "description": "Updated description",
  "updated_at": "2023-07-18T10:20:35Z",
  "status": "updated"
}
```

#### Delete Agent

```http
DELETE /agents/{agent_id}
```

**Response**:

```json
{
  "id": "finance_expert",
  "status": "deleted"
}
```

#### Import Agent from Config

```http
POST /agents/import
```

**Request Body**:

```json
{
  "config_path": "configs/weather_agent.yaml"
}
```

Or:

```json
{
  "config": {
    "id": "weather_expert",
    "description": "Weather forecast assistant",
    "model": {
      "provider": "openai",
      "model": "gpt-4o"
    },
    "system_message": "You are a weather expert...",
    "memory": {
      "buffer": 10,
      "long_term": true
    },
    "mcp_servers": [
      {
        "name": "weather_api",
        "url": "http://localhost:5001",
        "credentials": {
          "api_key": "${WEATHER_API_KEY}"
        }
      }
    ]
  }
}
```

**Response**:

```json
{
  "id": "weather_expert",
  "description": "Weather forecast assistant",
  "created_at": "2023-07-18T09:15:30Z",
  "status": "created",
  "mcp_servers_connected": 1
}
```

### Conversation Management

#### Send Message to Agent

```http
POST /agents/{agent_id}/chat
```

**Request Body**:

```json
{
  "content": "What's the weather like in New York?",
  "user_id": "user123"
}
```

**Response**:

```json
{
  "id": "msg_12345",
  "agent_id": "weather_expert",
  "user_id": "user123",
  "user_message": {
    "role": "user",
    "content": "What's the weather like in New York?"
  },
  "agent_response": {
    "role": "assistant",
    "content": "Currently in New York City, it's 72°F (22°C) and partly cloudy...",
    "tool_calls": [
      {
        "name": "get_weather",
        "parameters": {
          "location": "New York, NY"
        },
        "output": {
          "temperature": 72,
          "condition": "partly cloudy",
          "humidity": 65
        }
      }
    ]
  },
  "created_at": "2023-07-18T10:30:45Z"
}
```

#### Stream Message to Agent

```http
POST /agents/{agent_id}/chat/stream
```

**Request Body**:

```json
{
  "content": "What's the weather like in New York?",
  "user_id": "user123"
}
```

**Response**: Server-Sent Events (SSE) stream

```
event: message_start
data: {"id":"msg_12345","created_at":"2023-07-18T10:30:45Z"}

event: content
data: {"content":"Currently "}

event: content
data: {"content":"in "}

event: content
data: {"content":"New York City, "}

event: tool_call_start
data: {"id":"call_1","name":"get_weather","parameters":{"location":"New York, NY"}}

event: tool_call_end
data: {"id":"call_1","output":{"temperature":72,"condition":"partly cloudy","humidity":65}}

event: content
data: {"content":"it's 72°F (22°C) and partly cloudy..."}

event: message_end
data: {"id":"msg_12345"}
```

#### Chat with Orchestrator (Auto-Route)

```http
POST /chat
```

**Request Body**:

```json
{
  "content": "What's the weather like in New York?",
  "user_id": "user123"
}
```

The response format is the same as `POST /agents/{agent_id}/messages` but includes which agent handled the request:

```json
{
  "id": "msg_12345",
  "agent_id": "weather_expert",  // The agent selected by the orchestrator
  "routing_confidence": 0.92,    // Confidence score for routing decision
  "user_id": "user123",
  "user_message": {
    "role": "user",
    "content": "What's the weather like in New York?"
  },
  "agent_response": {
    "role": "assistant",
    "content": "Currently in New York City, it's 72°F (22°C) and partly cloudy..."
  },
  "created_at": "2023-07-18T10:30:45Z"
}
```

#### Stream Chat with Orchestrator (Auto-Route)

```http
POST /chat/stream
```

Similar to the agent streaming endpoint, but includes routing information in the initial event.

#### Get Conversation History

```http
GET /agents/{agent_id}/conversations?user_id={user_id}&limit=20&before=msg_12345
```

**Response**:

```json
{
  "messages": [
    {
      "id": "msg_12344",
      "agent_id": "weather_expert",
      "user_id": "user123",
      "user_message": {
        "role": "user",
        "content": "Do I need an umbrella tomorrow?"
      },
      "agent_response": {
        "role": "assistant",
        "content": "Based on the forecast for tomorrow in New York..."
      },
      "created_at": "2023-07-18T10:25:30Z"
    },
    {
      "id": "msg_12343",
      "agent_id": "weather_expert",
      "user_id": "user123",
      "user_message": {
        "role": "user",
        "content": "I live in New York City"
      },
      "agent_response": {
        "role": "assistant",
        "content": "Great! I'll remember that you're located in New York City..."
      },
      "created_at": "2023-07-18T10:20:15Z"
    }
  ],
  "has_more": true
}
```

#### Clear Conversation History

```http
DELETE /agents/{agent_id}/conversations?user_id={user_id}
```

**Response**:

```json
{
  "status": "cleared",
  "agent_id": "weather_expert",
  "user_id": "user123",
  "message_count": 5
}
```

### Memory Operations

#### Search Agent Memory

```http
GET /agents/{agent_id}/memory/search?query=weather&user_id=user123&limit=5
```

**Response**:

```json
{
  "results": [
    {
      "content": "The weather in New York is sunny today",
      "similarity": 0.92,
      "created_at": "2023-07-17T15:20:10Z",
      "message_id": "msg_12340"
    },
    {
      "content": "Tomorrow's weather forecast shows rain",
      "similarity": 0.85,
      "created_at": "2023-07-17T16:35:22Z",
      "message_id": "msg_12342"
    }
  ]
}
```

#### Clear Agent Memory

```http
DELETE /agents/{agent_id}/memory?user_id=user123
```

**Response**:

```json
{
  "status": "cleared",
  "agent_id": "weather_expert",
  "user_id": "user123"
}
```

#### Add Context Memory for User

```http
POST /users/{user_id}/context_memory
```

**Request Body**:

```json
{
  "knowledge": {
    "name": "John Smith",
    "location": {
      "city": "New York",
      "country": "USA"
    },
    "preferences": {
      "temperature_unit": "fahrenheit",
      "language": "english"
    }
  }
}
```

**Response**:

```json
{
  "status": "added",
  "user_id": "user123",
  "fields_added": ["name", "location", "preferences"]
}
```

#### Get Context Memory for User

```http
GET /users/{user_id}/context_memory
```

**Response**:

```json
{
  "user_id": "user123",
  "knowledge": {
    "name": "John Smith",
    "location": {
      "city": "New York",
      "country": "USA"
    },
    "preferences": {
      "temperature_unit": "fahrenheit",
      "language": "english"
    }
  },
  "last_updated": "2023-07-18T10:15:30Z"
}
```

#### Update Context Memory for User

```http
PATCH /users/{user_id}/context_memory
```

**Request Body**:

```json
{
  "knowledge": {
    "location": {
      "city": "Boston"
    },
    "preferences": {
      "temperature_unit": "celsius"
    }
  }
}
```

**Response**:

```json
{
  "status": "updated",
  "user_id": "user123",
  "fields_updated": ["location.city", "preferences.temperature_unit"]
}
```

#### Delete Context Memory for User

```http
DELETE /users/{user_id}/context_memory?fields=preferences
```

**Response**:

```json
{
  "status": "deleted",
  "user_id": "user123",
  "fields_deleted": ["preferences"]
}
```

### MCP Server Management

#### List MCP Servers for Agent

```http
GET /agents/{agent_id}/mcp_servers
```

**Response**:

```json
{
  "agent_id": "weather_expert",
  "mcp_servers": [
    {
      "name": "weather_api",
      "type": "http",
      "url": "http://localhost:5001",
      "connected": true,
      "stats": {
        "connection_age_s": 3600,
        "idle_time_s": 120,
        "active_requests": 0
      }
    },
    {
      "name": "geocoding",
      "type": "command",
      "command": "npx geocoding-server",
      "connected": true,
      "stats": {
        "connection_age_s": 3600,
        "idle_time_s": 300,
        "active_requests": 0,
        "pid": 12345
      }
    }
  ]
}
```

#### Connect MCP Server

```http
POST /agents/{agent_id}/mcp_servers
```

**Request Body**:

```json
{
  "name": "weather_api",
  "url": "http://localhost:5001",
  "credentials": {
    "api_key": "your_api_key_here"
  }
}
```

Or for command-line servers:

```json
{
  "name": "calculator",
  "command": "npx -y @modelcontextprotocol/server-calculator"
}
```

**Response**:

```json
{
  "status": "connected",
  "agent_id": "weather_expert",
  "server": {
    "name": "weather_api",
    "type": "http",
    "connected": true
  }
}
```

#### Disconnect MCP Server

```http
DELETE /agents/{agent_id}/mcp_servers/{server_name}
```

**Response**:

```json
{
  "status": "disconnected",
  "agent_id": "weather_expert",
  "server": {
    "name": "weather_api"
  }
}
```

#### Get MCP Server Status

```http
GET /agents/{agent_id}/mcp_servers/{server_name}
```

**Response**:

```json
{
  "name": "weather_api",
  "type": "http",
  "url": "http://localhost:5001",
  "connected": true,
  "stats": {
    "connection_age_s": 3600,
    "idle_time_s": 120,
    "active_requests": 0,
    "session_id": "sess_abc123",
    "current_time": "2023-07-18T10:30:45Z",
    "connect_time": "2023-07-18T09:30:45Z",
    "last_activity": "2023-07-18T10:28:45Z"
  },
  "available_tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          }
        },
        "required": ["location"]
      }
    },
    {
      "name": "get_forecast",
      "description": "Get weather forecast for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          },
          "days": {
            "type": "integer",
            "description": "Number of days to forecast"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### Knowledge Management

#### List Agent Knowledge Sources

```http
GET /agents/{agent_id}/knowledge
```

**Response**:

```json
{
  "agent_id": "product_assistant",
  "knowledge_sources": [
    {
      "id": "products",
      "description": "Product catalog information",
      "document_count": 5,
      "created_at": "2023-07-15T10:30:45Z"
    },
    {
      "id": "faqs",
      "description": "Frequently asked questions",
      "document_count": 10,
      "created_at": "2023-07-16T14:22:10Z"
    }
  ]
}
```

#### Add Knowledge Source

```http
POST /agents/{agent_id}/knowledge
```

**Request Body**:

```json
{
  "id": "pricing",
  "description": "Product pricing information",
  "source_type": "file",
  "path": "knowledge/pricing.txt"
}
```

Or for content-based knowledge:

```json
{
  "id": "refund_policy",
  "description": "Product refund policy",
  "source_type": "content",
  "content": "Our refund policy allows returns within 30 days of purchase..."
}
```

**Response**:

```json
{
  "status": "added",
  "agent_id": "product_assistant",
  "knowledge_source": {
    "id": "pricing",
    "description": "Product pricing information",
    "document_count": 1,
    "created_at": "2023-07-18T10:30:45Z"
  }
}
```

#### Remove Knowledge Source

```http
DELETE /agents/{agent_id}/knowledge/{knowledge_id}
```

**Response**:

```json
{
  "status": "removed",
  "agent_id": "product_assistant",
  "knowledge_source": {
    "id": "pricing"
  }
}
```

#### Search Agent Knowledge

```http
GET /agents/{agent_id}/knowledge/search?query=pricing+tiers&top_k=3&threshold=0.7
```

**Response**:

```json
{
  "agent_id": "product_assistant",
  "query": "pricing tiers",
  "results": [
    {
      "content": "Our product has three pricing tiers: Basic ($10/mo), Pro ($30/mo), and Enterprise ($100/mo).",
      "similarity": 0.92,
      "knowledge_id": "pricing",
      "document_id": "pricing_1"
    },
    {
      "content": "Enterprise tier includes unlimited API calls and 24/7 support.",
      "similarity": 0.81,
      "knowledge_id": "pricing",
      "document_id": "pricing_1"
    },
    {
      "content": "Volume discounts are available for annual subscriptions.",
      "similarity": 0.75,
      "knowledge_id": "pricing",
      "document_id": "pricing_1"
    }
  ]
}
```

### System Information

#### Get System Status

```http
GET /system/status
```

**Response**:

```json
{
  "status": "healthy",
  "version": "0.3.0",
  "uptime_seconds": 86400,
  "active_agents": 5,
  "active_connections": 12,
  "memory_usage_mb": 256,
  "database_status": "connected"
}
```

#### Get API Usage Stats

```http
GET /system/usage
```

**Response**:

```json
{
  "period": "last_24h",
  "endpoints": {
    "/chat": 1250,
    "/agents/{agent_id}/messages": 3420,
    "/agents/{agent_id}/memory/search": 156
  },
  "agent_usage": {
    "assistant": 1520,
    "weather_expert": 780,
    "finance_advisor": 420
  },
  "user_count": 45,
  "total_requests": 5230
}
```

## WebSocket API

In addition to the REST API, MUXI provides a WebSocket API for real-time communication, especially useful for multi-modal interactions.

### WebSocket Connection

```
wss://your-muxi-server.com/api/v1/ws?api_key=sk_muxi_YOUR_API_KEY
```

### WebSocket Message Format

All WebSocket messages use the following format:

```json
{
  "type": "message_type",
  "id": "unique_request_id",
  "data": {
    // Message-specific data
  }
}
```

### Message Types

#### Chat Message

**Client → Server**:

```json
{
  "type": "chat",
  "id": "req_12345",
  "data": {
    "agent_id": "assistant",  // Optional, will use orchestrator if omitted
    "user_id": "user123",     // Optional
    "content": "Tell me about this image",
    "attachments": [
      {
        "type": "image/jpeg",
        "name": "photo.jpg",
        "data": "base64_encoded_data_here"
      }
    ]
  }
}
```

**Server → Client** (Response chunks):

```json
{
  "type": "chat_start",
  "id": "req_12345",
  "data": {
    "message_id": "msg_54321",
    "agent_id": "image_expert"  // The agent handling the request
  }
}
```

```json
{
  "type": "chat_content",
  "id": "req_12345",
  "data": {
    "content": "This image shows a "
  }
}
```

```json
{
  "type": "chat_content",
  "id": "req_12345",
  "data": {
    "content": "mountain landscape with "
  }
}
```

```json
{
  "type": "chat_end",
  "id": "req_12345",
  "data": {
    "message_id": "msg_54321"
  }
}
```

#### Error Message

```json
{
  "type": "error",
  "id": "req_12345",
  "data": {
    "code": "bad_request",
    "message": "Invalid file format"
  }
}
```

## Implementation Roadmap

### Phase 1: Core API (v0.3.0)

- Authentication system
- Agent management endpoints
- Basic conversation endpoints
- Memory search and management

### Phase 2: Advanced Features (v0.4.0)

- MCP server management
- Knowledge management
- WebSocket support for real-time communication
- Streaming responses

### Phase 3: Scaling & Monitoring (v0.5.0)

- System status and monitoring
- API usage statistics
- Rate limiting and quotas
- Multi-modal content support

## Security Considerations

- All API endpoints must be secured with HTTPS in production
- API keys should be stored securely and rotated regularly
- Implement rate limiting to prevent abuse
- Add request validation to prevent injection attacks
- Sanitize all user input to prevent XSS
- Implement proper logging for security auditing
- Consider adding IP-based restrictions for sensitive operations
