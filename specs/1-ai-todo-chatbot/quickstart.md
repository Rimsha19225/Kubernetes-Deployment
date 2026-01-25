# Quick Start Guide: AI Todo Chatbot

## Overview
The AI Todo Chatbot operates as an intelligent control layer that processes natural language input and translates it into actions on the existing Phase 2 Todo application APIs.

## Architecture Components

### 1. Chat Interface Layer
- Receives user messages via API endpoint
- Manages session context
- Formats responses for user consumption

### 2. AI Processing Layer
- Processes natural language using Cohere API
- Identifies user intent from input
- Extracts entities (task titles, descriptions, keywords)

### 3. Intent Mapping Layer
- Maps identified intents to Phase 2 API operations
- Validates user permissions
- Manages confirmation flows for destructive actions

### 4. Backend Integration Layer
- Forwards authenticated requests to Phase 2 APIs
- Handles token propagation
- Manages error translation

## Setup Requirements

### Environment Variables
- `COHERE_API_KEY`: Cohere API key for AI processing
- `PHASE2_API_BASE_URL`: Base URL for Phase 2 APIs
- `JWT_SECRET`: Secret for validating authentication tokens

### Dependencies
- Cohere SDK for AI processing
- HTTP client for API communication
- JWT library for token validation

## Core Workflow

1. **User Input**: User sends natural language message to `/chat/message`
2. **Authentication**: System validates JWT token and retrieves user context
3. **Intent Recognition**: AI analyzes message to identify user intent
4. **Entity Extraction**: AI extracts relevant entities (titles, keywords, etc.)
5. **Validation**: System validates intent against allowed operations
6. **API Translation**: Intent is converted to appropriate Phase 2 API call
7. **Execution**: Phase 2 API performs the requested operation
8. **Response**: AI formats the result into natural language response
9. **Delivery**: Response is sent back to user

## Example Interactions

### Task Creation
- **User**: "Add a task to buy groceries"
- **System**: Calls Phase 2 POST /tasks with title "buy groceries"
- **Response**: "I've created a task 'buy groceries' for you."

### Task Update
- **User**: "Mark the grocery task as complete"
- **System**: Calls Phase 2 GET /tasks to find matching task, then PATCH /tasks/{id}
- **Response**: "I've marked the 'buy groceries' task as complete."

### Task Search
- **User**: "Find tasks about dentist"
- **System**: Calls Phase 2 GET /tasks with search parameter
- **Response**: Lists all tasks containing "dentist"

## Safety Measures
- All destructive actions require confirmation
- User context is validated for every operation
- Responses are filtered to prevent data leakage
- Error messages are sanitized and user-friendly