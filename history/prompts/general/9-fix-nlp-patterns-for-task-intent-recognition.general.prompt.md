---
id: 9
title: "Fix NLP Patterns for Task Intent Recognition"
stage: general
date: "2026-01-25"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "adeel"
command: "manual"
labels: ["bug-fix", "nlp", "intent-recognition", "task-processing"]
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

The chatbot was only recognizing CREATE_TASK intent and defaulting all task-related user inputs to creating new tasks, regardless of the actual user intent. For example, update/delete/search requests were all treated as create requests. This happened because the NLP intent processor lacked specific patterns to distinguish between different task operation intents.

## Response snapshot

Successfully enhanced the NLP intent processor with specific patterns for UPDATE_TASK, DELETE_TASK, and SEARCH_TASKS intents to properly distinguish between different task operations. Added patterns to match quoted task names and specific operation formats like "update 'task name' task to 'new name'" and "delete 'task name' task".

## Outcome

- ✅ Impact: The chatbot now correctly identifies and routes different task-related intents (UPDATE, DELETE, SEARCH) instead of defaulting to CREATE_TASK.
- 🧪 Tests: None
- 📁 Files: Modified backend/src/ai/nlp_intent_processor.py to add specific patterns for different task operation intents.
- 🔁 Next prompts: None
- 🧠 Reflection: Specific intent patterns are crucial for accurate natural language processing in task management systems.

## Evaluation notes (flywheel)

- Failure modes observed: Generic patterns were causing all task operations to be classified as CREATE_TASK intent.
- Graders run and results (PASS/FAIL):
- Prompt variant (if applicable):
- Next experiment (smallest change to try): Add fuzzy matching for task titles to improve search accuracy.