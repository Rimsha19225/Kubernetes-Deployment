---
id: 1
title: "Add-Cohere-API-key-configuration"
stage: "spec"
date_iso: "2026-01-22"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "todo-chatbot"
branch: "main"
user: "user"
command: "Add Cohere API key configuration"
labels: ["ai", "configuration", "api-key", "cohere"]
spec: null
ticket: null
adr: null
pr: null
files_yaml:
  - ".specify/memory/constitution.md"
  - "backend/.env"
  - "backend/src/config.py"
  - "backend/src/ai/__init__.py"
  - "backend/src/ai/cohere_service.py"
tests_yaml: []
---

# Prompt History Record

## Command
Add Cohere API key configuration

## User Input
```
Please add it in the constitution file. I want to use the Cohere API key in the chatbot, and the OpenAI Agent SDK code should also use the Cohere API key.
```

## Response Summary
Updated the constitution file to include Cohere API key configuration requirements in the AI Provider Configuration section. Added COHERE_API_KEY to the backend environment configuration. Updated the backend config.py file to include the cohere_api_key setting. Created a new AI services directory with a Cohere service module that handles the API key configuration.

## Files Modified
- .specify/memory/constitution.md: Added AI Provider Configuration section with API key management requirements
- backend/.env: Added COHERE_API_KEY environment variable
- backend/src/config.py: Added cohere_api_key setting to the Settings class
- backend/src/ai/__init__.py: Created AI services package initialization
- backend/src/ai/cohere_service.py: Created Cohere service module to handle API key configuration

## Outcome
Successfully configured the system to use Cohere API key as requested. The constitution now includes requirements for API key management, environment variables are set up, configuration is updated, and a service module is created to handle Cohere API interactions.