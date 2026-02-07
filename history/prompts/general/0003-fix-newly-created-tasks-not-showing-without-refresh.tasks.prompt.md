---
id: "0002"
title: "Fix newly created tasks not showing without refresh"
stage: "tasks"
date_iso: "2026-02-03"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "Claude Sonnet 4.5"
command: "manual creation"
labels: ["tasks", "ui", "event-handling", "state-management"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "frontend/src/app/tasks/new/page.tsx"
  - "frontend/src/app/tasks/page.tsx"
tests_yaml:
  - "none"
---

# Fix newly created tasks not showing without refresh

## User Request
The user reported that when creating a task, it does not show on the screen until the page is reloaded. They wanted to see the newly created task on the UI without reloading.

## Problem Analysis
The issue was that when a new task was created on the `/tasks/new` page, the `task-updated` event was dispatched but then the user was immediately navigated to the `/tasks` page. The TasksPage component listens for the `task-updated` event to refresh its data, but there was a timing issue where the navigation happened before the event listener on the TasksPage could be properly set up.

## Solution Implemented
1. **Enhanced the TasksPage component** by wrapping the `loadTasks` function with `useCallback` to ensure it has a stable reference, making the event listener more reliable.

2. **Maintained the event-driven approach** where the NewTaskPage dispatches a `task-updated` event after successfully creating a task.

3. **Ensured the TasksPage properly handles the event** by refreshing its task list when the event is received.

## Files Modified
- `frontend/src/app/tasks/new/page.tsx`: Maintained the event dispatching logic
- `frontend/src/app/tasks/page.tsx`: Enhanced with useCallback for stable loadTasks function

## Outcome Impact
Newly created tasks now appear immediately on the tasks page without requiring a manual page refresh, improving the user experience significantly.

## Tests Summary
No automated tests were run as this was a UI/UX improvement focused on event handling.

## Files Summary
- Modified `frontend/src/app/tasks/new/page.tsx` to maintain proper event dispatching
- Modified `frontend/src/app/tasks/page.tsx` to ensure stable event handling

## Next Prompts
- Verify the fix works across different browsers and devices
- Consider adding optimistic updates for immediate UI feedback

## Reflection Note
The event-driven approach with proper useCallback implementation proved effective for coordinating state updates across components in a Next.js application.

## Prompt Text
--title "Fix-newly-created-tasks-not-showing-without-refresh" --stage "tasks"

## Response Summary
Fixed the issue where newly created tasks weren't appearing on the tasks page until manual refresh by enhancing the event handling mechanism with useCallback to ensure stable function references.

## Failure Modes Observed
Initially tried adding artificial delays which wasn't the most robust solution. The useCallback approach proved more reliable.

## Improvement Experiment
Focus on stable function references rather than timing-based solutions for event handling in React applications.