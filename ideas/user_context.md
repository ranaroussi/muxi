# User Context Memory Renaming Plan

## Background

Currently, the MUXI Framework uses the term "user domain knowledge" to refer to knowledge specific to a user that enhances agent responses. This creates confusion with regular "domain knowledge" which is specialized information that agents use. To improve clarity, we will rename all instances of "user domain knowledge" to "user context memory" throughout the codebase.

## Objectives

1. Clearly distinguish between agent knowledge and user-specific information
2. Maintain consistent terminology across all code, APIs, and documentation
3. Ensure backward compatibility during transition
4. Update all relevant files: Python code, documentation, examples, and tests

## Implementation Plan

### Phase 1: Code Changes

1. **Core Classes and Functions**
   - Update `Memobase` class constants:
     - `DOMAIN_KNOWLEDGE_COLLECTION` → `CONTEXT_MEMORY_COLLECTION`
     - `DOMAIN_KNOWLEDGE_TYPE` → `CONTEXT_MEMORY_TYPE`
   - Rename methods in `Memobase`:
     - `add_user_domain_knowledge()` → `add_user_context_memory()`
     - `get_user_domain_knowledge()` → `get_user_context_memory()`
     - `import_user_domain_knowledge()` → `import_user_context_memory()`
     - `clear_user_domain_knowledge()` → `clear_user_context_memory()`
   - Update `Muxi` facade class methods:
     - `add_user_domain_knowledge()` → `add_user_context_memory()`
   - Update method references in `Agent` class:
     - `_enhance_with_domain_knowledge()` → `_enhance_with_context_memory()`
     - Update any other method calls accordingly

2. **Module Names**
   - If a `domain_knowledge.py` module exists specifically for user knowledge, rename to `context_memory.py`
   - Update corresponding imports in all files

### Phase 2: API Updates

1. **API Endpoints**
   - Update endpoint paths in the REST API:
     - `/users/{user_id}/domain_knowledge` → `/users/{user_id}/context_memory`

2. **Request/Response Structures**
   - Update JSON field names in API schemas to use "context_memory" terminology
   - Maintain backward compatibility with deprecated endpoint support

### Phase 3: Documentation Updates

1. **Markdown Files**
   - Update all references in documentation:
     - `docs/extend/knowledge.md` - Update sections about user knowledge
     - `docs/intro/quick-start.md` - Update examples
     - `README.md` - Update feature descriptions and examples
     - All other markdown files with "user domain knowledge" references

2. **Code Examples**
   - Update all examples in documentation and test files to use new method names

3. **Comments**
   - Update docstrings and comments in all code files

### Phase 4: Testing

1. **Unit Tests**
   - Update test files:
     - Rename `tests/test_domain_knowledge.py` if it's for user knowledge
     - Update all test cases using the old method names

2. **Integration Tests**
   - Ensure API tests are updated for new endpoints
   - Verify backward compatibility

## Backward Compatibility Strategy IS NOT RELEVANT


## Files to Update

### Python Code
- `packages/server/src/muxi/memory/memobase.py`
- `packages/core/src/muxi/facade.py`
- `packages/core/src/muxi/core/agent.py`
- Any additional Python files with references to user domain knowledge

### Documentation
- `ideas/api.md`
- `ideas/knowledge.md`
- `docs/extend/knowledge.md`
- `docs/intro/quick-start.md`
- `docs/technical/memory/` directory files
- `README.md`
- Other markdown files with references to user domain knowledge

### Tests
- `tests/test_domain_knowledge.py`
- Other test files using user domain knowledge functionality

## Timeline

1. **Planning & Preparation**: 1 day
   - Create detailed inventory of all references
   - Design backward compatibility approach

2. **Implementation**: 2-3 days
   - Code changes
   - API updates
   - Documentation updates

3. **Testing**: 1-2 days
   - Unit and integration testing
   - Verify backward compatibility

4. **Release**: 1 day
   - Update changelog
   - Create migration guide for users
   - Deploy updates

## Future Considerations

1. Consider updating related concepts for consistency:
   - Review other memory-related terminology
   - Ensure clear distinction between different types of knowledge/memory

2. Improve documentation around the conceptual differences:
   - User context memory (personalization)
   - Domain knowledge (specialized agent information)
   - Working memory (conversation history)
