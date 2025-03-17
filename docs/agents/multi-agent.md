---
layout: default
title: Multi-Agent Systems
parent: Building Agents
nav_order: 2
permalink: /agents/multi-agent/
---

# Multi-Agent Systems

This guide explores how to create multi-agent systems with the MUXI Framework, where multiple specialized agents work together to handle complex tasks.

## Why Use Multiple Agents?

Multi-agent systems offer several advantages:

- **Specialization**: Create agents with different expertise and capabilities
- **Division of Labor**: Distribute complex tasks among specialized agents
- **Scalability**: Handle more requests by distributing them across agents
- **Redundancy**: Provide fallback options if one agent cannot handle a task

## Setting Up a Multi-Agent System

### Basic Multi-Agent Setup

The Orchestrator class makes it easy to create and manage multiple agents:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create models for different agents
general_model = OpenAIModel(model="gpt-3.5-turbo")
expert_model = OpenAIModel(model="gpt-4o")

# Create a general assistant
orchestrator.create_agent(
    agent_id="general_assistant",
    model=general_model,
    system_message="You are a helpful assistant that can answer general questions."
)

# Create a coding assistant
orchestrator.create_agent(
    agent_id="code_assistant",
    model=expert_model,
    system_message="""You are a specialized coding assistant with expertise in Python,
    JavaScript, and other popular languages. Provide code examples and explanations."""
)

# Create a data science assistant
orchestrator.create_agent(
    agent_id="data_science_assistant",
    model=expert_model,
    system_message="""You are a specialized data science assistant with expertise in
    statistics, machine learning, and data analysis. Provide detailed technical advice."""
)
```

## Intelligent Message Routing

MUXI provides intelligent routing to direct messages to the most appropriate agent based on content:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

# Initialize the orchestrator with routing enabled
orchestrator = Orchestrator(enable_routing=True)

# Create specialized agents
orchestrator.create_agent(
    agent_id="general",
    model=OpenAIModel(model="gpt-3.5-turbo"),
    system_message="You are a helpful assistant for general questions.",
    description="Handles general questions about various topics."
)

orchestrator.create_agent(
    agent_id="coding",
    model=OpenAIModel(model="gpt-4o"),
    system_message="You are a coding expert who provides programming help.",
    description="Specialized in programming, software development, and technical questions."
)

orchestrator.create_agent(
    agent_id="creative",
    model=OpenAIModel(model="gpt-4o"),
    system_message="You are a creative assistant who helps with writing and artistic tasks.",
    description="Specialized in creative writing, storytelling, and artistic generation."
)

# The orchestrator will automatically route the message to the most appropriate agent
response = orchestrator.chat(message="How do I implement binary search in Python?")
print(f"Response (likely from coding agent): {response}")

response = orchestrator.chat(message="Tell me about the history of Rome.")
print(f"Response (likely from general agent): {response}")

response = orchestrator.chat(message="Write a short poem about autumn.")
print(f"Response (likely from creative agent): {response}")
```

## Routing Configuration

You can customize the routing behavior:

```python
# Configure routing with custom settings
orchestrator = Orchestrator(
    enable_routing=True,
    routing_model=OpenAIModel(model="gpt-4o"),  # Use a specific model for routing decisions
    routing_temperature=0.2,                     # Lower temperature for more deterministic routing
    default_agent_id="general"                   # Default agent if routing is uncertain
)
```

## Manual Agent Selection

You can also manually select which agent handles a message:

```python
# Chat with specific agents
response = orchestrator.chat("coding", "Write a function to calculate Fibonacci numbers.")
print(f"Coding Agent: {response}")

response = orchestrator.chat("creative", "Write a haiku about programming.")
print(f"Creative Agent: {response}")
```

## Agent Collaboration

You can implement collaboration between agents by passing information between them:

```python
# Example of agents collaborating on a complex task
coding_response = orchestrator.chat(
    "coding",
    "Create a Python script to analyze text sentiment."
)

data_science_response = orchestrator.chat(
    "data_science_assistant",
    f"Review this code for sentiment analysis and suggest improvements: {coding_response}"
)

final_response = orchestrator.chat(
    "coding",
    f"Update the code based on these suggestions: {data_science_response}"
)

print("Final solution after collaboration:")
print(final_response)
```

## Creating a Team of Agents from Configuration

You can define a team of agents using configuration:

```python
from muxi.core.orchestrator import Orchestrator

# Initialize the orchestrator
orchestrator = Orchestrator(enable_routing=True)

# Team configuration
team_config = {
    "agents": [
        {
            "agent_id": "researcher",
            "model": {
                "provider": "openai",
                "model": "gpt-4o"
            },
            "system_message": "You are a research assistant specialized in finding and summarizing information.",
            "description": "Specialized in research, information gathering, and summarization."
        },
        {
            "agent_id": "writer",
            "model": {
                "provider": "openai",
                "model": "gpt-4o"
            },
            "system_message": "You are a writing assistant specialized in creating well-structured content.",
            "description": "Specialized in writing, editing, and content creation."
        },
        {
            "agent_id": "critic",
            "model": {
                "provider": "openai",
                "model": "gpt-4o"
            },
            "system_message": "You are a critical reviewer who analyzes content for accuracy and quality.",
            "description": "Specialized in review, critique, and quality assessment."
        }
    ],
    "routing": {
        "default_agent_id": "researcher"
    }
}

# Create agents from configuration
for agent_config in team_config["agents"]:
    orchestrator.create_agent_from_config(agent_config)

# Set default agent if specified
if "routing" in team_config and "default_agent_id" in team_config["routing"]:
    orchestrator.default_agent_id = team_config["routing"]["default_agent_id"]
```

## Real-World Example: Research and Writing Pipeline

Here's a practical example of a multi-agent system for research and content creation:

```python
# Step 1: Research phase with the researcher agent
research_query = "What are the latest advances in quantum computing?"
research_results = orchestrator.chat("researcher", research_query)

# Step 2: Content creation with the writer agent
writing_prompt = f"Create an article about quantum computing based on this research: {research_results}"
draft_content = orchestrator.chat("writer", writing_prompt)

# Step 3: Review and improvement with the critic agent
review_prompt = f"Review this article for accuracy and clarity: {draft_content}"
review_feedback = orchestrator.chat("critic", review_prompt)

# Step 4: Final revision with the writer agent
revision_prompt = f"Revise the article based on this feedback: {review_feedback}"
final_content = orchestrator.chat("writer", revision_prompt)

print("Final Article:")
print(final_content)
```

## Advanced: Custom Routing Logic

You can implement custom routing logic for specialized needs:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel

class CustomOrchestrator(Orchestrator):
    def route_message(self, message, user_id=None):
        """Custom routing logic based on message content and patterns"""

        # Programming-related messages go to the coding agent
        if any(keyword in message.lower() for keyword in ["code", "programming", "function", "bug"]):
            return "coding"

        # Creative tasks go to the creative agent
        if any(keyword in message.lower() for keyword in ["write", "story", "poem", "creative"]):
            return "creative"

        # Data analysis goes to the data science agent
        if any(keyword in message.lower() for keyword in ["data", "analysis", "statistics", "graph"]):
            return "data_science"

        # Default to general assistant
        return "general"

# Use the custom orchestrator
custom_orchestrator = CustomOrchestrator()
```

## Best Practices for Multi-Agent Systems

1. **Clear Specialization**: Define clear roles and expertise for each agent
2. **Consistent System Messages**: Make system messages detailed and non-overlapping
3. **Appropriate Model Selection**: Use more powerful models for complex tasks
4. **Memory Management**: Consider whether agents should share memory or maintain separate contexts
5. **Error Handling**: Implement fallback mechanisms if routing fails
6. **Observability**: Add logging to track which agent handles which messages

## Next Steps

Now that you've set up a multi-agent system, you might want to:

- Add memory to your agents - see [Adding Memory](../memory/)
- Configure your agents with specific tools - see [Agent Configuration](../configuration/)
- Explore how to connect your agents to external services - see [Using MCP Servers](../../extend/using-mcp/)
