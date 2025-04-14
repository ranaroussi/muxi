# Memory Migration Plan: Agent to Orchestrator Level

## Overview

This document outlines the plan to move memory management from the Agent level to the Orchestrator level in the MUXI Framework. This architectural change will:

- Centralize memory management
- Prevent inconsistent database configurations between agents
- Make memory sharing between agents more efficient
- Simplify the API surface

## Implementation Tasks

### 1. Update Orchestrator Class

1. Modify `Orchestrator.__init__()` to accept memory parameters
   ```python
   def __init__(self, buffer_memory=None, long_term_memory=None):
       # Existing initialization code...
       self.buffer_memory = buffer_memory
       self.long_term_memory = long_term_memory
   ```

2. Update `Orchestrator.create_agent()` to pass a reference to the orchestrator instead of memory objects
   ```python
   def create_agent(
       self,
       agent_id: str,
       model: BaseModel,
       system_message: Optional[str] = None,
       description: Optional[str] = None,
       set_as_default: bool = False,
   ):
       # Create agent with reference to orchestrator for memory access
       agent = Agent(
           model=model,
           orchestrator=self,  # Pass self instead of memory objects
           system_message=system_message,
       )
       # Existing code...
   ```

3. Add methods for memory access that support agent-specific context
   ```python
   def add_to_buffer_memory(self, message, metadata=None, agent_id=None):
       if self.buffer_memory:
           # Add agent_id to metadata for context
           full_metadata = metadata or {}
           if agent_id:
               full_metadata["agent_id"] = agent_id
           return self.buffer_memory.add(message, metadata=full_metadata)
       return None

   async def add_to_long_term_memory(self, content, metadata=None, agent_id=None, user_id=None):
       if self.long_term_memory:
           full_metadata = metadata or {}
           if agent_id:
               full_metadata["agent_id"] = agent_id

           # Handle multi-user case
           if hasattr(self.long_term_memory, "add_user_memory") and user_id is not None:
               return await self.long_term_memory.add_user_memory(content, metadata=full_metadata, user_id=user_id)
           else:
               return await self.long_term_memory.add(content, metadata=full_metadata)
       return None

   async def search_memory(self, query, agent_id=None, k=5, use_long_term=True, user_id=None):
       # Implementation details...
   ```

4. Update memory-related orchestrator methods to use the centralized memory
   ```python
   def clear_all_memories(self, clear_long_term=False):
       # Clear centralized memory instead of per-agent memory
       if self.buffer_memory:
           self.buffer_memory.clear()

       if clear_long_term and self.long_term_memory:
           # Clear long-term memory based on its type
           # Implementation details...
   ```

### 2. Update Agent Class

1. Modify `Agent.__init__()` to store a reference to the orchestrator
   ```python
   def __init__(
       self,
       model: BaseModel,
       orchestrator=None,  # New parameter
       system_message: Optional[str] = None,
       name: Optional[str] = None,
       agent_id: Optional[str] = None,
       knowledge: Optional[List[KnowledgeSource]] = None,
       # Remove buffer_memory and long_term_memory parameters
   ):
       self.model = model
       self.name = name or "AI Assistant"
       self.agent_id = agent_id or get_default_nanoid()
       self.orchestrator = orchestrator  # Store reference to orchestrator
       # Rest of existing initialization...
   ```

2. Update all memory access methods in the Agent to use the orchestrator's memory
   ```python
   async def _store_in_memory(self, input_text: str, response_text: str) -> None:
       if not self.orchestrator:
           return

       # Get embedding
       embedding = await self.model.embed(f"User: {input_text}\nAssistant: {response_text}")

       # Store in orchestrator's buffer memory
       self.orchestrator.add_to_buffer_memory(
           message=embedding,
           metadata={
               "input": input_text,
               "response": response_text,
               "type": "conversation",
           },
           agent_id=self.agent_id
       )

       # Store in orchestrator's long-term memory
       await self.orchestrator.add_to_long_term_memory(
           content=f"User: {input_text}\nAssistant: {response_text}",
           metadata={
               "input": input_text,
               "response": response_text,
               "type": "conversation",
           },
           agent_id=self.agent_id
       )
   ```

3. Update other memory-related methods (clear_memory, search_memory, etc.)

### 3. Update Muxi Facade

1. Modify `Muxi.__init__()` to accept memory parameters
   ```python
   def __init__(self, buffer_memory=None, long_term_memory=None, db_connection_string=None):
       # Create memory objects if specified as integers or strings
       _buffer_memory = self._create_buffer_memory(buffer_memory)
       _long_term_memory = self._create_long_term_memory(long_term_memory)

       # Initialize the orchestrator with memory components
       self.orchestrator = Orchestrator(
           buffer_memory=_buffer_memory,
           long_term_memory=_long_term_memory
       )

       # Rest of existing initialization...
   ```

2. Add helper methods to create memory objects
   ```python
   def _create_buffer_memory(self, buffer_config):
       if buffer_config is None:
           return None
       if isinstance(buffer_config, int):
           return BufferMemory(buffer_size=buffer_config)
       return buffer_config  # Assume it's already a BufferMemory instance

   def _create_long_term_memory(self, long_term_config):
       # Implementation for parsing connection strings, creating SQLite/Postgres memory, etc.
       # Similar to existing code in _create_memory_systems()
   ```

3. Update the `add_agent` method to not include buffer_memory and long_term_memory in agent creation

### 4. API Compatibility Updates

1. Create compatibility layer for existing code that expects agents to have memory
   ```python
   # In Agent class:
   @property
   def buffer_memory(self):
       """Compatibility property that returns orchestrator's buffer memory."""
       if self.orchestrator:
           return self.orchestrator.buffer_memory
       return None

   @property
   def long_term_memory(self):
       """Compatibility property that returns orchestrator's long-term memory."""
       if self.orchestrator:
           return self.orchestrator.long_term_memory
       return None
   ```

2. Ensure all memory-related methods on Agent proxy to orchestrator correctly

### 5. Tests and Documentation

1. Update tests to use the new memory architecture
2. Update documentation to reflect the changes
3. Create migration guide for users of the framework

## Implementation Strategy

We'll implement the changes in the following order:

1. Add memory to Orchestrator without removing from Agent
2. Update Agent to use Orchestrator's memory when available
3. Update Muxi facade to initialize Orchestrator with memory
4. Add compatibility layer for existing code
5. Update tests and documentation
6. Remove memory parameters from Agent (with deprecation warnings)

This approach will allow for a gradual transition and maintain backward compatibility.

## Example Usage

### Declarative Method (Muxi Facade)

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI with orchestrator-level memory
app = muxi(
    buffer_memory=10,
    long_term_memory="postgresql://user:password@localhost:5432/muxi"
)

# Add agent from configuration
app.add_agent("configs/buffer_memory_agent.json")

# The agent will use the orchestrator's memory
response1 = await app.chat("assistant", "My name is Alice.")
print(response1)  # The agent acknowledges and remembers the name

response2 = await app.chat("assistant", "What's my name?")
print(response2)  # The agent should respond with "Alice"
```

### Programmatic Method

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory

# Create memory components
buffer = BufferMemory(15)
long_term_memory = LongTermMemory(connection_string="sqlite:///data/memory.db")

# Initialize orchestrator with memory
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=long_term_memory
)

# Create model
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)

# Create an agent that uses the orchestrator's memory
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant with both short-term and long-term memory capabilities.",
    model=model
)

# The agent will use the orchestrator's memory
orchestrator.chat("assistant", "Remember that my favorite color is blue.")
```
