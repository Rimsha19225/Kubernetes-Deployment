---
id: 5
title: "Fix Entity Extraction for GET_USER_INFO Intent"
stage: general
date: "2026-01-25"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "adeel"
command: "manual"
labels: ["bug-fix", "nlp", "intent-processing", "entity-extraction"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "backend/src/ai/nlp_intent_processor.py"
tests: []
---

## Prompt

When a user asks the chatbot "What is my name?" or other user-info questions, the chatbot returns "I'm sorry, but I encountered an error processing your request." This happens because the NLP intent processor's _extract_entities() method applies task-specific logic to all intents, including GET_USER_INFO. Words like "name" incorrectly trigger task status detection, causing STATUS_INDICATOR entities to be extracted for user info queries, which then confuses the task controller.

## Response snapshot

Successfully fixed the entity extraction method in the NLP intent processor to be intent-aware. Task-specific entity extraction (status indicators, completion patterns, reference demonstratives) is now only performed for task-related intents, preventing interference with GET_USER_INFO queries.

## Outcome

- ✅ Impact: The chatbot now properly handles user info queries like "What is my name?" without triggering task-specific entity extraction that caused errors.
- 🧪 Tests: None
- 📁 Files: Modified backend/src/ai/nlp_intent_processor.py to make entity extraction intent-aware, limiting task-specific extraction to appropriate intent types.
- 🔁 Next prompts: None
- 🧠 Reflection: Intent-specific processing is crucial for preventing cross-contamination between different types of user requests.

## Evaluation notes (flywheel)

- Failure modes observed: Entity extraction logic was applied universally, causing task-specific patterns to match in user-info queries and confuse the task controller.
- Graders run and results (PASS/FAIL):
- Prompt variant (if applicable):
- Next experiment (smallest change to try): Add more granular intent-specific processing throughout the NLP pipeline.