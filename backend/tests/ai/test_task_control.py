"""
Unit tests for task control service
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.models.chat_models import UserIntent, IntentType, ExtractedEntity, EntityType
from src.ai.task_control import TaskControl


@pytest.fixture
def task_controller():
    """Create a test instance of the task control service"""
    controller = TaskControl()
    return controller


@pytest.fixture
def mock_task_service():
    """Mock task service for testing"""
    mock_service = Mock()
    mock_service.get_tasks = AsyncMock(return_value=[])
    mock_service.create_task = AsyncMock(return_value=Mock(id="task_123", title="Test Task", completed=False))
    mock_service.update_task = AsyncMock(return_value=Mock(id="task_123", title="Updated Task", completed=True))
    mock_service.delete_task = AsyncMock(return_value=None)
    return mock_service


@pytest.mark.asyncio
class TestTaskCreation:
    """Test task creation functionality"""

    async def test_handle_create_task_basic(self, task_controller):
        """Test basic task creation"""
        # Create a mock intent for creating a task
        intent = UserIntent(
            intent_type=IntentType.CREATE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Buy groceries",
                    confidence_score=0.9
                )
            ]
        )

        # Mock the backend integration to return a successful result
        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "task_id": "task_123",
                             "task_title": "Buy groceries",
                             "response_type": "success"
                         }):

            result = await task_controller._handle_create_task("user_123", intent, None)

        assert result["success"] is True
        assert "Buy groceries" in result["response"]
        assert result["task_id"] == "task_123"
        assert result["task_title"] == "Buy groceries"

    async def test_handle_create_task_with_description(self, task_controller):
        """Test task creation with description"""
        intent = UserIntent(
            intent_type=IntentType.CREATE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Finish report",
                    confidence_score=0.9
                ),
                ExtractedEntity(
                    entity_type=EntityType.TASK_DESCRIPTION,
                    entity_value="Complete the quarterly report",
                    confidence_score=0.8
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "task_id": "task_456",
                             "task_title": "Finish report",
                             "response_type": "success"
                         }):

            result = await task_controller._handle_create_task("user_123", intent, None)

        assert result["success"] is True
        assert "Finish report" in result["response"]

    async def test_handle_create_task_backend_failure(self, task_controller):
        """Test task creation when backend operation fails"""
        intent = UserIntent(
            intent_type=IntentType.CREATE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Buy groceries",
                    confidence_score=0.9
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": False,
                             "error": "Database connection failed",
                             "response_type": "error"
                         }):

            result = await task_controller._handle_create_task("user_123", intent, None)

        assert result["success"] is False
        assert "Database connection failed" in result["response"]


@pytest.mark.asyncio
class TestTaskUpdate:
    """Test task update functionality"""

    async def test_handle_update_task_completion(self, task_controller):
        """Test updating task completion status"""
        intent = UserIntent(
            intent_type=IntentType.UPDATE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Buy groceries",
                    confidence_score=0.9
                ),
                ExtractedEntity(
                    entity_type=EntityType.STATUS_INDICATOR,
                    entity_value="complete",
                    confidence_score=0.8
                )
            ]
        )

        # Mock getting tasks and updating
        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         side_effect=[
                             # First call for get_tasks
                             {
                                 "success": True,
                                 "tasks": [Mock(id="task_123", title="Buy groceries", completed=False)],
                                 "response_type": "success"
                             },
                             # Second call for update_task
                             {
                                 "success": True,
                                 "task_id": "task_123",
                                 "task_title": "Buy groceries",
                                 "response_type": "success"
                             }
                         ]):

            result = await task_controller._handle_update_task("user_123", intent, None)

        assert result["success"] is True
        assert "Buy groceries" in result["response"]
        assert "complete" in result["response"]

    async def test_handle_update_task_title(self, task_controller):
        """Test updating task title"""
        intent = UserIntent(
            intent_type=IntentType.UPDATE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Old task name",
                    confidence_score=0.9
                ),
                # New title would be in description entity or parameters
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         side_effect=[
                             # First call for get_tasks
                             {
                                 "success": True,
                                 "tasks": [Mock(id="task_123", title="Old task name", completed=False)],
                                 "response_type": "success"
                             },
                             # Second call for update_task
                             {
                                 "success": True,
                                 "task_id": "task_123",
                                 "task_title": "New task name",
                                 "response_type": "success"
                             }
                         ]):

            result = await task_controller._handle_update_task("user_123", intent, None)

        assert result["success"] is True

    async def test_handle_update_task_not_found(self, task_controller):
        """Test updating a task that doesn't exist"""
        intent = UserIntent(
            intent_type=IntentType.UPDATE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Non-existent task",
                    confidence_score=0.9
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": [],  # No tasks found
                             "response_type": "success"
                         }):

            result = await task_controller._handle_update_task("user_123", intent, None)

        assert result["success"] is False
        assert "couldn't find a task matching" in result["response"]


@pytest.mark.asyncio
class TestTaskDeletion:
    """Test task deletion functionality"""

    async def test_handle_delete_task(self, task_controller):
        """Test deleting a task"""
        intent = UserIntent(
            intent_type=IntentType.DELETE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Buy groceries",
                    confidence_score=0.9
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         side_effect=[
                             # First call for get_tasks
                             {
                                 "success": True,
                                 "tasks": [Mock(id="task_123", title="Buy groceries", completed=False)],
                                 "response_type": "success"
                             },
                             # Second call for delete_task
                             {
                                 "success": True,
                                 "response_type": "task_deleted"
                             }
                         ]):

            # Simulate confirmed deletion
            session_context = {"confirmed_deletion": True}
            result = await task_controller._handle_delete_task("user_123", intent, session_context)

        assert result["success"] is True
        assert "deleted" in result["response"]

    async def test_handle_delete_task_needs_confirmation(self, task_controller):
        """Test that deleting a task requires confirmation"""
        intent = UserIntent(
            intent_type=IntentType.DELETE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Buy groceries",
                    confidence_score=0.9
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": [Mock(id="task_123", title="Buy groceries", completed=False)],
                             "response_type": "success"
                         }):

            # No confirmation provided in session context
            result = await task_controller._handle_delete_task("user_123", intent, {})

        assert result["success"] is False
        assert result["response_type"] == "confirmation_required"
        assert "Are you sure" in result["response"]

    async def test_handle_delete_task_not_found(self, task_controller):
        """Test deleting a task that doesn't exist"""
        intent = UserIntent(
            intent_type=IntentType.DELETE_TASK,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.TASK_TITLE,
                    entity_value="Non-existent task",
                    confidence_score=0.9
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": [],  # No tasks found
                             "response_type": "success"
                         }):

            result = await task_controller._handle_delete_task("user_123", intent, {"confirmed_deletion": True})

        assert result["success"] is False
        assert "couldn't find a task matching" in result["response"]


@pytest.mark.asyncio
class TestTaskListing:
    """Test task listing functionality"""

    async def test_handle_list_tasks(self, task_controller):
        """Test listing all tasks"""
        intent = UserIntent(
            intent_type=IntentType.LIST_TASKS,
            confidence_score=0.9,
            extracted_entities=[]
        )

        mock_tasks = [
            Mock(id="task_1", title="First task", completed=False),
            Mock(id="task_2", title="Second task", completed=True),
        ]

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": mock_tasks,
                             "response_type": "success"
                         }):

            result = await task_controller._handle_list_tasks("user_123", intent, None)

        assert result["success"] is True
        assert result["task_count"] == 2
        assert "First task" in result["response"]
        assert "Second task" in result["response"]

    async def test_handle_list_completed_tasks(self, task_controller):
        """Test listing completed tasks"""
        intent = UserIntent(
            intent_type=IntentType.LIST_TASKS,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.STATUS_INDICATOR,
                    entity_value="completed",
                    confidence_score=0.8
                )
            ]
        )

        mock_tasks = [
            Mock(id="task_1", title="Completed task", completed=True),
            Mock(id="task_2", title="Incomplete task", completed=False),
        ]

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": mock_tasks,
                             "response_type": "success"
                         }):

            result = await task_controller._handle_list_tasks("user_123", intent, None)

        assert result["success"] is True
        assert "Completed task" in result["response"]
        assert "completed" in result["response"]


@pytest.mark.asyncio
class TestTaskSearching:
    """Test task searching functionality"""

    async def test_handle_search_tasks(self, task_controller):
        """Test searching for tasks by keyword"""
        intent = UserIntent(
            intent_type=IntentType.SEARCH_TASKS,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.KEYWORD,
                    entity_value="groceries",
                    confidence_score=0.9
                )
            ]
        )

        mock_tasks = [
            Mock(id="task_1", title="Buy groceries", completed=False),
            Mock(id="task_2", title="Walk the dog", completed=True),
        ]

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": mock_tasks,
                             "response_type": "success",
                             "matching_count": 1
                         }):

            result = await task_controller._handle_search_tasks("user_123", intent, None)

        assert result["success"] is True
        assert result["matching_count"] == 1
        assert "Buy groceries" in result["response"]

    async def test_handle_search_tasks_no_results(self, task_controller):
        """Test searching for tasks with no matches"""
        intent = UserIntent(
            intent_type=IntentType.SEARCH_TASKS,
            confidence_score=0.9,
            extracted_entities=[
                ExtractedEntity(
                    entity_type=EntityType.KEYWORD,
                    entity_value="nonexistent",
                    confidence_score=0.9
                )
            ]
        )

        with patch.object(task_controller.backend_integration, 'execute_task_operation',
                         return_value={
                             "success": True,
                             "tasks": [],
                             "response_type": "success",
                             "matching_count": 0
                         }):

            result = await task_controller._handle_search_tasks("user_123", intent, None)

        assert result["success"] is False
        assert "couldn't find" in result["response"]


@pytest.mark.asyncio
class TestUserInfo:
    """Test user information functionality"""

    async def test_handle_get_user_info(self, task_controller):
        """Test getting user information"""
        intent = UserIntent(
            intent_type=IntentType.GET_USER_INFO,
            confidence_score=0.9,
            extracted_entities=[],
            parameters={"original_message": "What is my email?"}
        )

        result = await task_controller._handle_get_user_info("user_123", intent, None)

        assert result["success"] is True
        assert "user_123" in result["response"]
        assert result["user_id"] == "user_123"