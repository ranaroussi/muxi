# REST API

The AI Agent Framework provides a comprehensive REST API for interacting with agents, managing tools, and accessing memory. This guide explains the available endpoints and how to use them.

## API Overview

The REST API offers the following capabilities:
- Create, manage, and delete agents
- Send messages to agents
- Access and search agent memory
- List and manage available tools
- Monitor agent and system status
- Support multi-user contexts with user-specific memory

## Getting Started

### Starting the API Server

To start the API server, run:

```bash
# Start the API server on the default port (5050)
python -m src.api.run

# Start the API server on a different port
python -m src.api.run --port 8080

# Start the API server with auto-reload for development
python -m src.api.run --reload
```

### API Documentation

The API includes Swagger documentation, which can be accessed at:

```
http://localhost:5050/docs
```

### Authentication

By default, the API doesn't require authentication in development mode. For production deployments, you can enable authentication by setting the `API_AUTH_ENABLED` environment variable:

```bash
# Enable authentication
export API_AUTH_ENABLED=true
export API_KEY=your_secret_api_key

# Then start the server
python -m src.api.run
```

When authentication is enabled, include the API key in the headers:

```bash
curl -X GET http://localhost:5050/agents \
  -H "Authorization: Bearer your_secret_api_key"
```

## API Endpoints

### Health Check

Check if the API server is running:

```bash
# Request
curl -X GET http://localhost:5050/

# Response (200 OK)
{
  "status": "ok",
  "version": "0.1.0"
}
```

### Agent Management

#### List Agents

Retrieve all registered agents:

```bash
# Request
curl -X GET http://localhost:5050/agents

# Response (200 OK)
{
  "agents": [
    {
      "agent_id": "research_assistant",
      "tools": ["web_search", "calculator"],
      "is_default": true
    },
    {
      "agent_id": "coding_assistant",
      "tools": ["calculator"],
      "is_default": false
    }
  ]
}
```

#### Create Agent

Create a new agent:

```bash
# Request
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "model": "gpt-4o",
    "system_message": "You are a helpful AI assistant.",
    "enable_web_search": true,
    "enable_calculator": true,
    "use_long_term_memory": true,
    "multi_user_support": true
  }'

# Response (200 OK)
{
  "message": "Agent 'my_agent' created successfully"
}
```

Parameters:
- `agent_id` (required): Unique identifier for the agent
- `model`: LLM model to use (default: "gpt-4o")
- `system_message`: Instructions for the agent's behavior
- `enable_web_search`: Whether to enable the web search tool (default: false)
- `enable_calculator`: Whether to enable the calculator tool (default: false)
- `use_long_term_memory`: Whether to enable long-term memory (default: false)
- `multi_user_support`: Whether to enable multi-user support via Memobase (default: false)

#### Get Agent

Retrieve information about a specific agent:

```bash
# Request
curl -X GET http://localhost:5050/agents/data_analyst

# Response (200 OK)
{
  "agent_id": "data_analyst",
  "tools": ["calculator", "web_search"],
  "is_default": false,
  "created_at": "2023-06-15T14:30:00Z"
}
```

#### Delete Agent

Delete an agent:

```bash
# Request
curl -X DELETE http://localhost:5050/agents/data_analyst

# Response (200 OK)
{
  "status": "success",
  "message": "Agent 'data_analyst' deleted successfully"
}
```

#### Set Default Agent

Set an agent as the default:

```bash
# Request
curl -X POST http://localhost:5050/agents/research_assistant/set_default

# Response (200 OK)
{
  "status": "success",
  "message": "Agent 'research_assistant' set as default"
}
```

### Chat

#### Send Message to Agent

Send a message to an agent:

```bash
# Request
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "message": "What is the capital of France?",
    "user_id": 123
  }'

# Response (200 OK)
{
  "message": "The capital of France is Paris.",
  "agent_id": "my_agent",
  "user_id": 123,
  "tools_used": []
}
```

Parameters:
- `message` (required): The message to send to the agent
- `agent_id`: ID of the agent to send the message to (uses default if omitted)
- `user_id`: User ID for multi-user support (default: 0)

#### Chat with Default Agent

Send a message to the default agent:

```bash
# Request
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?"
  }'

# Response (200 OK)
{
  "agent_id": "research_assistant",
  "message": "The capital of France is Paris.",
  "tokens": {
    "prompt": 45,
    "completion": 8,
    "total": 53
  }
}
```

#### Streaming Chat

Stream a response from an agent:

```bash
# Request
curl -X POST http://localhost:5050/agents/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "research_assistant",
    "message": "Tell me about quantum computing"
  }'

# Response (200 OK, server-sent events)
data: {"chunk": "Quantum computing is", "done": false}

data: {"chunk": " a type of computing", "done": false}

data: {"chunk": " that uses quantum mechanics", "done": false}

...

data: {"chunk": "", "done": true}
```

### Memory

#### Search Agent Memory

Search an agent's memory for relevant information:

```bash
# Request
curl -X POST http://localhost:5050/agents/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "query": "What did we discuss about Paris?",
    "limit": 5,
    "use_long_term": true,
    "user_id": 123
  }'

# Response (200 OK)
{
  "query": "What did we discuss about Paris?",
  "agent_id": "my_agent",
  "user_id": 123,
  "results": [
    {
      "text": "User: What is the capital of France?\nAssistant: The capital of France is Paris.",
      "source": "buffer",
      "distance": 0.15,
      "metadata": {
        "timestamp": 1625097600
      }
    }
  ]
}
```

Parameters:
- `query` (required): The search query
- `agent_id`: ID of the agent to search (uses default if omitted)
- `limit`: Maximum number of results to return (default: 5)
- `use_long_term`: Whether to include long-term memory in search (default: true)
- `user_id`: User ID for multi-user support (default: 0)

#### Clear Agent Memory

Clear an agent's memory:

```bash
# Request
curl -X POST http://localhost:5050/agents/memory/clear \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "clear_long_term": false,
    "user_id": 123
  }'

# Response (200 OK)
{
  "message": "Memory cleared successfully",
  "agent_id": "my_agent",
  "user_id": 123
}
```

Parameters:
- `agent_id`: ID of the agent to clear memory for (uses default if omitted)
- `clear_long_term`: Whether to clear long-term memory as well (default: false)
- `user_id`: User ID for multi-user support (default: 0)

### Tools

#### List Tools

List all available tools:

```bash
# Request
curl -X GET http://localhost:5050/tools

# Response (200 OK)
{
  "tools": [
    {
      "name": "calculator",
      "description": "Perform mathematical calculations",
      "parameters": {
        "expression": {
          "type": "string",
          "description": "The mathematical expression to evaluate"
        }
      },
      "required_parameters": ["expression"]
    },
    {
      "name": "web_search",
      "description": "Search the web for information",
      "parameters": {
        "query": {
          "type": "string",
          "description": "The search query"
        },
        "num_results": {
          "type": "integer",
          "description": "Number of results to return"
        }
      },
      "required_parameters": ["query"]
    }
  ]
}
```

#### Get Tool Information

Get information about a specific tool:

```bash
# Request
curl -X GET http://localhost:5050/tools/calculator

# Response (200 OK)
{
  "name": "calculator",
  "description": "Perform mathematical calculations",
  "parameters": {
    "expression": {
      "type": "string",
      "description": "The mathematical expression to evaluate"
    }
  },
  "required_parameters": ["expression"]
}
```

#### Register a Tool

Register a new tool:

```bash
# Request
curl -X POST http://localhost:5050/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather",
    "class_path": "src.tools.weather.WeatherTool",
    "config": {
      "api_key": "your_weather_api_key"
    }
  }'

# Response (201 Created)
{
  "status": "success",
  "message": "Tool 'weather' registered successfully"
}
```

#### Update Tool Configuration

Update a tool's configuration:

```bash
# Request
curl -X PATCH http://localhost:5050/tools/weather \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "api_key": "new_weather_api_key"
    }
  }'

# Response (200 OK)
{
  "status": "success",
  "message": "Tool 'weather' updated successfully"
}
```

#### Unregister a Tool

Remove a tool from the registry:

```bash
# Request
curl -X DELETE http://localhost:5050/tools/weather

# Response (200 OK)
{
  "status": "success",
  "message": "Tool 'weather' unregistered successfully"
}
```

### System Management

#### Get System Status

Retrieve system status information:

```bash
# Request
curl -X GET http://localhost:5050/system/status

# Response (200 OK)
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "memory_usage_mb": 156.4,
  "active_connections": 3,
  "agent_count": 2
}
```

#### Get Resource Usage

Get resource usage statistics:

```bash
# Request
curl -X GET http://localhost:5050/system/resources

# Response (200 OK)
{
  "cpu_percent": 12.5,
  "memory_percent": 23.7,
  "memory_used_mb": 156.4,
  "total_memory_mb": 8192,
  "disk_percent": 45.2,
  "agents": {
    "research_assistant": {
      "requests_processed": 42,
      "average_latency_ms": 980.5,
      "token_usage": {
        "prompt": 12500,
        "completion": 4350,
        "total": 16850
      }
    },
    "coding_assistant": {
      "requests_processed": 17,
      "average_latency_ms": 1120.8,
      "token_usage": {
        "prompt": 8700,
        "completion": 3200,
        "total": 11900
      }
    }
  }
}
```

## Multi-User Support

The AI Agent Framework supports multi-user operations through the `user_id` parameter. This allows for:

1. **User-specific memory contexts**: Each user gets their own memory space
2. **Personalized conversations**: Agents can remember information specific to each user
3. **Privacy boundaries**: User memories are isolated from each other

### Creating a Multi-User Agent

```bash
curl -X POST http://localhost:5050/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "system_message": "You are a helpful assistant that remembers information about different users.",
    "use_long_term_memory": true,
    "multi_user_support": true
  }'
```

### Interacting with a Multi-User Agent

```bash
# User 123 introduces themselves
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "message": "My name is Alice and I live in New York.",
    "user_id": 123
  }'

# User 456 introduces themselves
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "message": "My name is Bob and I live in London.",
    "user_id": 456
  }'

# User 123 asks a question (agent remembers it's Alice)
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "message": "Where do I live?",
    "user_id": 123
  }'
# Response will mention New York

# User 456 asks the same question (agent remembers it's Bob)
curl -X POST http://localhost:5050/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "message": "Where do I live?",
    "user_id": 456
  }'
# Response will mention London
```

### Searching User-Specific Memory

```bash
# Search Alice's memories
curl -X POST http://localhost:5050/agents/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "query": "Where does the user live?",
    "user_id": 123
  }'
# Results will include information about New York

# Search Bob's memories
curl -X POST http://localhost:5050/agents/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "query": "Where does the user live?",
    "user_id": 456
  }'
# Results will include information about London
```

### Clearing User-Specific Memory

```bash
# Clear Alice's buffer memory
curl -X POST http://localhost:5050/agents/memory/clear \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "user_id": 123,
    "clear_long_term": false
  }'

# Clear Bob's entire memory (buffer and long-term)
curl -X POST http://localhost:5050/agents/memory/clear \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "user_id": 456,
    "clear_long_term": true
  }'

# Clear default user memory
curl -X POST http://localhost:5050/agents/memory/clear \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "multi_user_agent",
    "clear_long_term": false
  }'
```

## Advanced API Usage

### Error Handling

The API uses standard HTTP status codes:

- **200 OK**: The request was successful
- **201 Created**: The resource was created successfully
- **400 Bad Request**: The request was invalid
- **401 Unauthorized**: Authentication is required
- **404 Not Found**: The requested resource was not found
- **500 Internal Server Error**: An error occurred on the server

Error responses include detailed information:

```json
{
  "error": true,
  "message": "Agent not found",
  "detail": "No agent with ID 'unknown_agent' exists",
  "status_code": 404
}
```

### Pagination

For endpoints that return multiple items, pagination is supported:

```bash
# Request with pagination
curl -X GET "http://localhost:5050/agents?page=2&limit=10"

# Response (200 OK)
{
  "agents": [
    ...
  ],
  "pagination": {
    "page": 2,
    "limit": 10,
    "total_items": 35,
    "total_pages": 4
  }
}
```

### Filtering

Some endpoints support filtering:

```bash
# Filter agents by tool
curl -X GET "http://localhost:5050/agents?tool=web_search"

# Response (200 OK)
{
  "agents": [
    {
      "agent_id": "research_assistant",
      "tools": ["web_search", "calculator"],
      "is_default": true
    },
    // Other agents with web_search tool
  ]
}
```

### Rate Limiting

The API includes rate limiting to prevent abuse:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1623763200

{
  "error": true,
  "message": "Rate limit exceeded",
  "detail": "Too many requests. Please try again in 30 seconds.",
  "status_code": 429
}
```

## API Client Examples

### Python Client

```python
import requests
import json

class AIAgentClient:
    def __init__(self, base_url="http://localhost:5050", api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def list_agents(self):
        """List all agents."""
        response = requests.get(f"{self.base_url}/agents", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_agent(self, agent_id, system_message=None, tools=None, set_as_default=False):
        """Create a new agent."""
        payload = {
            "agent_id": agent_id,
            "system_message": system_message or "You are a helpful assistant.",
            "tools": tools or [],
            "set_as_default": set_as_default
        }
        response = requests.post(
            f"{self.base_url}/agents",
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()

    def chat(self, message, agent_id=None):
        """Send a message to an agent."""
        payload = {"message": message}
        if agent_id:
            payload["agent_id"] = agent_id

        response = requests.post(
            f"{self.base_url}/agents/chat",
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()

    def search_memory(self, query, agent_id, top_k=5):
        """Search an agent's memory."""
        payload = {
            "agent_id": agent_id,
            "query": query,
            "top_k": top_k
        }
        response = requests.post(
            f"{self.base_url}/agents/memory/search",
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()

    def clear_memory(self, agent_id, user_id=0, clear_long_term=False):
        """Clear an agent's memory."""
        payload = {
            "agent_id": agent_id,
            "user_id": user_id,
            "clear_long_term": clear_long_term
        }
        response = requests.post(
            f"{self.base_url}/agents/memory/clear",
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """List all available tools."""
        response = requests.get(f"{self.base_url}/tools", headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
client = AIAgentClient()

# Create an agent
client.create_agent(
    agent_id="assistant",
    system_message="You are a helpful assistant specializing in Python programming.",
    tools=["calculator", "web_search"],
    set_as_default=True
)

# Chat with the agent
response = client.chat("How do I sort a list in Python?")
print(f"Agent: {response['message']}")

# Search memory
results = client.search_memory("Python list methods", agent_id="assistant")
for result in results["results"]:
    print(f"Score: {result['score']}, Text: {result['text']}")
```

### JavaScript Client

```javascript
class AIAgentClient {
    constructor(baseUrl = 'http://localhost:5050', apiKey = null) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json'
        };

        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }

    async listAgents() {
        const response = await fetch(`${this.baseUrl}/agents`, {
            method: 'GET',
            headers: this.headers
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    async createAgent(agentId, systemMessage = null, tools = null, setAsDefault = false) {
        const payload = {
            agent_id: agentId,
            system_message: systemMessage || 'You are a helpful assistant.',
            tools: tools || [],
            set_as_default: setAsDefault
        };

        const response = await fetch(`${this.baseUrl}/agents`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    async chat(message, agentId = null) {
        const payload = { message };

        if (agentId) {
            payload.agent_id = agentId;
        }

        const response = await fetch(`${this.baseUrl}/agents/chat`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    async streamChat(message, agentId = null, onChunk = null) {
        const payload = { message };

        if (agentId) {
            payload.agent_id = agentId;
        }

        const response = await fetch(`${this.baseUrl}/agents/chat/stream`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let result = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(value, { stream: true });

            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    result += data.chunk;

                    if (onChunk) {
                        onChunk(data.chunk, data.done);
                    }

                    if (data.done) {
                        return result;
                    }
                }
            }
        }

        return result;
    }

    async searchMemory(query, agentId, topK = 5) {
        const payload = {
            agent_id: agentId,
            query: query,
            top_k: topK
        };

        const response = await fetch(`${this.baseUrl}/agents/memory/search`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    async clearMemory(agentId, userId = 0, clearLongTerm = false) {
        const payload = {
            agent_id: agentId,
            user_id: userId,
            clear_long_term: clearLongTerm
        };

        const response = await fetch(`${this.baseUrl}/agents/memory/clear`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    async listTools() {
        const response = await fetch(`${this.baseUrl}/tools`, {
            method: 'GET',
            headers: this.headers
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }
}

// Usage
const client = new AIAgentClient();

async function demo() {
    try {
        // Create an agent
        await client.createAgent(
            'web_assistant',
            'You are a helpful assistant specializing in web development.',
            ['calculator', 'web_search'],
            true
        );

        // Chat with the agent
        const response = await client.chat('What is React.js?');
        console.log(`Agent: ${response.message}`);

        // Stream chat
        console.log('Streaming response:');
        await client.streamChat(
            'Explain the difference between React and Angular',
            null,
            (chunk, done) => {
                process.stdout.write(chunk);
                if (done) process.stdout.write('\n');
            }
        );

        // Search memory
        const results = await client.searchMemory('JavaScript frameworks', 'web_assistant');
        for (const result of results.results) {
            console.log(`Score: ${result.score}, Text: ${result.text}`);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

demo();
```

## API Versioning

The API uses versioning to ensure backward compatibility. The current version is accessible at the base URL, and specific versions can be accessed with a version prefix:

```bash
# Current version
curl -X GET http://localhost:5050/agents

# Specific version
curl -X GET http://localhost:5050/v1/agents
```

## Best Practices

1. **Rate Limiting**: Implement client-side throttling to avoid hitting rate limits

2. **Error Handling**: Handle API errors gracefully in your application

3. **Authentication**: Always use authentication in production environments

4. **Pagination**: Use pagination for endpoints that return multiple items

5. **Streaming**: Prefer streaming endpoints for long-running agent responses

6. **Caching**: Implement caching for frequently accessed resources

7. **Status Monitoring**: Regularly check the system status endpoint

## Troubleshooting

### Common Error Codes

- **400 Bad Request**: Check the request format and parameters
- **401 Unauthorized**: Verify your API key and authentication headers
- **404 Not Found**: Ensure the requested resource exists
- **429 Too Many Requests**: Implement request throttling
- **500 Internal Server Error**: Check the server logs for details

### API Server Logs

To view detailed logs from the API server:

```bash
# Set the log level to DEBUG
export LOG_LEVEL=DEBUG

# Start the server
python -m src.api.run

# View logs in real-time
tail -f logs/api.log
```

## Next Steps

After understanding the REST API, you might want to explore:

- Setting up [WebSocket connections](./websocket.md) for real-time communication
- Creating custom [agents](./agent.md) via the API
- Implementing [tools](./tools.md) and registering them via the API
- Exploring [MCP features](./mcp.md) for advanced message handling
