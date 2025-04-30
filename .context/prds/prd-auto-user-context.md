# Automatic User Context Extraction PRD

## Overview

This document outlines the implementation plan for adding automatic user information extraction capabilities to the MUXI Framework. This feature will enable agents to automatically identify and store important information about users from conversations, building a comprehensive user profile over time without requiring explicit code to identify and store each piece of information.

## Problem Statement

Currently, the MUXI Framework provides robust user context memory capabilities, but requires developers to explicitly add information to memory using `add_user_context_memory()` or similar methods. This manual approach:

1. Requires explicit code to identify and extract user information
2. Misses valuable information shared naturally in conversations
3. Places the burden on developers to anticipate what information might be relevant
4. Doesn't leverage the capabilities of LLMs to infer relationships and importance

## Solution: Automatic Context Extraction

We will implement an automatic information extraction system that:

1. Analyzes conversations after each interaction
2. Identifies key facts, preferences, and characteristics about the user
3. Assigns importance scores to discovered information
4. Stores information in the user's context memory
5. Resolves conflicts with existing information
6. Provides configuration options for developers to control the behavior

## Goals and Non-Goals

### Goals

- Create a flexible extraction system that works across different use cases
- Allow developers to control extraction behavior through configuration
- Support extraction of structured data (e.g., contact details, preferences)
- Enable importance-based prioritization of information
- Implement confidence scoring to prevent storing uncertain information
- Provide model selection options for cost optimization

### Non-Goals

- Extract information from non-conversation sources (e.g., documents, forms)
- Create a complex rule-based extraction system
- Support extraction beyond what can be inferred from conversation
- Replace explicit context memory management methods

## Implementation Plan

### 1. Core Components

#### MemoryExtractor Class

We will create a dedicated `MemoryExtractor` class responsible for:

- Processing conversation history
- Extracting user information
- Scoring importance and confidence
- Resolving conflicts with existing information
- Storing results in context memory

```python
class MemoryExtractor:
    def __init__(
        self,
        orchestrator,
        extraction_model=None,
        confidence_threshold=0.7,
        auto_extract=True,
        extraction_interval=1,  # Process every n messages
        max_history_tokens=1000,
    ):
        self.orchestrator = orchestrator
        self.extraction_model = extraction_model  # Model for extraction (may differ from agent model)
        self.confidence_threshold = confidence_threshold
        self.auto_extract = auto_extract
        self.extraction_interval = extraction_interval
        self.max_history_tokens = max_history_tokens

    async def process_conversation_turn(
        self,
        user_message,
        agent_response,
        user_id,
        message_count=1
    ):
        """Process a conversation turn and extract information if needed."""
        if not self.auto_extract:
            return

        # Skip extraction for anonymous users (user_id=0)
        if user_id == 0:
            return

        # Only process every n messages based on extraction_interval
        if message_count % self.extraction_interval != 0:
            return

        # Create conversation context from this turn
        conversation = f"User: {user_message}\nAssistant: {agent_response}"

        # Extract information
        extraction_results = await self._extract_user_information(conversation)

        # Process and store results if confidence threshold is met
        await self._process_extraction_results(extraction_results, user_id)

    async def _extract_user_information(self, conversation):
        """Extract user information using the specified LLM."""
        # Use the specified extraction model if available, otherwise use orchestrator's default
        model = self.extraction_model or self.orchestrator.default_model

        # Create extraction prompt
        prompt = self._create_extraction_prompt(conversation)

        # Generate extraction results
        extraction_response = await model.generate(prompt)

        # Parse results into structured format
        try:
            # Parse JSON response (primary approach)
            extraction_results = json.loads(extraction_response)
        except json.JSONDecodeError:
            # Fallback parsing if LLM doesn't return valid JSON
            extraction_results = self._parse_fallback_extraction(extraction_response)

        return extraction_results

    def _create_extraction_prompt(self, conversation):
        """Create an optimized prompt for information extraction."""
        return (
            "Based on the following conversation, extract important information about the user "
            "that should be remembered for future interactions. For each piece of information, "
            "include:\n"
            "1. The specific information (value)\n"
            "2. The category/key it belongs to (e.g., name, location, preference)\n"
            "3. A confidence score (0.0-1.0) indicating how certain you are\n"
            "4. An importance score (0.0-1.0) indicating how important this is to remember\n\n"
            "Format your response as a JSON object with the following structure:\n"
            "{\n"
            '  "extracted_info": [\n'
            '    {\n'
            '      "key": "category name",\n'
            '      "value": "the extracted information",\n'
            '      "confidence": 0.95,\n'
            '      "importance": 0.8\n'
            '    },\n'
            '    ...\n'
            '  ]\n'
            "}\n\n"
            f"Conversation:\n{conversation}\n\n"
            "If there is no relevant information to extract, return an empty array for extracted_info."
        )

    async def _process_extraction_results(self, extraction_results, user_id):
        """Process extraction results and update context memory."""
        if not extraction_results or "extracted_info" not in extraction_results:
            return

        # Get existing user context memory
        existing_context = await self.orchestrator.get_user_context_memory(user_id=user_id)

        # Process each extracted item
        knowledge_updates = {}
        for item in extraction_results["extracted_info"]:
            # Skip items below confidence threshold
            if item["confidence"] < self.confidence_threshold:
                continue

            key = item["key"]
            value = item["value"]
            importance = item["importance"]

            # Handle conflicts with existing information
            if key in existing_context:
                # Determine if we should update based on confidence and importance
                if not self._should_update_existing(key, value, existing_context[key], importance):
                    continue

            # Add to updates
            knowledge_updates[key] = value

        # Store updates in context memory if any exist
        if knowledge_updates:
            await self.orchestrator.add_user_context_memory(
                user_id=user_id,
                knowledge=knowledge_updates,
                source="automatic_extraction",
                importance=0.85  # Default importance for automatic extraction
            )

    def _should_update_existing(self, key, new_value, existing_value, importance):
        """Determine if existing information should be updated."""
        # For complex updates like adding to lists, merging objects, etc.
        # Will need to implement category-specific logic

        # Simple version - higher importance items replace existing items
        if isinstance(existing_value, dict) and "importance" in existing_value:
            return importance > existing_value["importance"]

        # Default to updating
        return True

    def _parse_fallback_extraction(self, text):
        """Parse extraction results from text if JSON parsing fails."""
        # Implement fallback parsing logic for when the LLM doesn't return valid JSON
        # This is a simplified implementation
        lines = text.strip().split('\n')
        extracted_info = []

        current_item = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_item and "key" in current_item and "value" in current_item:
                    # Add default values if missing
                    if "confidence" not in current_item:
                        current_item["confidence"] = 0.7
                    if "importance" not in current_item:
                        current_item["importance"] = 0.5
                    extracted_info.append(current_item)
                current_item = {}
            elif ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key in ["key", "category"]:
                    current_item["key"] = value
                elif key in ["value", "information"]:
                    current_item["value"] = value
                elif key == "confidence":
                    try:
                        current_item["confidence"] = float(value)
                    except ValueError:
                        current_item["confidence"] = 0.7
                elif key == "importance":
                    try:
                        current_item["importance"] = float(value)
                    except ValueError:
                        current_item["importance"] = 0.5

        # Add the last item if it exists
        if current_item and "key" in current_item and "value" in current_item:
            # Add default values if missing
            if "confidence" not in current_item:
                current_item["confidence"] = 0.7
            if "importance" not in current_item:
                current_item["importance"] = 0.5
            extracted_info.append(current_item)

        return {"extracted_info": extracted_info}
```

### 2. Integration with Agent & Orchestrator

#### Agent Integration

```python
class Agent:
    # Existing implementation...

    async def process_message(self, message: Union[str, MCPMessage], user_id: Optional[int] = None) -> MCPMessage:
        """Process a message from the user."""
        # Existing implementation...

        # Convert string message to MCPMessage if needed
        if isinstance(message, str):
            content = message
            # Store original message
            original_content = content
            # Enhance message with context memory if available
            enhanced_message = await self._enhance_with_context_memory(content, user_id)
            message = MCPMessage(role="user", content=enhanced_message)
        else:
            content = message.content
            original_content = content
            # Process existing MCPMessage...

        # Process message with MCP handler
        response = await self.mcp_handler.process_message(message)

        # Store assistant response in memory if using multi-user support
        # Existing implementation...

        # Perform automatic extraction if enabled
        if (self.orchestrator and
            hasattr(self.orchestrator, 'memory_extractor') and
            self.orchestrator.memory_extractor and
            user_id is not None):

            # Increment message counter for this user
            user_message_count = self.orchestrator.get_user_message_count(user_id)

            # Process conversation turn for extraction
            await self.orchestrator.memory_extractor.process_conversation_turn(
                user_message=original_content,
                agent_response=response.content,
                user_id=user_id,
                message_count=user_message_count
            )

        return response
```

#### Orchestrator Integration

```python
class Orchestrator:
    # Existing implementation...

    def __init__(
        self,
        buffer_memory=None,
        long_term_memory=None,
        is_multi_user=False,
        auto_extract_context=False,
        extraction_model=None,
        extraction_confidence=0.7,
        extraction_interval=1,
    ):
        # Existing initialization...

        # Initialize message counter for extraction interval
        self.user_message_counts = {}

        # Initialize memory extractor if auto_extract is enabled
        self.memory_extractor = None
        if auto_extract_context and self.is_multi_user and self.long_term_memory:
            self.memory_extractor = MemoryExtractor(
                orchestrator=self,
                extraction_model=extraction_model,
                confidence_threshold=extraction_confidence,
                auto_extract=auto_extract_context,
                extraction_interval=extraction_interval
            )

    def get_user_message_count(self, user_id):
        """Get and increment the message count for a user."""
        if user_id not in self.user_message_counts:
            self.user_message_counts[user_id] = 0

        self.user_message_counts[user_id] += 1
        return self.user_message_counts[user_id]

    # Rest of implementation...
```

### 3. Configuration Options

Update the MUXI facade to support automatic extraction configuration:

```python
def muxi(
    buffer_memory=None,
    long_term_memory=None,
    is_multi_user=False,
    auto_extract_context=False,  # Enable automatic context extraction
    extraction_model=None,       # Model to use for extraction (None = use agent model)
    extraction_confidence=0.7,   # Minimum confidence threshold
    extraction_interval=1,       # Process every n messages
    # Other existing parameters...
):
    """Initialize the MUXI Framework."""
    # Create orchestrator with extraction settings
    orchestrator = Orchestrator(
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        is_multi_user=is_multi_user,
        auto_extract_context=auto_extract_context,
        extraction_model=extraction_model,
        extraction_confidence=extraction_confidence,
        extraction_interval=extraction_interval,
    )

    # Rest of implementation...
```

## Usage Examples

### Basic Usage with Default Agent Model

```python
from muxi import muxi
import os

# Initialize MUXI with automatic extraction
app = muxi(
    buffer_memory=100,
    long_term_memory="sqlite:///memory.db",
    is_multi_user=True,
    auto_extract_context=True,  # Enable automatic extraction
)

# Add an agent
app.add_agent(
    agent_id="assistant",
    model={
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
)

# The agent will now automatically extract and store user information
```

### Advanced Configuration with Custom Extraction Model

```python
from muxi import muxi
import os
from muxi.core.models.openai import OpenAIModel

# Create a lower-cost model specifically for extraction
extraction_model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo",  # Lower cost model for extraction
)

# Initialize MUXI with custom extraction settings
app = muxi(
    buffer_memory=100,
    long_term_memory="postgresql://user:pass@localhost:5432/db",
    is_multi_user=True,
    auto_extract_context=True,
    extraction_model=extraction_model,  # Use specific model for extraction
    extraction_confidence=0.8,  # Higher confidence threshold
    extraction_interval=3,  # Only process every 3rd message
)

# Add agent with higher-capability model for interactions
app.add_agent(
    agent_id="assistant",
    model={
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
)

# The system will now use gpt-3.5-turbo for extraction (saving cost)
# while using Claude for the actual conversation
```

### Manual Extraction

```python
# For more control, extraction can be triggered manually
async def process_important_conversation(app, conversation_history, user_id):
    # Extract from existing conversation history
    extracted_info = await app.extract_user_context(
        conversation_history=conversation_history,
        user_id=user_id,
        confidence_threshold=0.9  # Higher threshold for this specific extraction
    )

    print(f"Extracted information: {extracted_info}")

    # Information is automatically stored in user context memory
```

## Technical Considerations

### 1. Model Selection for Cost Optimization

- **Default Behavior**: By default, the system uses the agent's model for extraction
- **Cost Optimization**: Developers can specify a lower-cost model (e.g., gpt-3.5-turbo) for extraction while using a higher-capability model (e.g., claude-3-opus) for conversations
- **Extraction Quality**: The extraction model should be capable of following structured extraction instructions and outputting well-formatted JSON

### 2. Extraction Frequency

- **Default**: Process every message
- **Configurable Interval**: Process every Nth message via `extraction_interval`
- **Adaptive Processing**: Future enhancement could analyze message importance to determine when to extract

### 3. Storage Efficiency

- **Deduplication**: Avoid storing the same information multiple times
- **Merging Related Information**: Intelligently merge related information (e.g., combine partial addresses)
- **Importance-Based Pruning**: If memory grows too large, remove less important information first

### 4. Privacy Considerations

- **Opt-Out Mechanism**: Allow users to disable automatic extraction
- **Explicit Information**: Consider flagging automatically extracted vs. explicitly provided information
- **Retention Policy**: Implement configurable retention periods for different information types

## Implementation Timeline

1. **Phase 1: Core Implementation** (2-3 days)
   - Implement `MemoryExtractor` class
   - Integrate with Agent and Orchestrator
   - Add configuration options
   - Create basic tests

2. **Phase 2: Enhancements** (2-3 days)
   - Implement conflict resolution logic
   - Add categorization of information types
   - Optimize extraction prompts
   - Add extraction model selection

3. **Phase 3: Documentation & Examples** (1-2 days)
   - Update documentation
   - Create usage examples
   - Add best practices guide

## Success Metrics

- **Extraction Accuracy**: Correctly identify and extract 85%+ of important user information
- **False Positive Rate**: Less than 10% incorrect extractions
- **Performance Impact**: Less than 15% additional latency when extraction is enabled
- **Storage Efficiency**: No more than 2x increase in context memory size compared to manual extraction

## API Reference

### Orchestrator Methods

```python
class Orchestrator:
    # New methods

    async def extract_user_context(
        self,
        conversation_history,
        user_id,
        confidence_threshold=None,
        model=None
    ):
        """
        Extract user context information from conversation history.

        Args:
            conversation_history: String or list of messages
            user_id: User ID to store information for
            confidence_threshold: Override default confidence threshold
            model: Override default extraction model

        Returns:
            Dictionary of extracted information
        """
        # Implementation details...

    async def get_extraction_stats(self, user_id):
        """
        Get statistics about automatic extractions for a user.

        Args:
            user_id: User ID to get stats for

        Returns:
            Dictionary of extraction statistics
        """
        # Implementation details...
```

## Future Enhancements

1. **Adaptive Extraction**: Dynamically adjust extraction frequency based on conversation importance
2. **Structured Information Templates**: Define templates for common information types (addresses, preferences, etc.)
3. **Information Lifecycle Management**: Age out information based on recency and importance
4. **Enhanced Conflict Resolution**: More sophisticated handling of conflicting information
5. **User Correction Flow**: Allow users to correct automatically extracted information
6. **Extraction Confidence Scoring**: Improve accuracy of confidence assessments
7. **Multi-Turn Information Assembly**: Build complex information across multiple conversation turns

## Conclusion

Automatic user context extraction will significantly enhance the MUXI Framework's ability to build rich user profiles over time, without requiring explicit manual updates to context memory. This feature maintains MUXI's philosophy of providing powerful capabilities through simple APIs while giving developers fine-grained control through configuration options.

The implementation will focus on extraction quality, privacy considerations, and performance optimization, with flexible model selection to allow cost-effective deployment across different use cases.
