---
layout: default
title: MCP Servers
parent: Core Concepts
has_children: false
nav_order: 5
permalink: /mcp-servers/
---
# MCP Servers

MCP Servers extend the capabilities of AI agents by enabling them to perform specific actions or retrieve information beyond their training data through the Model Context Protocol (MCP).

## What are MCP Servers?

MCP Servers are specialized services that agents can use to:
- Access external data sources and APIs
- Perform calculations
- Execute code
- Interact with databases
- Manipulate files and documents

## Understanding the Model Context Protocol (MCP)

The Model Context Protocol (MCP) is the standardized communication protocol that enables LLMs to request external service execution and receive results.

### MCP Servers vs Direct Integration

MCP provides several advantages over direct integration:

- **Separation of Concerns**: MCP servers can run independently from your main application
- **Language Agnostic**: Implement MCP servers in any programming language
- **Versioning**: Update MCP servers without changing the core framework
- **Security**: Control access to sensitive operations through dedicated servers
- **Scalability**: Scale computational resources for specific services independently

### How MCP Works

When an MCP server is used in the MUXI framework, the process follows this flow:

1. The LLM decides an external service is needed to answer a query
2. The LLM sends an MCP request formatted according to the MCP standard
3. The MCP client routes the request to the appropriate MCP server
4. The MCP server executes the requested operation in its environment
5. The results are formatted as an MCP response and returned to the LLM

## Built-in MCP Servers

The framework includes several built-in MCP server integrations that provide common functionality.

### Calculator Service

The Calculator service allows agents to evaluate mathematical expressions.

```python
from muxi.core.mcp import MCPClient

# Create an MCP client connected to the calculator service
calculator = MCPClient(endpoint="http://localhost:5003/calculator")

# Execute the service
response = await calculator.execute(
    method="calculate",
    params={"expression": "2 + 2 * 3"}
)
print(f"Result: {response['result']}")  # Result: 8
```

### Web Search Service

The Web Search service enables agents to search the internet for information.

```python
from muxi.core.mcp import MCPClient

# Create an MCP client connected to the web search service
search = MCPClient(endpoint="http://localhost:5003/web-search")

# Execute the service
response = await search.execute(
    method="search",
    params={"query": "latest AI developments", "num_results": 5}
)
for result in response["results"]:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}\n")
```

### File Operations Service

The File Operations service provides capabilities for reading and writing files.

```python
from muxi.core.mcp import MCPClient

# Create an MCP client connected to the file operations service
file_ops = MCPClient(endpoint="http://localhost:5003/file-operations")

# Read a file
response = await file_ops.execute(
    method="read_file",
    params={"path": "data/config.json"}
)
print(f"File contents: {response['content']}")

# Write to a file
response = await file_ops.execute(
    method="write_file",
    params={
        "path": "data/output.txt",
        "content": "Hello, world!",
        "mode": "w"
    }
)
print(f"Success: {response['success']}")
```

## Creating Custom MCP Servers

You can create custom MCP servers to extend the capabilities of your agents. Here's how to build a basic MCP server:

### MCP Server Base Structure

An MCP server typically includes these components:

1. API endpoints for handling MCP requests
2. Service logic for executing operations
3. Response formatting according to MCP standards

Here's a basic example using FastAPI:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class MCPRequest(BaseModel):
    method: str
    params: dict

class MCPResponse(BaseModel):
    result: dict
    error: str = None

@app.post("/weather", response_model=MCPResponse)
async def weather_endpoint(request: MCPRequest):
    try:
        if request.method == "get_weather":
            location = request.params.get("location")
            if not location:
                return {"error": "Location parameter is required"}

            weather_data = get_weather_data(location)
            return {"result": weather_data}
        else:
            return {"error": f"Unknown method: {request.method}"}
    except Exception as e:
        return {"error": str(e)}

def get_weather_data(location):
    # Implementation of weather data retrieval
    api_key = "your_weather_api_key"
    response = requests.get(
        f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    )
    data = response.json()

    return {
        "location": data["location"]["name"],
        "country": data["location"]["country"],
        "temperature": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"],
        "humidity": data["current"]["humidity"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
```

### Example: Database MCP Server

Here's an example of an MCP server that allows agents to run SQL queries against a database:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import create_engine, text
import os

app = FastAPI()

# Database connection
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")
engine = create_engine(DB_URL)

class MCPRequest(BaseModel):
    method: str
    params: dict

class MCPResponse(BaseModel):
    result: dict = None
    error: str = None

@app.post("/database", response_model=MCPResponse)
async def database_endpoint(request: MCPRequest):
    try:
        if request.method == "query":
            query = request.params.get("query")
            if not query:
                return {"error": "Query parameter is required"}

            # Security: validate query to prevent SQL injection
            if not is_safe_query(query):
                return {"error": "Query contains unsafe operations"}

            results = execute_query(query)
            return {"result": {"rows": results}}
        else:
            return {"error": f"Unknown method: {request.method}"}
    except Exception as e:
        return {"error": str(e)}

def is_safe_query(query):
    # Implement security checks here
    # This is a simplified example - implement proper SQL validation in production
    unsafe_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
    return not any(keyword in query.upper() for keyword in unsafe_keywords)

def execute_query(query):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        if result.returns_rows:
            columns = result.keys()
            rows = []
            for row in result:
                rows.append(dict(zip(columns, row)))
            return rows
        return {"affected_rows": result.rowcount}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
```

## Registering MCP Servers with Agents

To make MCP servers available to an agent, they need to be registered when creating the agent:

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.mcp import MCPClient

# Create MCP clients
weather_service = MCPClient(endpoint="http://localhost:5003/weather")
database_service = MCPClient(endpoint="http://localhost:5003/database")

# Create an agent with MCP servers
agent = Agent(
    model=OpenAIModel("gpt-4o"),
    mcp_servers={
        "weather": weather_service,
        "database": database_service
    },
    system_message="You are a helpful assistant with access to external services."
)

# Agent can now use these services when needed
response = await agent.chat("What's the weather like in New York?")
```

## MCP Server Security

When implementing MCP servers, follow these security best practices:

1. **Authentication**: Require API keys or tokens for all MCP server requests
2. **Input Validation**: Thoroughly validate all inputs to prevent injection attacks
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Logging**: Maintain detailed logs of all operations for auditing
5. **Sandboxing**: Run untrusted code in isolated environments
6. **Principle of Least Privilege**: Grant only necessary permissions to each service

## Best Practices for MCP Server Implementation

1. **Service Discovery**: Implement service discovery mechanisms for dynamic server registration
2. **Error Handling**: Provide detailed error messages that help diagnose issues
3. **Versioning**: Support API versioning to maintain backward compatibility
4. **Documentation**: Document all available methods and parameters
5. **Monitoring**: Implement health checks and performance monitoring
6. **Caching**: Cache frequently requested data to improve performance
7. **Graceful Degradation**: Design services to degrade gracefully when dependencies fail

## Next Steps

After implementing MCP servers, you might want to explore:

- Creating more complex services with [multi-step operations](./orchestrator)
- Setting up [WebSocket connections](./websocket) for real-time updates from MCP servers
- Implementing [memory integration](./memory) to store service results for future use
- Developing [agent collaboration](./orchestrator) methods that share service results between agents
