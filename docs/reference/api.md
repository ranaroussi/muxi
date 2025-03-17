---
layout: default
title: API Documentation
parent: Reference
nav_order: 1
permalink: /reference/api/
---

# API Documentation

This page provides preliminary documentation for the MUXI Framework's REST API endpoints.

## Authentication

API endpoints require authentication. MUXI uses API key authentication.

To authenticate requests, include an `Authorization` header with a Bearer token:

```
Authorization: Bearer <token>
```

You can set the `token` when starting a muxi server with the `--api-key` flag.

## API Endpoints

### Agent Endpoints

#### GET /agents

List all available agents.

**Response:**
```json
{
  "agents": [
    {
      "id": "assistant-1",
      "name": "General Assistant",
      "description": "A general-purpose AI assistant"
    },
    {
      "id": "coder-1",
      "name": "Code Assistant",
      "description": "An AI assistant specialized in coding"
    }
  ]
}
```

#### POST /agents

Create a new agent.

**Request Body:**
```json
{
  "id": "custom-agent-1",
  "name": "Custom Agent",
  "description": "A custom-tailored agent",
  "model": {
    "provider": "openai",
    "name": "gpt-4",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1024
    }
  }
}
```

**Response:**
```json
{
  "id": "custom-agent-1",
  "name": "Custom Agent",
  "description": "A custom-tailored agent",
  "status": "created"
}
```

#### GET /agents/{agent_id}

Get details about a specific agent.

**Response:**
```json
{
  "id": "assistant-1",
  "name": "General Assistant",
  "description": "A general-purpose AI assistant",
  "model": {
    "provider": "openai",
    "name": "gpt-4",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1024
    }
  }
}
```

#### DELETE /agents/{agent_id}

Delete a specific agent.

**Response:**
```json
{
  "status": "deleted",
  "id": "assistant-1"
}
```

### Chat Endpoints

#### POST /chat/{agent_id}

Send a message to an agent.

**Request Body:**
```json
{
  "message": "What's the weather like today?",
  "user_id": "user123",
  "session_id": "session456",
  "context": {
    "location": "New York"
  }
}
```

**Response:**
```json
{
  "id": "msg_123456",
  "content": "I don't have real-time weather data, but I can help you find weather information for New York.",
  "timestamp": "2023-09-21T14:32:01Z",
  "agent_id": "assistant-1",
  "session_id": "session456"
}
```

#### GET /chat/{agent_id}/history

Get chat history for a specific agent and user session.

**Parameters:**
- `user_id` (required): The user's ID
- `session_id` (required): The session ID
- `limit` (optional): Maximum number of messages to return (default: 50)
- `before` (optional): Return messages before this timestamp

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_123455",
      "role": "user",
      "content": "What's the weather like today?",
      "timestamp": "2023-09-21T14:31:45Z"
    },
    {
      "id": "msg_123456",
      "role": "assistant",
      "content": "I don't have real-time weather data, but I can help you find weather information for New York.",
      "timestamp": "2023-09-21T14:32:01Z"
    }
  ],
  "has_more": false
}
```

### Memory Endpoints

#### GET /memory/{agent_id}

Query an agent's memory.

**Parameters:**
- `user_id` (required): The user's ID
- `query` (required): The search query
- `limit` (optional): Maximum number of memories to return (default: 10)

**Response:**
```json
{
  "memories": [
    {
      "id": "mem_123456",
      "content": "User lives in New York",
      "created_at": "2023-09-20T10:15:30Z",
      "relevance_score": 0.95
    },
    {
      "id": "mem_123457",
      "content": "User mentioned they like sunny weather",
      "created_at": "2023-09-19T11:20:15Z",
      "relevance_score": 0.82
    }
  ]
}
```

#### POST /memory/{agent_id}

Add a memory for an agent.

**Request Body:**
```json
{
  "user_id": "user123",
  "content": "User prefers vegetarian food",
  "metadata": {
    "source": "conversation",
    "importance": "high"
  }
}
```

**Response:**
```json
{
  "id": "mem_123458",
  "status": "created",
  "created_at": "2023-09-21T14:40:22Z"
}
```

## Error Responses

All API endpoints return standard HTTP status codes. In case of an error, the response body will contain additional information:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Missing required parameter: user_id",
    "details": {
      "param": "user_id"
    }
  }
}
```

Common error codes:
- `invalid_request`: The request is malformed or missing required parameters
- `authentication_error`: Authentication failed
- `permission_denied`: The authenticated user doesn't have permission for this action
- `not_found`: The requested resource doesn't exist
- `rate_limit_exceeded`: The rate limit for the API has been exceeded
- `internal_error`: An internal server error occurred

## Rate Limiting

API requests are subject to rate limiting. The current limits are:
- 60 requests per minute per user for most endpoints
- 10 requests per minute per user for resource-intensive endpoints

Rate limit information is included in the response headers:
- `X-RateLimit-Limit`: The rate limit ceiling
- `X-RateLimit-Remaining`: The number of requests left for the time window
- `X-RateLimit-Reset`: The remaining window before the rate limit resets in UTC epoch seconds

## Pagination

Endpoints that return lists of resources support pagination using the following parameters:
- `limit`: Number of items to return per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

Paginated responses include metadata:

```json
{
  "items": [...],
  "pagination": {
    "total": 120,
    "limit": 50,
    "offset": 0,
    "next_offset": 50
  }
}
```

## Versioning

The API version is specified in the URL path: `/api/v1/...`

When breaking changes are introduced, a new API version will be released. Previous versions will be maintained for a reasonable deprecation period.

---

**Note**: This is preliminary API documentation. The complete API design will be finalized at a later stage of development.
