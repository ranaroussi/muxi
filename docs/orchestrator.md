# Orchestrator

The Orchestrator is a central component of the AI Agent Framework responsible for managing multiple agents and coordinating their interactions. It serves as the control center for agent creation, access, and communication.

## What is the Orchestrator?

The Orchestrator:
- Creates and manages multiple agents
- Routes messages to the appropriate agents
- Facilitates communication between agents
- Maintains a registry of available agents
- Controls access to shared resources

## Using the Orchestrator

### Initialization

The Orchestrator can be initialized as a standalone component:

```python
from src.core.orchestrator import Orchestrator

# Create a new orchestrator
orchestrator = Orchestrator()
```

### Creating Agents

The primary function of the Orchestrator is to create and manage agents:

```python
from src.models import OpenAIModel
from src.memory.buffer import BufferMemory
from src.tools.web_search import WebSearchTool

# Create an agent with the orchestrator
orchestrator.create_agent(
    agent_id="research_agent",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    tools=[WebSearchTool()],
    system_message="You are a research assistant specialized in finding and summarizing information.",
    set_as_default=True
)

# Create another agent
orchestrator.create_agent(
    agent_id="coding_agent",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    tools=[],
    system_message="You are a coding assistant specialized in Python programming.",
)
```

### Interacting with Agents

You can interact with agents through the Orchestrator:

```python
# Send a message to a specific agent
response = await orchestrator.run(
    agent_id="research_agent",
    message="What are the latest developments in quantum computing?"
)
print(response)

# Send a message to the default agent
response = await orchestrator.run(
    message="Explain the concept of quantum entanglement"
)
print(response)
```

### Managing Agents

The Orchestrator provides methods to manage the agent lifecycle:

```python
# Get a list of all agents
agents = orchestrator.list_agents()
print(f"Available agents: {agents}")

# Check if an agent exists
if orchestrator.has_agent("research_agent"):
    print("Research agent exists")

# Get a reference to an agent
agent = orchestrator.get_agent("research_agent")

# Delete an agent
orchestrator.delete_agent("coding_agent")

# Set a different default agent
orchestrator.set_default_agent("research_agent")
```

## Multi-Agent Collaboration

One of the powerful features of the Orchestrator is enabling collaboration between multiple agents:

### Sequential Agent Collaboration

```python
# Research agent finds information
research_response = await orchestrator.run(
    agent_id="research_agent",
    message="Find information about climate change mitigation strategies"
)

# Analysis agent analyzes the information
analysis_response = await orchestrator.run(
    agent_id="analysis_agent",
    message=f"Analyze this information and identify the most promising strategies: {research_response}"
)

# Summary agent creates a final summary
summary_response = await orchestrator.run(
    agent_id="summary_agent",
    message=f"Create a concise summary of these strategies: {analysis_response}"
)

print(summary_response)
```

### Agent Communication

Agents can indirectly communicate through the Orchestrator:

```python
# Define a collaboration protocol
async def agent_collaboration():
    # First agent generates ideas
    ideas = await orchestrator.run(
        agent_id="brainstorm_agent",
        message="Generate 5 innovative solutions for reducing urban traffic congestion"
    )

    # Second agent evaluates the ideas
    evaluation = await orchestrator.run(
        agent_id="critic_agent",
        message=f"Critically evaluate these solutions, ranking them from most to least promising: {ideas}"
    )

    # Third agent synthesizes a comprehensive plan
    plan = await orchestrator.run(
        agent_id="synthesis_agent",
        message=f"Based on these evaluations, create a detailed implementation plan for the top 2 solutions: {evaluation}"
    )

    return plan

# Execute the collaboration
plan = await agent_collaboration()
print(plan)
```

## Advanced Features

### Dynamic Agent Creation

You can dynamically create specialized agents based on user requests:

```python
async def get_specialized_agent(domain):
    # Check if a specialized agent exists
    agent_id = f"{domain}_specialist"

    if not orchestrator.has_agent(agent_id):
        # Create a new specialized agent
        system_message = f"You are an expert in {domain}. Provide detailed, accurate information about {domain} topics."

        orchestrator.create_agent(
            agent_id=agent_id,
            model=OpenAIModel(model="gpt-4o"),
            buffer_memory=BufferMemory(),
            system_message=system_message
        )

    return agent_id

# Use the function to get or create a specialized agent
physics_agent_id = await get_specialized_agent("physics")
response = await orchestrator.run(
    agent_id=physics_agent_id,
    message="Explain quantum field theory in simple terms"
)
print(response)
```

### Agent Teams

You can organize agents into teams for complex tasks:

```python
class AgentTeam:
    def __init__(self, orchestrator, team_name, agent_ids):
        self.orchestrator = orchestrator
        self.team_name = team_name
        self.agent_ids = agent_ids

    async def run_team_task(self, task, coordinator_id=None):
        results = {}

        # Distribute the task to each team member
        for agent_id in self.agent_ids:
            results[agent_id] = await self.orchestrator.run(
                agent_id=agent_id,
                message=f"Task for {agent_id}: {task}"
            )

        # If a coordinator is specified, have them synthesize the results
        if coordinator_id:
            synthesis_message = f"Synthesize the following team outputs for task '{task}':\n\n"
            for agent_id, result in results.items():
                synthesis_message += f"=== {agent_id} ===\n{result}\n\n"

            final_result = await self.orchestrator.run(
                agent_id=coordinator_id,
                message=synthesis_message
            )
            return final_result

        return results

# Create a research team
research_team = AgentTeam(
    orchestrator=orchestrator,
    team_name="Research Team",
    agent_ids=["data_collector", "analyst", "writer"]
)

# Run a team task
result = await research_team.run_team_task(
    task="Research the impact of artificial intelligence on healthcare",
    coordinator_id="research_director"
)
print(result)
```

## Persistence and State Management

The Orchestrator can persist agent states to allow for long-running operations:

```python
import json
import os

class PersistentOrchestrator(Orchestrator):
    def __init__(self, state_file="orchestrator_state.json"):
        super().__init__()
        self.state_file = state_file
        self.load_state()

    def save_state(self):
        state = {
            "agents": list(self.agents.keys()),
            "default_agent": self.default_agent
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

    def load_state(self):
        if not os.path.exists(self.state_file):
            return

        with open(self.state_file, "r") as f:
            state = json.load(f)

        # Recreate agents (simplified - in practice you'd need to store and restore more state)
        for agent_id in state.get("agents", []):
            if agent_id not in self.agents:
                self.create_agent(agent_id=agent_id)

        # Restore default agent
        if state.get("default_agent"):
            self.default_agent = state["default_agent"]

    def create_agent(self, agent_id, **kwargs):
        super().create_agent(agent_id, **kwargs)
        self.save_state()

    def delete_agent(self, agent_id):
        super().delete_agent(agent_id)
        self.save_state()

    def set_default_agent(self, agent_id):
        super().set_default_agent(agent_id)
        self.save_state()

# Use the persistent orchestrator
persistent_orchestrator = PersistentOrchestrator()
```

## Best Practices

1. **Agent Management**: Create agents with clear, distinct roles and responsibilities

2. **Resource Allocation**: Be mindful of resource usage when running multiple agents simultaneously

3. **Error Handling**: Implement robust error handling to prevent failures in one agent from affecting others

4. **State Management**: Consider implementing persistence for important agent states

5. **Security**: Implement appropriate access controls if multiple users are interacting with different agents

## Troubleshooting

### Agent Creation Issues

- Ensure all required parameters are provided
- Check for duplicate agent IDs
- Verify that the LLM provider is properly configured

### Communication Issues

- Ensure messages are being routed to the correct agent
- Check for rate limiting or quota issues with LLM providers
- Verify that shared resources (e.g., memory) are accessible

### Performance Issues

- Consider using a thread pool for parallel agent execution
- Implement caching for frequently requested information
- Monitor resource usage and scale accordingly

## Next Steps

After setting up your Orchestrator and agents, you might want to explore:

- Implementing [custom tools](./tools.md) for specialized agent capabilities
- Setting up [memory systems](./memory.md) for improved agent recall
- Creating a [WebSocket connection](./websocket.md) for real-time agent interaction
- Exploring [MCP features](./mcp.md) for advanced LLM control
