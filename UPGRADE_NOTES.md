# MUXI Framework Upgrade Notes for Version 1.0

## Breaking Changes

As part of the preparation for the MUXI Framework 1.0 release, we've removed all backward compatibility support to create a cleaner, more maintainable codebase. This document outlines the changes made and provides guidance for upgrading your code.

### Removed Deprecated Methods

The following deprecated methods have been completely removed:

1. **In the `Agent` class:**
   - `_enhance_with_domain_knowledge()` - Use `_enhance_with_context_memory()` instead

2. **In the `Muxi` facade class:**
   - `add_user_domain_knowledge()` - Use `add_user_context_memory()` instead

### Updated API Signatures

1. **`Agent` class constructor:**
   - Removed the `memory` parameter - Use `buffer_memory` instead
   - Old: `Agent(model, memory=None, ...)`
   - New: `Agent(model, buffer_memory=None, ...)`

2. **`Orchestrator.create_agent` method:**
   - Removed the `memory` parameter - Use `buffer_memory` instead
   - Old: `create_agent(agent_id, model, memory=None, ...)`
   - New: `create_agent(agent_id, model, buffer_memory=None, ...)`

### Renamed Concepts

All references to "domain knowledge" have been renamed to "context memory" throughout the codebase, which better reflects the purpose of this feature - storing personalized user context.

### Other Changes

- Removed comments referencing backward compatibility in code
- Removed backward compatibility for user_id=0 handling in the Memobase wrapper
- Updated documentation to reflect the new terminology and methods

## Migration Guide

### For Agent Creation

If you were creating agents with the `memory` parameter:

```python
# Old code
agent = Agent(model=model, memory=my_memory)

# New code
agent = Agent(model=model, buffer_memory=my_memory)
```

### For User Context Operations

If you were using the domain knowledge methods:

```python
# Old code
muxi.add_user_domain_knowledge(user_id, {"name": "John"})

# New code
muxi.add_user_context_memory(user_id, {"name": "John"})
```

### For Advanced Agent Customization

If you were extending the Agent class and overriding methods:

```python
# Old code
async def _enhance_with_domain_knowledge(self, message, user_id=None):
    # Custom implementation

# New code
async def _enhance_with_context_memory(self, message, user_id=None):
    # Custom implementation
```

## Test Updates Required

Note that removing backward compatibility has broken a number of tests in the codebase. If you've created custom tests that rely on the old API, you'll need to update them.

## Conclusion

These changes are part of our commitment to providing a cleaner, more maintainable framework as we move toward version 1.0. While breaking changes can be disruptive, they allow us to move forward with a better foundation for future development.
