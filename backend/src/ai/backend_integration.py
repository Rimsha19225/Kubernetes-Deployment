"""
Backend Integration Layer
Handles secure communication between AI and backend systems
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from src.services import task_service
from src.services.auth_service import get_user_by_id
from src.utils.ai_logging import ai_logger
from src.ai.quality_guard import quality_guard

logger = logging.getLogger(__name__)

class BackendIntegration:
    """
    Handles secure communication between AI and backend systems
    """
    def __init__(self):
        # No initialization needed as we'll call functions directly
        pass

    async def execute_task_operation(
        self,
        user_id: str,
        operation: str,
        params: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a task operation against the backend with proper validation
        """
        try:
            # Validate user context and permissions
            validation_result = await self._validate_user_access(
                user_id,
                operation,
                user_context
            )

            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "response_type": "error"
                }

            # Perform the operation based on type
            if operation == "create_task":
                return await self._create_task(user_id, params)
            elif operation == "update_task":
                return await self._update_task(user_id, params)
            elif operation == "delete_task":
                return await self._delete_task(user_id, params)
            elif operation == "get_tasks":
                return await self._get_tasks(user_id, params)
            elif operation == "get_task_by_id":
                return await self._get_task_by_id(user_id, params)
            elif operation == "search_tasks":
                return await self._search_tasks(user_id, params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "response_type": "error"
                }

        except Exception as e:
            ai_logger.log_error("backend_operation_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Operation failed: {str(e)}",
                "response_type": "error"
            }

    def _parse_date(self, date_str: str):
        """
        Parse various date string formats into a datetime object
        """
        import re
        from datetime import datetime

        # If dateutil is available, use it for better parsing
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except ImportError:
            # If dateutil is not available, use basic parsing
            date_str = date_str.strip().lower()

            # Handle month names
            month_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
                'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
                'nov': 11, 'november': 11, 'dec': 12, 'december': 12
            }

            # Pattern: DD Month YYYY or DD Month YY
            pattern1 = r"(\d{1,2})\s+([a-z]+)\s+(\d{2,4})"
            match = re.match(pattern1, date_str)
            if match:
                day = int(match.group(1))
                month_name = match.group(2)
                year = int(match.group(3))

                if month_name in month_map:
                    month = month_map[month_name]
                    # Handle 2-digit years
                    if year < 100:
                        year += 2000 if year < 50 else 1900
                    return datetime(year, month, day)

            # Pattern: MM/DD/YYYY or DD/MM/YYYY (basic format)
            pattern2 = r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})"
            match = re.match(pattern2, date_str)
            if match:
                first = int(match.group(1))
                second = int(match.group(2))
                year = int(match.group(3))

                # Handle 2-digit years
                if year < 100:
                    year += 2000 if year < 50 else 1900

                # Assuming format is DD/MM/YYYY based on typical European format
                if first <= 12 and second <= 12:
                    # Could be either, but if first is > 12, it must be DD/MM/YYYY
                    if first > 12:
                        return datetime(year, second, first)
                    elif second > 12:
                        return datetime(year, first, second)
                    else:
                        # Default to assuming first is month (US format)
                        return datetime(year, first, second)
                elif first <= 12:
                    return datetime(year, first, second)
                else:
                    return datetime(year, second, first)

            # Pattern: YYYY-MM-DD
            pattern3 = r"(\d{4})-(\d{1,2})-(\d{1,2})"
            match = re.match(pattern3, date_str)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                return datetime(year, month, day)

        return None

    async def _validate_user_access(
        self,
        user_id: str,
        operation: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that the user has access to perform the operation
        """
        try:
            # Check if user exists
            user = get_user_by_id(user_id)
            if not user:
                return {
                    "is_valid": False,
                    "error": "User not found"
                }

            # Validate operation-specific permissions
            if operation == "create_task":
                allowed = "create_own_tasks" in user_context.get("permissions", [])
            elif operation == "update_task":
                allowed = "update_own_tasks" in user_context.get("permissions", [])
            elif operation == "delete_task":
                allowed = "delete_own_tasks" in user_context.get("permissions", [])
            elif operation in ["get_tasks", "search_tasks"]:
                allowed = "read_own_tasks" in user_context.get("permissions", [])
            else:
                allowed = False

            if not allowed:
                return {
                    "is_valid": False,
                    "error": "Insufficient permissions"
                }

            return {
                "is_valid": True,
                "error": None
            }

        except Exception as e:
            ai_logger.log_error("user_access_validation_failed", str(e), user_id)
            return {
                "is_valid": False,
                "error": "Access validation failed"
            }

    async def _create_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a task through the backend service
        """
        try:
            # Validate input parameters
            if not params.get("title"):
                return {
                    "success": False,
                    "error": "Task title is required",
                    "response_type": "error"
                }

            # Sanitize input
            due_date_param = params.get("due_date")
            # Parse due date if provided
            parsed_due_date = None
            if due_date_param:
                parsed_due_date = self._parse_date(due_date_param)

            task_data = {
                "title": str(params.get("title", ""))[:255],  # Limit length
                "description": str(params.get("description", ""))[:1000],  # Limit length
                "user_id": user_id,
                "completed": bool(params.get("completed", False)),
                "due_date": parsed_due_date  # Include parsed due date if provided
            }

            # Create the task using the service function
            from src.database.session import get_session
            from src.models.task import TaskCreate

            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                task_create = TaskCreate(
                    title=task_data.get("title", ""),
                    description=task_data.get("description", ""),
                    completed=task_data.get("completed", False),
                    priority=task_data.get("priority", "medium"),
                    due_date=task_data.get("due_date")
                )

                created_task = task_service.create_task(task_create, int(user_id), session)
            finally:
                # Close the session properly
                session.close()

            return {
                "success": True,
                "task_id": created_task.id,
                "task_title": created_task.title,
                "response_type": "success"
            }

        except Exception as e:
            ai_logger.log_error("task_creation_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}",
                "response_type": "error"
            }

    async def _update_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a task through the backend service
        """
        try:
            task_id = params.get("task_id")
            if not task_id:
                return {
                    "success": False,
                    "error": "Task ID is required for update",
                    "response_type": "error"
                }

            # Check if task belongs to user
            from src.database.session import get_session

            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                existing_task = task_service.get_task_by_id(int(task_id), int(user_id), session)
            finally:
                # Close the session properly
                session.close()

            if not existing_task or str(existing_task.user_id) != user_id:
                return {
                    "success": False,
                    "error": "Task not found or access denied",
                    "response_type": "error"
                }

            # Prepare update data
            from src.models.task import TaskUpdate
            update_data = {}
            if "title" in params:
                update_data["title"] = str(params["title"])[:255]
            if "description" in params:
                update_data["description"] = str(params["description"])[:1000]
            if "completed" in params:
                update_data["completed"] = bool(params["completed"])

            # Update the task
            task_update = TaskUpdate(**update_data)

            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                updated_task = task_service.update_task(int(task_id), task_update, int(user_id), session)

                # Extract the needed values before closing the session
                # to avoid SQLAlchemy detached instance errors
                task_id_result = updated_task.id
                task_title_result = updated_task.title
            finally:
                # Close the session properly
                session.close()

            return {
                "success": True,
                "task_id": task_id_result,
                "task_title": task_title_result,
                "response_type": "success",
                "update_action": "updated"
            }

        except Exception as e:
            ai_logger.log_error("task_update_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Failed to update task: {str(e)}",
                "response_type": "error"
            }

    async def _delete_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a task through the backend service
        """
        try:
            task_id = params.get("task_id")
            if not task_id:
                return {
                    "success": False,
                    "error": "Task ID is required for deletion",
                    "response_type": "error"
                }

            # Check if task belongs to user
            from src.database.session import get_session

            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                existing_task = task_service.get_task_by_id(int(task_id), int(user_id), session)
            finally:
                # Close the session properly
                session.close()

            if not existing_task or str(existing_task.user_id) != user_id:
                return {
                    "success": False,
                    "error": "Task not found or access denied",
                    "response_type": "error"
                }

            # Delete the task
            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                result = task_service.delete_task(int(task_id), int(user_id), session)
            finally:
                # Close the session properly
                session.close()

            if not result:
                return {
                    "success": False,
                    "error": "Failed to delete task",
                    "response_type": "error"
                }

            return {
                "success": True,
                "response_type": "task_deleted"
            }

        except Exception as e:
            ai_logger.log_error("task_deletion_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Failed to delete task: {str(e)}",
                "response_type": "error"
            }

    async def _get_task_by_id(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a specific task by ID through the backend service
        """
        try:
            task_id = params.get("task_id")
            if not task_id:
                return {
                    "success": False,
                    "error": "Task ID is required",
                    "response_type": "error"
                }

            # Get the generator and extract the session
            from src.database.session import get_session
            session_gen = get_session()
            session = next(session_gen)
            try:
                existing_task = task_service.get_task_by_id(int(task_id), int(user_id), session)

                # Extract the needed values before closing the session
                # to avoid SQLAlchemy detached instance errors
                if existing_task:
                    task_result = {
                        'id': existing_task.id,
                        'title': existing_task.title,
                        'description': existing_task.description,
                        'completed': existing_task.completed,
                        'user_id': existing_task.user_id,
                        'created_at': existing_task.created_at,
                        'updated_at': existing_task.updated_at
                    }
                else:
                    task_result = None
            finally:
                # Close the session properly
                session.close()

            if not task_result or str(task_result['user_id']) != user_id:
                return {
                    "success": False,
                    "error": "Task not found or access denied",
                    "response_type": "error"
                }

            return {
                "success": True,
                "task": task_result,
                "response_type": "success"
            }

        except Exception as e:
            ai_logger.log_error("task_retrieval_by_id_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Failed to retrieve task: {str(e)}",
                "response_type": "error"
            }

    async def _get_tasks(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get tasks through the backend service
        """
        try:
            # Get all tasks for the user
            from src.database.session import get_session

            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                tasks = task_service.get_tasks(int(user_id), session)

                # Convert tasks to a format that avoids SQLAlchemy detached instance errors
                task_results = []
                for task in tasks:
                    # Create a simple object that mimics the Task model attributes
                    task_obj = type('Task', (), {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'completed': task.completed,
                        'user_id': task.user_id,
                        'created_at': task.created_at,
                        'updated_at': task.updated_at
                    })()
                    task_results.append(task_obj)
            finally:
                # Close the session properly
                session.close()

            # Apply any filters from params
            if params.get("status") == "completed":
                task_results = [task for task in task_results if task.completed]
            elif params.get("status") == "pending":
                task_results = [task for task in task_results if not task.completed]

            return {
                "success": True,
                "tasks": task_results,
                "task_count": len(task_results),
                "response_type": "success"
            }

        except Exception as e:
            ai_logger.log_error("task_retrieval_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Failed to retrieve tasks: {str(e)}",
                "response_type": "error"
            }

    async def _search_tasks(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search tasks through the backend service
        """
        try:
            # First get all tasks for the user
            from src.database.session import get_session

            # Get the generator and extract the session
            session_gen = get_session()
            session = next(session_gen)
            try:
                all_tasks = task_service.get_tasks(int(user_id), session)
            finally:
                # Close the session properly
                session.close()

            # Apply search criteria
            search_term = params.get("search_term", "").lower()
            if not search_term:
                return {
                    "success": False,
                    "error": "Search term is required",
                    "response_type": "error"
                }

            # Filter tasks based on search term
            matching_tasks = []
            for task in all_tasks:
                task_content = f"{task.title} {task.description or ''}".lower()
                if search_term in task_content:
                    matching_tasks.append(task)

            return {
                "success": True,
                "tasks": matching_tasks,
                "matching_count": len(matching_tasks),
                "response_type": "success"
            }

        except Exception as e:
            ai_logger.log_error("task_search_failed", str(e), user_id)
            return {
                "success": False,
                "error": f"Failed to search tasks: {str(e)}",
                "response_type": "error"
            }

    async def validate_api_response(
        self,
        response: Dict[str, Any],
        operation: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate API responses for safety and accuracy
        """
        try:
            # Use quality guard to validate the response
            validation_result = quality_guard.validate_response(
                str(response),
                None,  # We don't have an intent here, but this is for response validation
                user_context,
                response
            )

            return {
                "is_valid": validation_result["is_valid"],
                "issues": validation_result["issues"],
                "sanitized_response": validation_result["sanitized_response"]
            }

        except Exception as e:
            ai_logger.log_error("response_validation_failed", str(e), user_context.get("user_id"))
            return {
                "is_valid": False,
                "issues": ["Error during response validation"],
                "sanitized_response": response
            }


# Global instance of the backend integration service
backend_integration = BackendIntegration()