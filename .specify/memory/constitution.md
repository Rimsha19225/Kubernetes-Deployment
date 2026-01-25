<!-- SYNC IMPACT REPORT
Version change: 1.0.0 → 2.0.0
Modified principles: Phase Isolation, Agent-Governed Development, Core Principles
Added sections: Phase 3 Principles, Agent Responsibilities, Skill-Governed Capabilities
Removed sections: Phase 2-specific constraints
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ✅ updated
Follow-up TODOs: None
-->
# Todo Application Phase 3 Constitution: AI Todo Chatbot

## Overview
Phase 3 introduces an AI-powered Todo Chatbot as an intelligent control and interaction layer on top of the existing Phase 2 system. The chatbot is NOT a separate application, but rather an intelligent control layer that must preserve all Phase 2 logic, APIs, and business rules.

## Core Principles

### 1. Phase 2 Preservation
- Phase 2 APIs, business rules, and security measures are the single source of truth
- The chatbot must use Phase 2 APIs exclusively for all operations
- Direct database access by the chatbot is strictly forbidden
- No Phase 2 logic may be modified, bypassed, or duplicated

### 2. Intent-Driven Control
- The chatbot operates by identifying user intent from natural language input
- Every chatbot action must map to a valid Phase 2 operation
- If an intent cannot be safely mapped to a Phase 2 operation, it must be rejected or clarified

### 3. No Hallucinated Actions
- The chatbot may not invent data, tasks, users, or states that don't exist in Phase 2
- If information is not available via Phase 2 APIs, the chatbot must acknowledge this limitation
- All responses must be grounded in actual system data

### 4. User-Scoped Safety
- The chatbot may only access data belonging to the authenticated user
- Cross-user access is strictly forbidden
- The chatbot must correctly identify and use the logged-in user context at all times

### 5. Explicit Behavior Only
- All chatbot capabilities must be explicitly specified in the constitution or specifications
- Implicit or assumed AI behavior is not allowed
- If a behavior is not explicitly specified, the chatbot must not perform it

## Agent-Governed Execution

### Agent Responsibilities
All Phase 3 work must be performed by specialized agents with fixed responsibilities:
- **phase3-system-architect**: Defines and enforces system architecture
- **ai-chatbot-orchestration**: Coordinates chatbot operations and intent processing
- **nlp-intent**: Parses natural language and identifies user intent
- **task-ai-control**: Translates AI intents to Phase 2 task operations
- **user-context**: Manages user identity and data isolation
- **ai-backend-integration**: Handles secure communication between AI and backend
- **ai-response-composer**: Formats responses for user consumption
- **ai-quality-guard**: Validates responses for safety and accuracy
- **skills-create**: Manages the creation and governance of professional skills

### Agent Constraints
- No agent may act outside its defined scope
- Agents must coordinate through approved interfaces only
- Agent behaviors must be explicitly specified

## Skill-Governed Capabilities

### Skill Requirements
- Agents may only use approved and documented skills
- Skills must be atomic, non-overlapping, and purpose-specific
- No agent may create or assume new skills without explicit approval
- All skills must be documented in the skills directory

## AI Provider Configuration

### API Key Management
- The system must use the Cohere API key for all AI operations
- API keys must be stored securely in environment variables
- The Cohere API key must be accessible to all AI agents and services
- The OpenAI Agent SDK must be configured to use the Cohere API key instead of OpenAI services
- API key access must follow the principle of least privilege

## Supported Chatbot Operations

The chatbot must be able to perform these operations using Phase 2 APIs:
- Add tasks
- Delete tasks
- Edit tasks
- Mark tasks as complete or incomplete
- Search tasks by title or description keywords
- Filter tasks (completed/incomplete)
- Sort tasks (by title, status, date)
- List tasks clearly
- Answer questions about the currently logged-in user (e.g., email)

## Chatbot Operation Rules

### Safety Requirements
- The chatbot must confirm destructive actions when appropriate
- Ambiguous commands must trigger clarification questions
- Multi-step commands must be handled safely and sequentially
- Errors must be translated into clear, human-readable messages

### Authentication & Authorization
- All actions must respect existing authentication protocols
- User data isolation must be maintained at all times
- The chatbot must validate user context before each sensitive operation

## Hard Constraints

### Non-Negotiable Requirements
- No direct database access by any AI component
- No modification of Phase 2 business rules
- No unauthenticated actions
- No cross-user data access
- No silent failures
- No undocumented AI behavior

## Success Criteria

Phase 3 is considered complete only if:
- All supported task operations work reliably via the chatbot
- The chatbot consistently respects authentication and user isolation
- The chatbot never bypasses Phase 2 APIs
- Errors and confirmations are clearly communicated to users
- All chatbot behavior is traceable to specifications
- No Phase 2 functionality is broken or compromised

## Decision Priority Order

When ambiguity arises, decisions must follow this priority:
1. Phase 3 Constitution
2. Phase 2 APIs and established rules
3. Approved Phase 3 Specifications
4. Security and user safety considerations
5. Clarity over convenience

## Constitutional Rule

**If a behavior is not explicitly specified in this constitution or supporting specifications, the chatbot must not perform it.**

This ensures the system remains safe, predictable, and aligned with the established architectural principles.

**Version**: 2.0.0 | **Ratified**: 2026-01-21 | **Last Amended**: 2026-01-21