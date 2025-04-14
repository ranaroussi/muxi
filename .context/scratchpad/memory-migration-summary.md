# Memory Migration: From Agent to Orchestrator Level

## Implementation Summary

We've successfully developed a plan and implementation for moving the memory module from the agent level to the orchestrator level in the MUXI Framework. The key files created include:

1. [memory-migration-plan.md](.context/scratchpad/memory-migration-plan.md) - Detailed plan outlining the implementation strategy
2. [orchestrator_memory.py](.context/scratchpad/orchestrator_memory.py) - Updated Orchestrator implementation with centralized memory
3. [agent_memory.py](.context/scratchpad/agent_memory.py) - Updated Agent implementation that uses orchestrator's memory
4. [facade_memory.py](.context/scratchpad/facade_memory.py) - Updated Muxi facade that initializes orchestrator with memory

## Key Changes

### Orchestrator Class

1. Added memory parameters to `__init__`:
   ```python
   def __init__(
       self,
       buffer_memory: Optional[BufferMemory] = None,
       long_term_memory: Optional[Union[LongTermMemory, Memobase]] = None
   ):
       # Existing initialization code...
       self.buffer_memory = buffer_memory
       self.long_term_memory = long_term_memory
   ```

2. Updated `create_agent()` to pass a reference to orchestrator instead of memory objects:
   ```python
   agent = Agent(
       model=model,
       orchestrator=self,  # Pass reference to orchestrator
       system_message=system_message,
       agent_id=agent_id,
   )
   ```

3. Added memory access methods like `add_to_buffer_memory()`, `add_to_long_term_memory()`, `search_memory()`, and `clear_memory()` that provide centralized access with agent context

### Agent Class

1. Modified `__init__()` to store a reference to orchestrator:
   ```python
   def __init__(
       self,
       model: BaseModel,
       orchestrator=None,  # New parameter
       # ...other parameters...
   ):
       # ...
       self.orchestrator = orchestrator  # Store reference to orchestrator
   ```

2. Added compatibility properties to maintain backward compatibility:
   ```python
   @property
   def buffer_memory(self):
       """Compatibility property that returns orchestrator's buffer memory."""
       if self.orchestrator and hasattr(self.orchestrator, "buffer_memory"):
           return self.orchestrator.buffer_memory
       return self._buffer_memory  # Fallback to legacy memory
   ```

3. Updated memory-related methods to use orchestrator's memory with graceful fallback to legacy behavior

### Muxi Facade

1. Updated `__init__()` to accept memory parameters:
   ```python
   def __init__(
       self,
       buffer_memory: Optional[Union[int, BufferMemory]] = None,
       long_term_memory: Optional[Union[str, bool, LongTermMemory, Memobase]] = None,
       db_connection_string: Optional[str] = None
   ):
   ```

2. Added helper methods to create memory objects from various configuration formats:
   ```python
   def _create_buffer_memory(self, buffer_config):
       # Implementation...

   def _create_long_term_memory(self, long_term_config):
       # Implementation...
   ```

3. Updated `add_agent()` to use the orchestrator's memory instead of creating per-agent memory

## Backward Compatibility

The implementation maintains backward compatibility in several ways:

1. Legacy memory parameters in `Agent.__init__()` are kept but marked as deprecated
2. The Agent class exposes compatible properties (`buffer_memory`, `long_term_memory`) that proxy to orchestrator
3. Memory methods have graceful fallback to legacy behavior when orchestrator is not available
4. The facade accepts the same parameter formats as the original with expanded options

## Migration Path

To migrate existing code to the new architecture:

1. Update imports to the new versions of each class
2. Move memory configuration from agent level to orchestrator level (typically in Muxi facade)
3. Test with existing code to ensure compatibility
4. Update documentation to reflect the new recommended practices

## Usage Examples

### Declarative API (Muxi Facade)

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI with memory at orchestrator level
app = muxi(
    buffer_memory=10,  # Buffer size of 10
    long_term_memory="postgresql://user:password@localhost:5432/muxi"  # PostgreSQL
)

# Add agent from configuration (no memory configuration needed)
app.add_agent("configs/agent_config.json")

# Chat with the agent - uses orchestrator's memory
response = await app.chat("assistant", "Remember my name is Alice.")
```

### Programmatic API

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory

# Create memory components
buffer = BufferMemory(max_size=15)
long_term = LongTermMemory(connection_string="sqlite:///data/memory.db")

# Initialize orchestrator with memory
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=long_term
)

# Create agent that uses orchestrator's memory
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o"),
    system_message="You are a helpful assistant with memory."
)

# Chat with the agent - uses orchestrator's memory
response = await orchestrator.chat("assistant", "Remember my favorite color is blue.")
```

## Next Steps

1. Integrate the implementation into the codebase
2. Add unit tests for the new memory architecture
3. Update documentation with the new approach
4. Consider a more formal deprecation process for legacy memory parameters
5. Create a migration guide for users
