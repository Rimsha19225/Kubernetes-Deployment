"""
Task Control
Translates AI intents to specific Phase 2 task operations
"""
from typing import Dict, Any, Optional, List
import logging
import re
from datetime import datetime

from src.models.chat_models import UserIntent, IntentType, ExtractedEntity
from src.ai.backend_integration import backend_integration
from src.models.task import Task
from src.utils.ai_logging import ai_logger

logger = logging.getLogger(__name__)

class TaskControl:
    """
    Translates AI intents to specific Phase 2 task operations
    """
    def __init__(self):
        self.backend_integration = backend_integration

    async def execute_intent(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the appropriate task operation based on the identified intent
        """
        with ai_logger.measure_duration("execute_intent", user_id):
            if intent.intent_type == IntentType.CREATE_TASK:
                return await self._handle_create_task(user_id, intent, session_context)
            elif intent.intent_type == IntentType.UPDATE_TASK:
                return await self._handle_update_task(user_id, intent, session_context)
            elif intent.intent_type == IntentType.DELETE_TASK:
                return await self._handle_delete_task(user_id, intent, session_context)
            elif intent.intent_type == IntentType.LIST_TASKS:
                return await self._handle_list_tasks(user_id, intent, session_context)
            elif intent.intent_type == IntentType.SEARCH_TASKS:
                return await self._handle_search_tasks(user_id, intent, session_context)
            elif intent.intent_type == IntentType.GET_USER_INFO:
                return await self._handle_get_user_info(user_id, intent, session_context)
            else:
                return {
                    "success": False,
                    "response": "Sorry, I didn't understand that request.",
                    "response_type": "error"
                }

    async def _handle_create_task(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle task creation based on intent and extracted entities
        """
        try:
            # Extract title, description, and due date from entities
            title = None
            description = None
            due_date = None

            for entity in intent.extracted_entities:
                if entity.entity_type == "TASK_TITLE" and not title:
                    title = entity.entity_value
                elif entity.entity_type == "TASK_DESCRIPTION":
                    description = entity.entity_value
                elif entity.entity_type == "DATE_REFERENCE":
                    due_date = entity.entity_value

            # If we don't have a title, try to construct one from the original message
            if not title:
                original_message = intent.parameters.get("original_message", "").lower().strip()
                original_message_full = intent.parameters.get("original_message", "")

                # Define generic phrases that should result in "New Task"
                generic_phrases = [
                    "create a task", "add a task", "make a task",
                    "create task", "add task", "make task"
                ]

                if original_message in generic_phrases:
                    # If the message is just a generic request without specific content, use "New Task"
                    title = "New Task"
                else:
                    # For more specific messages, try to extract content
                    # Check if the message follows a pattern like "create task to <do something>"
                    # Look for patterns like "create task to <content>", "add task to <content>", etc.
                    patterns = [
                        r"(?:create|add|make)\s+(?:a\s+)?task\s+(?:to|called|for)\s+(.+)",
                        r"i\s+need\s+to\s+(.+)",
                        r"i\s+want\s+to\s+(.+)",
                        r"to\s+(.+)"
                    ]

                    extracted_content = None
                    for pattern in patterns:
                        match = re.search(pattern, original_message)
                        if match:
                            extracted_content = match.group(1).strip()
                            break

                    if extracted_content and len(extracted_content) > 0:
                        # Find the extracted content in the original message and get the original casing
                        original_lower = original_message_full.lower()
                        pos = original_lower.find(extracted_content.lower())
                        if pos != -1:
                            title = original_message_full[pos:pos+len(extracted_content)]
                        else:
                            title = extracted_content
                    else:
                        # If we couldn't extract specific content, use the original message but strip generic parts
                        title = original_message_full.strip()

            # Prepare parameters for backend integration
            params = {
                "title": title,
                "description": description or "",
                "due_date": due_date
            }

            # Call the backend integration layer to create the task
            result = await self.backend_integration.execute_task_operation(
                user_id=user_id,
                operation="create_task",
                params=params,
                user_context={"user_id": user_id, "permissions": ["create_own_tasks"]}
            )

            if result["success"]:
                response = f"I've created a task '{result['task_title']}' for you."

                ai_logger.logger.info(f"Task created: {result['task_id']} for user {user_id}")

                return {
                    "success": True,
                    "response": response,
                    "response_type": "success",
                    "task_id": result['task_id'],
                    "task_title": result['task_title']
                }
            else:
                return {
                    "success": False,
                    "response": f"Sorry, I couldn't create the task: {result.get('error', 'Unknown error')}",
                    "response_type": "error"
                }

        except Exception as e:
            ai_logger.log_error("task_creation_failed", str(e), user_id)
            return {
                "success": False,
                "response": f"Sorry, I couldn't create the task: {str(e)}",
                "response_type": "error"
            }

    async def _handle_update_task(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle task update based on intent and extracted entities
        """
        try:
            # Extract task reference and update details
            task_reference = None
            task_id = None
            new_title = None
            new_description = None
            new_status = None

            for entity in intent.extracted_entities:
                if entity.entity_type == "TASK_ID":
                    task_id = entity.entity_value
                elif entity.entity_type == "TASK_TITLE":
                    task_reference = entity.entity_value
                elif entity.entity_type == "TASK_UPDATE_VALUE":
                    # This is the new value for title or description based on the context
                    # Check if the original message contains "title" to decide
                    original_message = intent.parameters.get("original_message", "").lower()
                    if "title" in original_message:
                        new_title = entity.entity_value
                    elif "description" in original_message:
                        new_description = entity.entity_value
                    else:
                        # Default to updating the title if not specified
                        new_title = entity.entity_value
                elif entity.entity_type == "TASK_DESCRIPTION":
                    new_description = entity.entity_value
                elif entity.entity_type == "STATUS_INDICATOR":
                    new_status = entity.entity_value == "complete"

            # If task_id is explicitly provided, try to find that specific task directly
            target_task = None
            if task_id:
                try:
                    # Try to get the specific task by ID using backend integration
                    get_specific_params = {"task_id": int(task_id)}
                    specific_task_result = await self.backend_integration.execute_task_operation(
                        user_id=user_id,
                        operation="get_task_by_id",
                        params=get_specific_params,
                        user_context={"user_id": user_id, "permissions": ["read_own_tasks"]}
                    )

                    if specific_task_result["success"]:
                        target_task = specific_task_result.get("task")
                    else:
                        # If specific task retrieval fails, fall back to getting all tasks
                        pass
                except ValueError:
                    # If task_id is not a valid integer, fall back to normal lookup
                    pass

            # If no explicit task ID was provided or it failed, try other methods
            if not target_task:
                # Find the task to update using backend integration
                get_params = {}
                tasks_result = await self.backend_integration.execute_task_operation(
                    user_id=user_id,
                    operation="get_tasks",
                    params=get_params,
                    user_context={"user_id": user_id, "permissions": ["read_own_tasks"]}
                )

                if not tasks_result["success"]:
                    return {
                        "success": False,
                        "response": f"Sorry, I couldn't retrieve your tasks: {tasks_result.get('error', 'Unknown error')}",
                        "response_type": "error"
                    }

                tasks = tasks_result.get("tasks", [])

                # Try to match the task reference to an existing task
                if task_reference:
                    for task in tasks:
                        if (task_reference.lower() in task.title.lower() or
                            task_reference.lower() in (task.description or "").lower()):
                            target_task = task
                            break

                # If we didn't find a task by reference, try to identify by other entities
                if not target_task:
                    # Check for reference demonstratives like "first", "last", "that", etc.
                    for entity in intent.extracted_entities:
                        if entity.entity_type == "REFERENCE_DEMONSTRATIVE":
                            if entity.entity_value == "last" or entity.entity_value == "recent":
                                if tasks:
                                    target_task = tasks[-1]  # Last task
                            elif entity.entity_value == "first":
                                if tasks:
                                    target_task = tasks[0]  # First task
                            elif entity.entity_value == "that" or entity.entity_value == "this":
                                # Use session context to identify the last referenced task
                                if session_context and "last_referenced_task_id" in session_context:
                                    for task in tasks:
                                        if task.id == session_context["last_referenced_task_id"]:
                                            target_task = task
                                            break
                                # If no last referenced task, use the most recent task
                                elif tasks:
                                    target_task = tasks[-1]  # Most recent task

            if not target_task:
                # If we couldn't find a specific task, ask for clarification
                return {
                    "success": False,
                    "response": f"I couldn't find a task matching your request. Could you be more specific?",
                    "response_type": "clarification_needed"
                }

            # Prepare update parameters for backend integration
            update_params = {
                "task_id": target_task.id
            }
            if new_title:
                update_params["title"] = new_title
            if new_description:
                update_params["description"] = new_description
            if new_status is not None:
                update_params["completed"] = new_status

            # Update the task via backend integration
            update_result = await self.backend_integration.execute_task_operation(
                user_id=user_id,
                operation="update_task",
                params=update_params,
                user_context={"user_id": user_id, "permissions": ["update_own_tasks"]}
            )

            if update_result["success"]:
                status_str = "completed" if (new_status if new_status is not None else getattr(target_task, 'completed', False)) else "incomplete"
                response = f"I've updated the task '{update_result.get('task_title', target_task.title)}' to be {status_str}."

                ai_logger.logger.info(f"Task updated: {target_task.id} for user {user_id}")

                return {
                    "success": True,
                    "response": response,
                    "response_type": "success",
                    "task_id": target_task.id,
                    "task_title": update_result.get('task_title', target_task.title),
                    "update_action": "updated"
                }
            else:
                return {
                    "success": False,
                    "response": f"Sorry, I couldn't update the task: {update_result.get('error', 'Unknown error')}",
                    "response_type": "error"
                }

        except Exception as e:
            ai_logger.log_error("task_update_failed", str(e), user_id)
            return {
                "success": False,
                "response": f"Sorry, I couldn't update the task: {str(e)}",
                "response_type": "error"
            }

    async def _handle_delete_task(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle task deletion based on intent and extracted entities
        """
        try:
            # Extract task reference
            task_reference = None
            for entity in intent.extracted_entities:
                if entity.entity_type == "TASK_TITLE":
                    task_reference = entity.entity_value

            # Find the task to delete using backend integration
            get_params = {}
            tasks_result = await self.backend_integration.execute_task_operation(
                user_id=user_id,
                operation="get_tasks",
                params=get_params,
                user_context={"user_id": user_id, "permissions": ["read_own_tasks"]}
            )

            if not tasks_result["success"]:
                return {
                    "success": False,
                    "response": f"Sorry, I couldn't retrieve your tasks: {tasks_result.get('error', 'Unknown error')}",
                    "response_type": "error"
                }

            tasks = tasks_result.get("tasks", [])
            target_task = None

            # Try to match the task reference to an existing task
            for task in tasks:
                if task_reference and (task_reference.lower() in task.title.lower() or
                                      task_reference.lower() in (task.description or "").lower()):
                    target_task = task
                    break

            if not target_task:
                # If we couldn't find a specific task, ask for clarification
                return {
                    "success": False,
                    "response": f"I couldn't find a task matching your request. Could you be more specific?",
                    "response_type": "clarification_needed"
                }

            # Check if this is a confirmation of deletion
            is_confirmed = (
                session_context and
                session_context.get("confirmed_deletion") or
                session_context and
                session_context.get("pending_actions", {}).get("confirmed_action") == "delete_task"
            )

            # For safety, ask for confirmation before deleting if not already confirmed
            if not is_confirmed:
                return {
                    "success": False,
                    "response": f"Are you sure you want to delete the task '{target_task.title}'? Please respond with 'Yes' or 'No'.",
                    "response_type": "confirmation_required",
                    "pending_action": "delete_task",
                    "task_id": target_task.id
                }

            # Delete the task via backend integration
            delete_params = {
                "task_id": target_task.id
            }

            delete_result = await self.backend_integration.execute_task_operation(
                user_id=user_id,
                operation="delete_task",
                params=delete_params,
                user_context={"user_id": user_id, "permissions": ["delete_own_tasks"]}
            )

            if delete_result["success"]:
                response = f"I've deleted the task '{target_task.title}'."

                ai_logger.logger.info(f"Task deleted: {target_task.id} for user {user_id}")

                return {
                    "success": True,
                    "response": response,
                    "response_type": "task_deleted",
                    "task_id": target_task.id
                }
            else:
                return {
                    "success": False,
                    "response": f"Sorry, I couldn't delete the task: {delete_result.get('error', 'Unknown error')}",
                    "response_type": "error"
                }

        except Exception as e:
            ai_logger.log_error("task_deletion_failed", str(e), user_id)
            return {
                "success": False,
                "response": f"Sorry, I couldn't delete the task: {str(e)}",
                "response_type": "error"
            }

    async def _handle_list_tasks(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle task listing based on intent
        """
        try:
            # Apply filters if specified in entities
            params = {}
            for entity in intent.extracted_entities:
                if entity.entity_type == "STATUS_INDICATOR":
                    status_filter = entity.entity_value
                    if status_filter in ["completed", "done", "finished"]:
                        params["status"] = "completed"
                    elif status_filter in ["pending", "incomplete", "not done"]:
                        params["status"] = "pending"

            # Get tasks using backend integration
            tasks_result = await self.backend_integration.execute_task_operation(
                user_id=user_id,
                operation="get_tasks",
                params=params,
                user_context={"user_id": user_id, "permissions": ["read_own_tasks"]}
            )

            if not tasks_result["success"]:
                return {
                    "success": False,
                    "response": f"Sorry, I couldn't retrieve your tasks: {tasks_result.get('error', 'Unknown error')}",
                    "response_type": "error"
                }

            all_tasks = tasks_result.get("tasks", [])

            # Apply filters based on the parameters
            if params.get("status") == "completed":
                filtered_tasks = [task for task in all_tasks if task.completed]
            elif params.get("status") == "pending":
                filtered_tasks = [task for task in all_tasks if not task.completed]
            else:
                filtered_tasks = all_tasks

            # Check if the original message was to show the task list specifically
            original_message = intent.parameters.get("original_message", "").lower()
            is_show_task_list_request = "show" in original_message and ("task list" in original_message or "task" in original_message and "list" in original_message)

            if not filtered_tasks:
                if params.get("status"):
                    status_desc = params["status"]
                    response = f"You don't have any {status_desc} tasks."
                else:
                    response = "You don't have any tasks yet."
            else:
                task_list = []
                for task in filtered_tasks[:10]:  # Limit to first 10 tasks to avoid long responses
                    status = "✓" if task.completed else "○"
                    task_list.append(f"{status} {task.title}")

                if len(filtered_tasks) > 10:
                    if params.get("status"):
                        status_desc = params["status"]
                        response = f"You have {len(filtered_tasks)} {status_desc} tasks. Here are the first 10:\n" + "\n".join(task_list)
                    else:
                        response = f"You have {len(filtered_tasks)} tasks. Here are the first 10:\n" + "\n".join(task_list)
                else:
                    if params.get("status"):
                        status_desc = params["status"]
                        response = f"You have {len(filtered_tasks)} {status_desc} tasks:\n" + "\n".join(task_list)
                    else:
                        response = f"You have {len(filtered_tasks)} tasks:\n" + "\n".join(task_list)

            ai_logger.logger.info(f"Listed {len(filtered_tasks)} tasks for user {user_id} (filtered from {len(all_tasks)})")

            result_data = {
                "success": True,
                "response": response,
                "response_type": "success",
                "task_count": len(filtered_tasks),
                "tasks": filtered_tasks  # Include tasks for potential further processing
            }

            # Add request type if this was a show task list request
            if is_show_task_list_request:
                result_data["request_type"] = "show_task_list"

            return result_data
        except Exception as e:
            ai_logger.log_error("task_listing_failed", str(e), user_id)
            return {
                "success": False,
                "response": f"Sorry, I couldn't retrieve your tasks: {str(e)}",
                "response_type": "error"
            }

    async def _handle_search_tasks(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle task search based on intent and extracted entities
        """
        try:
            # Extract search keywords
            keywords = []
            status_filters = []

            for entity in intent.extracted_entities:
                if entity.entity_type == "KEYWORD":
                    keywords.append(entity.entity_value)
                elif entity.entity_type == "STATUS_INDICATOR":
                    status_filters.append(entity.entity_value)

            if not keywords:
                return {
                    "success": False,
                    "response": "What would you like to search for?",
                    "response_type": "clarification_needed"
                }

            # Search tasks using backend integration
            search_params = {
                "search_term": keywords[0]  # Use first keyword for search
            }

            if status_filters:
                if status_filters[0] in ["completed", "done", "finished"]:
                    search_params["status"] = "completed"
                elif status_filters[0] in ["pending", "incomplete", "not done"]:
                    search_params["status"] = "pending"

            search_result = await self.backend_integration.execute_task_operation(
                user_id=user_id,
                operation="search_tasks",
                params=search_params,
                user_context={"user_id": user_id, "permissions": ["read_own_tasks"]}
            )

            if not search_result["success"]:
                return {
                    "success": False,
                    "response": f"Sorry, I couldn't search your tasks: {search_result.get('error', 'Unknown error')}",
                    "response_type": "error"
                }

            matching_tasks = search_result.get("tasks", [])

            if not matching_tasks:
                if status_filters:
                    response = f"I couldn't find any {status_filters[0]} tasks containing {' or '.join(keywords)}."
                else:
                    response = f"I couldn't find any tasks containing {' or '.join(keywords)}."
            else:
                task_list = []
                for task in matching_tasks[:10]:  # Limit to first 10 tasks
                    status = "✓" if task.completed else "○"
                    task_list.append(f"{status} {task.title}")

                if len(matching_tasks) > 10:
                    if status_filters:
                        response = f"I found {len(matching_tasks)} {status_filters[0]} tasks containing {keywords[0]}. Here are the first 10:\n" + "\n".join(task_list)
                    else:
                        response = f"I found {len(matching_tasks)} tasks containing {keywords[0]}. Here are the first 10:\n" + "\n".join(task_list)
                else:
                    if status_filters:
                        response = f"I found {len(matching_tasks)} {status_filters[0]} tasks containing {keywords[0]}:\n" + "\n".join(task_list)
                    else:
                        response = f"I found {len(matching_tasks)} tasks containing {keywords[0]}:\n" + "\n".join(task_list)

            ai_logger.logger.info(f"Searched tasks for keywords {keywords} with status filters {status_filters}, found {len(matching_tasks)} matches for user {user_id}")

            return {
                "success": True,
                "response": response,
                "response_type": "success",
                "matching_count": len(matching_tasks),
                "keyword": keywords[0] if keywords else None,
                "tasks": matching_tasks  # Include tasks for response composition
            }
        except Exception as e:
            ai_logger.log_error("task_search_failed", str(e), user_id)
            return {
                "success": False,
                "response": f"Sorry, I couldn't search your tasks: {str(e)}",
                "response_type": "error"
            }

    async def _handle_get_user_info(
        self,
        user_id: str,
        intent: UserIntent,
        session_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle user information requests
        """
        try:
            # Add safety check for intent object itself
            if intent is None:
                ai_logger.log_error("user_info_retrieval_failed", "Intent object is None", user_id)
                return {
                    "success": False,
                    "response": "I'm sorry, but I encountered an error processing your request.",
                    "response_type": "error"
                }

            # Add safety check for user_id
            if not user_id:
                ai_logger.log_error("user_info_retrieval_failed", "User ID is empty or None", user_id)
                return {
                    "success": False,
                    "response": "I'm sorry, but I encountered an error processing your request.",
                    "response_type": "error"
                }

            # Fetch actual user information from the database using the auth service
            try:
                from src.services.auth_service import get_user_by_id
                user = get_user_by_id(user_id)
            except Exception as db_error:
                ai_logger.log_error("user_retrieval_db_error", str(db_error), user_id)
                return {
                    "success": False,
                    "response": "I'm sorry, but I encountered an error processing your request.",
                    "response_type": "error"
                }

            # Add additional check to ensure user is a proper User object
            if user is None:
                # User not found in database
                response = f"Sorry, I couldn't find your user information. You may need to log in again."
                # Return success=True because the operation completed successfully,
                # even though the user wasn't found in the database
                return {
                    "success": True,
                    "response": response,
                    "response_type": "info",  # Changed from "error" to "info"
                    "user_id": user_id
                }

            # Double-check that user is a valid User object before accessing attributes
            if not hasattr(user, 'name') or not hasattr(user, 'email'):
                # User object doesn't have expected attributes
                response = f"Sorry, I couldn't retrieve your user information properly."
                return {
                    "success": True,
                    "response": response,
                    "response_type": "info",
                    "user_id": user_id
                }

            try:
                # Extract requested information based on the intent
                # Add safety check for intent.parameters access
                original_message = ""
                if hasattr(intent, 'parameters') and intent.parameters is not None:
                    original_message = intent.parameters.get("original_message", "")

                message_lower = original_message.lower()

                # Check if user asked for name specifically
                if "name" in message_lower or "username" in message_lower:
                    # Safely access user attributes with fallbacks
                    user_name = getattr(user, 'name', None)
                    user_email = getattr(user, 'email', None)

                    if user_name and user_email:
                        # Show both name and email when asked for name
                        response = f"Your name is {user_name} and your email is {user_email}"
                    elif user_name:
                        response = f"Your name is {user_name}"
                    elif user_email:
                        response = f"Your email is {user_email}"
                    else:
                        # Neither name nor email available
                        response = f"You are logged in as user_{user_id}@example.com"
                elif "email" in message_lower:
                    user_email = getattr(user, 'email', f"user_{user_id}@example.com")
                    response = f"Your email is {user_email}"
                else:
                    # Default to showing both name and email
                    user_name = getattr(user, 'name', f"user_{user_id}")
                    user_email = getattr(user, 'email', f"user_{user_id}@example.com")
                    response = f"You are logged in as {user_name} ({user_email})"

                ai_logger.logger.info(f"Retrieved user info for user {user_id}")

                return {
                    "success": True,
                    "response": response,
                    "response_type": "success",
                    "user_id": user_id,
                    "email": getattr(user, 'email', f"user_{user_id}@example.com")
                }
            except AttributeError as attr_error:
                # Specific error for attribute access issues
                ai_logger.log_error("user_attribute_access_failed", str(attr_error), user_id)
                response = f"Sorry, I couldn't retrieve your user information properly."
                return {
                    "success": True,
                    "response": response,
                    "response_type": "info",
                    "user_id": user_id
                }

        except Exception as e:
            ai_logger.log_error("user_info_retrieval_failed", str(e), user_id)
            return {
                "success": False,
                "response": "I'm sorry, but I encountered an error processing your request.",
                "response_type": "error"
            }


# Global instance of the task control service
task_controller = TaskControl()