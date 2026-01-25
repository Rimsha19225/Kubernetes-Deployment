# Data Model: AI Todo Chatbot

## Core Entities

### ChatMessage
- **Fields**: id, userId, messageText, timestamp, messageType (input/output), sessionId
- **Relationships**: Belongs to User, Part of ChatSession
- **Validation**: MessageText must not be empty, timestamp must be current

### ChatSession
- **Fields**: id, userId, createdAt, lastActiveAt, isActive
- **Relationships**: Belongs to User, Contains ChatMessages
- **State Transitions**: Active → Inactive (after timeout or explicit end)

### UserIntent
- **Fields**: id, intentType (CREATE_TASK, UPDATE_TASK, DELETE_TASK, LIST_TASKS, SEARCH_TASKS, GET_USER_INFO), confidenceScore, extractedEntities
- **Validation**: intentType must be one of allowed values, confidenceScore must be between 0 and 1

### ExtractedEntity
- **Fields**: id, entityType (TASK_TITLE, TASK_DESCRIPTION, KEYWORD, STATUS_INDICATOR, REFERENCE_DEMONSTRATIVE), entityValue, confidenceScore
- **Validation**: entityType must be one of allowed values, entityValue must not be empty

### TaskOperation
- **Fields**: id, operationType (CREATE, UPDATE, DELETE, SEARCH, FILTER, SORT), parameters, userId
- **Relationships**: Associated with User
- **Validation**: operationType must be valid, parameters must match operation requirements

## System State Models

### ConversationState
- **Fields**: sessionId, currentIntent, pendingClarifications, awaitingConfirmation
- **State Transitions**: IDLE → PROCESSING → AWAITING_CONFIRMATION/PENDING_CLARIFICATION → COMPLETE

### UserContext
- **Fields**: userId, isAuthenticated, permissions, activeTasksFilter
- **Validation**: userId must exist and be authenticated for operations