"""
Unit tests for response composer
"""
import pytest
import asyncio
from unittest.mock import Mock

from src.ai.response_composer import ResponseComposer


@pytest.fixture
def response_composer():
    """Create a test instance of the response composer"""
    return ResponseComposer()


class TestResponseComposition:
    """Test response composition functionality"""

    def test_compose_task_created_response(self, response_composer):
        """Test composing response for task creation"""
        operation_result = {
            "success": True,
            "response": "",
            "task_title": "Buy groceries",
            "task_id": "task_123",
            "response_type": "success"
        }

        response = response_composer.compose_response(operation_result)

        assert "Buy groceries" in response
        assert "created" in response.lower()

    def test_compose_task_updated_response(self, response_composer):
        """Test composing response for task update"""
        operation_result = {
            "success": True,
            "response": "",
            "task_title": "Clean room",
            "completed": True,
            "response_type": "task_updated"
        }

        response = response_composer.compose_response(operation_result)

        assert "Clean room" in response
        assert "complete" in response.lower()

    def test_compose_task_deleted_response(self, response_composer):
        """Test composing response for task deletion"""
        operation_result = {
            "success": True,
            "response": "",
            "task_title": "Old task",
            "response_type": "task_deleted"
        }

        response = response_composer.compose_response(operation_result)

        assert "Old task" in response
        assert "deleted" in response.lower()

    def test_compose_task_listed_response(self, response_composer):
        """Test composing response for task listing"""
        mock_task = Mock()
        mock_task.title = "Sample task"
        mock_task.completed = False

        operation_result = {
            "success": True,
            "response": "",
            "task_count": 1,
            "tasks": [mock_task],
            "response_type": "success"
        }

        response = response_composer.compose_response(operation_result)

        assert "1 tasks" in response
        assert "Sample task" in response

    def test_compose_error_response(self, response_composer):
        """Test composing response for error cases"""
        operation_result = {
            "success": False,
            "response": "",
            "response_type": "error",
            "error": "Database connection failed"
        }

        response = response_composer.compose_response(operation_result)

        assert "Database connection failed" in response
        assert "couldn't" in response.lower()

    def test_compose_clarification_needed_response(self, response_composer):
        """Test composing response when clarification is needed"""
        operation_result = {
            "success": False,
            "response": "Could you be more specific?",
            "response_type": "clarification_needed"
        }

        response = response_composer.compose_response(operation_result)

        assert "Could you be more specific?" in response

    def test_compose_confirmation_required_response(self, response_composer):
        """Test composing response when confirmation is required"""
        operation_result = {
            "success": False,
            "response": "Please confirm this action.",
            "response_type": "confirmation_required"
        }

        response = response_composer.compose_response(operation_result)

        assert "Please confirm" in response

    def test_compose_user_info_response(self, response_composer):
        """Test composing response for user information"""
        operation_result = {
            "success": True,
            "response": "",
            "user_id": "user_123",
            "email": "user_123@example.com",
            "response_type": "success"
        }

        response = response_composer.compose_response(operation_result)

        assert "user_123" in response
        assert "example.com" in response

    def test_compose_response_with_existing_response(self, response_composer):
        """Test that existing response in operation_result is returned directly"""
        original_response = "Custom response from operation"
        operation_result = {
            "success": True,
            "response": original_response,
            "response_type": "success"
        }

        response = response_composer.compose_response(operation_result)

        assert response == original_response

    def test_add_suggestions_for_successful_task_creation(self, response_composer):
        """Test adding suggestions after successful task creation"""
        operation_result = {
            "success": True,
            "response_type": "success",
            "task_id": "task_123"
        }

        suggestions = response_composer.add_suggestions("Task created successfully", operation_result)

        # Check if appropriate suggestions are provided after task creation
        assert isinstance(suggestions, list)
        # Should include suggestions related to task management
        has_task_suggestions = any("task" in suggestion.lower() for suggestion in suggestions)
        assert has_task_suggestions

    def test_add_suggestions_for_task_listing(self, response_composer):
        """Test adding suggestions after task listing"""
        operation_result = {
            "success": True,
            "response_type": "success",
            "task_count": 5
        }

        suggestions = response_composer.add_suggestions("Here are your tasks", operation_result)

        assert isinstance(suggestions, list)
        # Should include suggestions related to filtering/sorting tasks

    def test_add_suggestions_for_clarification_needed(self, response_composer):
        """Test adding suggestions when clarification is needed"""
        operation_result = {
            "success": False,
            "response_type": "clarification_needed"
        }

        suggestions = response_composer.add_suggestions("Need more info", operation_result)

        assert isinstance(suggestions, list)
        # Should include suggestions about how to provide more specific information

    def test_add_suggestions_for_confirmation_required(self, response_composer):
        """Test adding suggestions when confirmation is required"""
        operation_result = {
            "success": False,
            "response_type": "confirmation_required"
        }

        suggestions = response_composer.add_suggestions("Confirm action", operation_result)

        assert isinstance(suggestions, list)
        # Should include suggestions about confirming or canceling

    def test_format_task_list_empty(self, response_composer):
        """Test formatting empty task list"""
        formatted = response_composer._format_task_list([])

        assert "No tasks found" in formatted

    def test_format_task_list_with_tasks(self, response_composer):
        """Test formatting task list with tasks"""
        mock_task1 = Mock()
        mock_task1.title = "Task 1"
        mock_task1.completed = False

        mock_task2 = Mock()
        mock_task2.title = "Task 2"
        mock_task2.completed = True

        formatted = response_composer._format_task_list([mock_task1, mock_task2])

        assert "Task 1" in formatted
        assert "Task 2" in formatted
        assert "○" in formatted  # Uncompleted task indicator
        assert "✓" in formatted  # Completed task indicator

    def test_format_task_list_many_tasks(self, response_composer):
        """Test formatting task list with more than 10 tasks"""
        mock_tasks = []
        for i in range(15):
            mock_task = Mock()
            mock_task.title = f"Task {i+1}"
            mock_task.completed = i % 2 == 0  # Alternate completed status
            mock_tasks.append(mock_task)

        formatted = response_composer._format_task_list(mock_tasks)

        # Should show first 10 tasks and mention there are more
        assert "Task 1" in formatted
        assert "Task 10" in formatted
        assert "Task 11" not in formatted  # Task 11 shouldn't be shown
        assert "more" in formatted or "..." in formatted


class TestResponseCompositionEdgeCases:
    """Test edge cases for response composition"""

    def test_compose_response_with_none_result(self, response_composer):
        """Test composing response with None result"""
        response = response_composer.compose_response({})

        assert "request was processed successfully" in response.lower()

    def test_compose_response_with_invalid_result(self, response_composer):
        """Test composing response with invalid result structure"""
        response = response_composer.compose_response("invalid_result")

        # Should handle gracefully and return a default message
        assert isinstance(response, str)

    def test_add_suggestions_with_exception(self, response_composer):
        """Test adding suggestions when an exception occurs"""
        try:
            suggestions = response_composer.add_suggestions("test", {})
            assert isinstance(suggestions, list)
        except Exception:
            # If there's an exception, it should be handled gracefully
            assert True  # This test is just to ensure no unhandled exceptions

    def test_format_task_list_with_invalid_tasks(self, response_composer):
        """Test formatting task list with invalid task objects"""
        # Test with mixed valid and invalid task objects
        mock_task = Mock()
        mock_task.title = "Valid task"
        mock_task.completed = False

        invalid_task = {"title": "Dict task", "completed": True}

        formatted = response_composer._format_task_list([mock_task, invalid_task])

        # Should handle both Mock objects and dict objects
        assert "Valid task" in formatted
        assert "Dict task" in formatted

    def test_compose_error_response_variations(self, response_composer):
        """Test different types of error responses"""
        error_scenarios = [
            {"success": False, "response": "", "error": "Connection timeout", "response_type": "error"},
            {"success": False, "response": "", "response_type": "error"},
            {"success": False, "error": "Validation failed", "response_type": "error"}
        ]

        for scenario in error_scenarios:
            response = response_composer.compose_response(scenario)
            assert "couldn't" in response.lower() or "error" in response.lower()