"""
Response Composer
Formats API results into natural language responses
"""
from typing import Dict, Any, List, Optional
import logging
import re

from src.utils.ai_logging import ai_logger

logger = logging.getLogger(__name__)

class ResponseComposer:
    """
    Formats API results into natural language responses
    """
    def __init__(self):
        self.response_templates = {
            "task_created": [
                "I've created a task '{title}' for you.",
                "Your task '{title}' has been added successfully.",
                "Done! I've added '{title}' to your task list."
            ],
            "task_updated": [
                "I've updated the task '{title}' to be {status}.",
                "Your task '{title}' is now {status}.",
                "Got it! The task '{title}' has been changed to {status}."
            ],
            "task_deleted": [
                "I've removed the task '{title}' from your list.",
                "The task '{title}' has been deleted.",
                "Done! I've deleted '{title}'."
            ],
            "tasks_listed": [
                "You have {count} tasks:\n{tasks}",
                "Here are your {count} tasks:\n{tasks}",
                "I found {count} tasks for you:\n{tasks}"
            ],
            "tasks_searched": [
                "I found {count} tasks containing '{keyword}':\n{tasks}",
                "Here are the {count} tasks matching '{keyword}':\n{tasks}",
                "You have {count} tasks with '{keyword}':\n{tasks}"
            ],
            "user_info": [
                "You are logged in as {email}.",
                "Your email is {email}.",
                "I see you're logged in with {email}."
            ],
            "error": [
                "I'm sorry, but {error}",
                "There was an issue: {error}",
                "Something went wrong: {error}"
            ],
            "clarification_needed": [
                "{request}",
                "Could you clarify: {request}",
                "I need more information: {request}"
            ],
            "confirmation_required": [
                "{request}",
                "Please confirm: {request}",
                "To proceed: {request}"
            ]
        }

    def compose_response(
        self,
        operation_result: Dict[str, Any],
        original_message: str = None
    ) -> str:
        """
        Compose a natural language response based on the operation result
        """
        try:
            success = operation_result.get('success', False)
            response_type = operation_result.get('response_type', 'success')
            response = operation_result.get('response', '')

            # If there's already a specific response, return it
            if response:
                return response

            # Otherwise, compose a response based on the operation result
            if response_type == 'error':
                return self._compose_error_response(operation_result)
            elif response_type == 'clarification_needed':
                return self._compose_clarification_response(operation_result)
            elif response_type == 'confirmation_required':
                return self._compose_confirmation_response(operation_result)
            elif success:
                return self._compose_success_response(operation_result)
            else:
                return "I'm not sure what happened. Could you try rephrasing that?"

        except Exception as e:
            ai_logger.log_error("response_composition_failed", str(e))
            return "I apologize, but I had trouble processing that response."

    def _compose_success_response(self, result: Dict[str, Any]) -> str:
        """
        Compose a success response based on the operation result
        """
        try:
            if 'task_title' in result:
                if result.get('task_id'):
                    if result.get('response_type') == 'task_deleted':
                        return f"I've removed the task '{result['task_title']}' from your list."
                    elif 'completed' in result or result.get('response_type') == 'task_updated':
                        status = "complete" if result.get('completed', False) else "incomplete"
                        action = result.get('update_action', 'updated')
                        return f"I've {action} the task '{result['task_title']}' to be {status}."
                    else:
                        return f"I've created a task '{result['task_title']}' for you."

            if 'task_count' in result:
                count = result['task_count']
                if count == 0:
                    return "You don't have any tasks yet."

                tasks = result.get('tasks', [])
                task_list = self._format_task_list(tasks)

                # Check if this is a filtered result
                if result.get('response_type') == 'task_filtered':
                    status = result.get('filter_status', 'specified')
                    response = f"You have {count} {status} tasks:\n{task_list}"
                else:
                    response = f"You have {count} tasks:\n{task_list}"

                # If this was a request to show the task list, add navigation suggestion
                if result.get('request_type') == 'show_task_list':
                    response += "\n\nYou can also view all your tasks on the task dashboard."

                return response

            if 'matching_count' in result:
                count = result['matching_count']
                keyword = result.get('keyword', 'the search term')
                tasks = result.get('tasks', [])
                task_list = self._format_task_list(tasks)

                # Check if this is a filtered search result
                if result.get('filter_status'):
                    status = result['filter_status']
                    return f"I found {count} {status} tasks containing '{keyword}':\n{task_list}"
                else:
                    return f"I found {count} tasks containing '{keyword}':\n{task_list}"

            if 'user_id' in result:
                if 'email' in result:
                    return f"You are logged in as {result['email']}."
                else:
                    return f"You are logged in with user ID: {result['user_id']}."

            # Default success message
            return "Your request was processed successfully."

        except Exception as e:
            ai_logger.log_error("success_response_composition_failed", str(e))
            return "The operation was successful, but I couldn't format the response properly."

    def _compose_error_response(self, result: Dict[str, Any]) -> str:
        """
        Compose an error response
        """
        try:
            error_msg = result.get('response', result.get('error', 'an unknown error occurred'))

            # Handle specific error types with more user-friendly messages
            error_lower = error_msg.lower()
            if 'not found' in error_lower or 'does not exist' in error_lower:
                return f"Sorry, I couldn't find what you were looking for: {error_msg}"
            elif 'permission' in error_lower or 'unauthorized' in error_lower:
                return f"I'm sorry, but you don't have permission to perform this action."
            elif 'duplicate' in error_lower or 'already exists' in error_lower:
                return f"It looks like that already exists. Is there something else I can help you with?"
            elif 'required' in error_lower or 'missing' in error_lower:
                return f"I need more information to complete this request: {error_msg}"
            elif 'connection' in error_lower or 'timeout' in error_lower:
                return f"I'm having trouble connecting to the service right now. Please try again in a moment."
            else:
                return f"Sorry, I couldn't complete that action: {error_msg}"
        except Exception as e:
            ai_logger.log_error("error_response_composition_failed", str(e))
            return "Sorry, there was an error processing your request."

    def _compose_clarification_response(self, result: Dict[str, Any]) -> str:
        """
        Compose a clarification-needed response
        """
        try:
            request = result.get('response', 'Could you please be more specific?')
            return request
        except Exception as e:
            ai_logger.log_error("clarification_response_composition_failed", str(e))
            return "I need more information to help you with that."

    def _compose_confirmation_response(self, result: Dict[str, Any]) -> str:
        """
        Compose a confirmation-required response
        """
        try:
            request = result.get('response', 'Please confirm this action.')
            return request
        except Exception as e:
            ai_logger.log_error("confirmation_response_composition_failed", str(e))
            return "I need your confirmation before proceeding."

    def _format_task_list(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Format a list of tasks into a readable string
        """
        try:
            if not tasks:
                return "No tasks found."

            formatted_tasks = []
            for task in tasks[:10]:  # Limit to 10 tasks to avoid long responses
                if isinstance(task, dict):
                    title = task.get('title', 'Untitled')
                    completed = task.get('completed', False)
                else:
                    # If task is a model object, access its properties
                    title = getattr(task, 'title', 'Untitled')
                    completed = getattr(task, 'completed', False)

                status_icon = "✓" if completed else "○"
                formatted_tasks.append(f"{status_icon} {title}")

            if len(tasks) > 10:
                formatted_tasks.append(f"... and {len(tasks) - 10} more")

            return "\n".join(formatted_tasks)

        except Exception as e:
            ai_logger.log_error("task_list_formatting_failed", str(e))
            return "Error formatting task list."

    def add_suggestions(self, response: str, operation_result: Dict[str, Any]) -> List[str]:
        """
        Add helpful suggestions based on the operation result
        """
        suggestions = []

        try:
            response_type = operation_result.get('response_type', 'success')

            if response_type == 'success':
                if 'task_id' in operation_result:
                    # If a task was created, suggest next actions
                    suggestions.extend([
                        "Would you like to set a due date for this task?",
                        "Do you want to add a description to this task?",
                        "I can also mark this task as completed if you've finished it."
                    ])
                elif operation_result.get('task_count', 0) > 0:
                    # If tasks were listed, suggest filtering
                    suggestions.extend([
                        "You can ask me to show only completed tasks",
                        "Would you like to search for specific tasks?",
                        "I can sort your tasks by title or date if you'd like"
                    ])
            elif response_type == 'clarification_needed':
                # If clarification was needed, suggest common alternatives
                suggestions.extend([
                    "Try being more specific about which task you mean",
                    "You can refer to tasks by their exact title",
                    "Use keywords that appear in the task title or description"
                ])
            elif response_type == 'confirmation_required':
                # If confirmation was required, suggest how to proceed
                suggestions.extend([
                    "Say 'yes' to confirm this action",
                    "Say 'no' or 'cancel' to abort",
                    "You can also ask me to show you the task before deleting"
                ])

        except Exception as e:
            ai_logger.log_error("suggestions_generation_failed", str(e))

        return suggestions


# Global instance of the response composer
response_composer = ResponseComposer()