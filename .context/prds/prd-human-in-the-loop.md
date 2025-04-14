# MUXI Framework Human-in-the-Loop PRD

## 1. Introduction

This PRD defines the requirements and design for the Human-in-the-Loop feature of the MUXI Framework. This feature will enable agents to pause execution while awaiting human input, then resume processing once input is received, creating an asynchronous communication channel between agents and human users.

### 1.1 Background

AI agents often need human guidance or approval during task execution. These situations include:
- Confirming a potentially expensive or irreversible action
- Seeking clarification when faced with ambiguity
- Requesting additional information not available to the agent
- Presenting options and awaiting user preference

The Human-in-the-Loop feature addresses these needs by providing a standardized way for agents to pause execution, collect human input, and resume with the provided information.

## 2. Goals and Objectives

### 2.1 Primary Goals

- Implement a mechanism for agents to pause execution while awaiting human input
- Provide a flexible notification system allowing developers to choose delivery methods
- Create a simple response collection interface for human users to provide input
- Ensure reliable state preservation and resumption of processing
- Make the system extensible for various use cases and notification channels

### 2.2 Success Metrics

- Agent state is reliably preserved and restored across the pause/resume cycle
- Developers can easily integrate custom notification systems (WhatsApp, email, etc.)
- The default form interface is simple and requires minimal configuration
- Response processing time adds minimal overhead to agent execution

## 3. Feature Requirements

### 3.1 Functional Requirements

1. **State Management**
   - Store complete agent execution state when a human-in-the-loop request is triggered
   - Generate unique interaction IDs for each request
   - Support resumption of execution with the exact state and context
   - Clean up stored state after successful completion or expiration

2. **Notification System**
   - Provide a callback interface for developers to implement custom notifications
   - Include the agent's message and a form URL in the callback context
   - Support optional expiration times for time-sensitive requests
   - Include a default implementation for simple use cases

3. **Response Interface**
   - Provide a default web form that displays the agent's message
   - Include a simple text input field for human response
   - Support response submission to the framework's API
   - Ensure the form works on mobile and desktop devices

4. **API Endpoints**
   - Create `/v1/interactions/:id/respond` endpoint for response collection
   - Provide endpoints for checking interaction status
   - Support optional authentication for response validation
   - Allow response submission from both the default form and custom implementations

5. **Integration with Agent Flow**
   - Enable agents to trigger human-in-the-loop requests at any point in processing
   - Pass human responses directly to agents without modification or parsing
   - Allow agents to determine their own criteria for when to request human input
   - Support multiple sequential human-in-the-loop interactions within a single task

### 3.2 Non-Functional Requirements

1. **Persistence**
   - Use SQLite by default for state storage
   - Support PostgreSQL for production deployments
   - Ensure durability of state across server restarts
   - Implement appropriate data retention and cleanup policies

2. **Security**
   - Sanitize all user inputs to prevent injection attacks
   - Validate interaction IDs to prevent unauthorized access
   - Protect stored state data from unauthorized access
   - Optional support for authentication of response submissions

3. **Performance**
   - Minimize overhead added to agent processing
   - Efficiently serialize and deserialize agent state
   - Implement appropriate timeouts for pending interactions
   - Optimize database interactions for fast response times

4. **Extensibility**
   - Design for easy addition of new notification providers
   - Support custom authentication mechanisms
   - Allow for future enhancements like structured response types
   - Maintain clean separation between core functionality and extensions

## 4. User Experience

### 4.1 Developer Experience

Developers will configure the human-in-the-loop feature through agent configuration:

```python
# Example configuration
agent_config = {
    "human_in_loop": {
        "enabled": True,
        "notification_callback": my_notification_function,
        "interaction_timeout": 24*60*60,  # 24 hours in seconds
        "state_storage": {
            "type": "sqlite",  # or "postgres"
            "connection_string": "sqlite:///interactions.db"
        }
    }
}
```

The notification callback function will receive context about the interaction:

```python
def my_notification_function(interaction_context):
    """
    Process a human-in-the-loop interaction request.

    Args:
        interaction_context: Dict containing:
            - interaction_id: Unique identifier for this interaction
            - agent_message: The message/question from the agent
            - form_url: URL to the default response form
            - expiry_time: When this interaction request expires (optional)
    """
    # Developer implements their preferred notification method
    send_email(
        to="user@example.com",
        subject="Your assistant needs your input",
        body=f"""
        Your assistant says:

        "{interaction_context['agent_message']}"

        You can respond here: {interaction_context['form_url']}
        """
    )
```

### 4.2 End-User Experience

From the end-user perspective, the experience will be:

1. User initiates a task with an agent through any interface
2. Agent processes the task until it needs human input
3. User receives a notification (email, WhatsApp, etc.) with the agent's message
4. User clicks the provided link or otherwise accesses the response interface
5. User sees the agent's message and provides a text response
6. User submits their response
7. Agent resumes processing with the provided input
8. Agent continues the task to completion

The default form will be simple and focused, containing:
- The agent's message/question
- A text input field for the user's response
- A submit button

## 5. Technical Design

### 5.1 State Storage

The framework will store interaction state in a database:

```
Table: human_interactions
Columns:
- interaction_id: UUID (Primary Key)
- agent_id: String
- user_id: String (optional)
- message: Text
- created_at: Timestamp
- expires_at: Timestamp (optional)
- status: Enum ('pending', 'completed', 'expired')
- response: Text (null until completed)

Table: interaction_state
Columns:
- interaction_id: UUID (Foreign Key to human_interactions)
- state_data: BLOB/JSON (serialized agent state)
```

### 5.2 API Endpoints

```
POST /v1/interactions/:id/respond
- Request body: { "response": "User's text response" }
- Response: { "status": "success", "message": "Response received" }

GET /v1/interactions/:id/status
- Response: { "status": "pending|completed|expired", "created_at": "timestamp" }
```

### 5.3 Agent Integration

Agents will use a simple async method to request human input:

```python
# Inside agent processing
human_response = await self.request_human_input(
    "I found several hotels in Vienna. Would you like me to book Hotel Mozart at $220/night with 4.5 stars, or would you prefer I keep searching?"
)

# Agent continues processing with the human's response
```

### 5.4 Notification System

The notification system will use a provider pattern:

```python
class NotificationManager:
    def __init__(self):
        self.default_callback = None

    def register_callback(self, callback_function):
        self.default_callback = callback_function

    async def send_notification(self, interaction_context):
        if self.default_callback:
            return await self.default_callback(interaction_context)
        else:
            # Log that no callback is registered
            return False
```

## 6. Implementation Plan

### 6.1 Phase 1: Core Infrastructure

1. Create database schema for interaction storage
2. Implement state serialization and deserialization
3. Build basic API endpoints for response collection
4. Develop the notification callback system

### 6.2 Phase 2: Agent Integration

1. Add `request_human_input` method to Agent class
2. Create middleware for processing human responses
3. Implement state preservation and resumption in agent flow
4. Add configuration options for human-in-the-loop features

### 6.3 Phase 3: Default Form Implementation

1. Create a simple web form for response collection
2. Implement URL generation for interaction forms
3. Add basic styling and mobile responsiveness
4. Ensure proper error handling and validation

### 6.4 Phase 4: Testing and Documentation

1. Create comprehensive unit tests for all components
2. Perform integration testing of the full workflow
3. Write detailed documentation for developers
4. Create examples demonstrating various use cases

## 7. Future Considerations

1. **Rich Response Types**: Potentially extend the system to support structured responses like multiple choice, file uploads, etc.

2. **Real-time Notification**: Add WebSocket support for real-time notifications when responses are received.

3. **Multi-step Interactions**: Support for guided workflows with multiple back-and-forth interactions.

4. **Authentication Improvements**: More robust authentication options for sensitive interactions.

5. **Analytics**: Tracking and reporting on interaction completion rates, response times, etc.
