"""
Task Service Class
Wraps the task service functions in a class for use by AI components
"""
from sqlmodel import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from ..database.session import get_session
from ..models.task import Task, TaskCreate, TaskUpdate
from .task_service import (
    create_task,
    get_tasks,
    get_task_by_id,
    update_task,
    delete_task
)


class TaskService:
    """
    Service class that wraps task operations for use by AI components
    """

    def __init__(self):
        pass

    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task asynchronously
        """
        # Get a database session
        with get_session() as session:
            # Create a TaskCreate object from the data
            task_create = TaskCreate(
                title=task_data["title"],
                description=task_data.get("description", ""),
                completed=task_data.get("completed", False),
                priority=task_data.get("priority", "medium"),
                due_date=task_data.get("due_date")
            )

            # Call the synchronous function
            result = create_task(task_create, task_data["user_id"], session)
            return result

    async def get_tasks(self, user_id: str) -> List[Task]:
        """
        Get all tasks for a user asynchronously
        """
        with get_session() as session:
            # Call the synchronous function
            result = get_tasks(int(user_id), session)
            return result

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID asynchronously
        """
        with get_session() as session:
            # Call the synchronous function
            result = get_task_by_id(int(task_id), int(user_id), session)
            return result

    async def update_task(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Task:
        """
        Update a task asynchronously
        """
        with get_session() as session:
            # Convert update_data to TaskUpdate object
            task_update = TaskUpdate(**update_data)

            # Call the synchronous function
            result = update_task(int(task_id), task_update, int(user_id), session)
            return result

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete a task asynchronously
        """
        with get_session() as session:
            # Call the synchronous function
            result = delete_task(int(task_id), int(user_id), session)
            return result