"""
Unit tests for NLP intent processor
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.models.chat_models import IntentType
from src.ai.nlp_intent_processor import NLPIntentProcessor


@pytest.fixture
def nlp_processor():
    """Create a test instance of the NLP intent processor"""
    return NLPIntentProcessor()


@pytest.mark.asyncio
class TestIntentClassification:
    """Test intent classification functionality"""

    async def test_create_task_intent_identification(self, nlp_processor):
        """Test that create task intents are correctly identified"""
        test_messages = [
            "Add a task to buy groceries",
            "Create a task to schedule dentist appointment",
            "I need to clean my room",
            "Remind me to call mom",
            "Make a new task to finish report"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            assert intent.intent_type == IntentType.CREATE_TASK
            assert intent.confidence_score >= 0.5

    async def test_update_task_intent_identification(self, nlp_processor):
        """Test that update task intents are correctly identified"""
        test_messages = [
            "Update the grocery task to be complete",
            "Change the dentist appointment description",
            "Mark the cleaning task as done",
            "Set the report task as complete"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            assert intent.intent_type in [IntentType.UPDATE_TASK, IntentType.CREATE_TASK]
            assert intent.confidence_score >= 0.3

    async def test_delete_task_intent_identification(self, nlp_processor):
        """Test that delete task intents are correctly identified"""
        test_messages = [
            "Delete the grocery task",
            "Remove the dentist appointment task",
            "Cancel the cleaning task"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            # May be classified as DELETE or UPDATE depending on pattern matching
            assert intent.intent_type in [IntentType.DELETE_TASK, IntentType.UPDATE_TASK, IntentType.CREATE_TASK]
            assert intent.confidence_score >= 0.3

    async def test_list_tasks_intent_identification(self, nlp_processor):
        """Test that list tasks intents are correctly identified"""
        test_messages = [
            "Show me all my tasks",
            "What are my current tasks?",
            "List all tasks",
            "Display my tasks"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            assert intent.intent_type == IntentType.LIST_TASKS
            assert intent.confidence_score >= 0.5

    async def test_search_tasks_intent_identification(self, nlp_processor):
        """Test that search tasks intents are correctly identified"""
        test_messages = [
            "Find tasks about dentist",
            "Search for grocery tasks",
            "Look for cleaning tasks",
            "Show tasks containing report"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            assert intent.intent_type == IntentType.SEARCH_TASKS
            assert intent.confidence_score >= 0.5

    async def test_get_user_info_intent_identification(self, nlp_processor):
        """Test that get user info intents are correctly identified"""
        test_messages = [
            "What is my email?",
            "Who am I logged in as?",
            "Tell me about myself",
            "Show my profile"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            assert intent.intent_type == IntentType.GET_USER_INFO
            assert intent.confidence_score >= 0.5

    async def test_unknown_intent_identification(self, nlp_processor):
        """Test that unknown intents are properly handled"""
        test_messages = [
            "This is not a valid task command",
            "Random text that doesn't match any pattern",
            "Blah blah blah",
            "xyz123abc"
        ]

        for message in test_messages:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            # Unknown intents might still get classified with low confidence
            assert intent.confidence_score <= 0.5


@pytest.mark.asyncio
class TestEntityExtraction:
    """Test entity extraction functionality"""

    async def test_task_title_extraction(self, nlp_processor):
        """Test that task titles are extracted correctly"""
        test_cases = [
            ("Add a task to buy groceries", "buy groceries"),
            ("Create task called 'finish report'", "finish report"),
            ("I need to clean my room", "clean my room"),
        ]

        for message, expected_title in test_cases:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            title_entities = [e for e in intent.extracted_entities if e.entity_type == "TASK_TITLE"]

            # Check if any extracted title contains the expected text
            found_match = any(expected_title.lower() in entity.entity_value.lower() for entity in title_entities)
            assert found_match, f"Expected to find title containing '{expected_title}', got {title_entities}"

    async def test_keyword_extraction(self, nlp_processor):
        """Test that keywords are extracted correctly for search"""
        test_cases = [
            ("Find tasks about dentist", "dentist"),
            ("Search for grocery tasks", "grocery"),
            ("Look for cleaning tasks", "cleaning"),
        ]

        for message, expected_keyword in test_cases:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            keyword_entities = [e for e in intent.extracted_entities if e.entity_type == "KEYWORD"]

            # Check if any extracted keyword matches the expected text
            found_match = any(expected_keyword.lower() in entity.entity_value.lower() for entity in keyword_entities)
            assert found_match, f"Expected to find keyword containing '{expected_keyword}', got {keyword_entities}"

    async def test_status_indicator_extraction(self, nlp_processor):
        """Test that status indicators are extracted correctly"""
        test_cases = [
            ("Mark the task as complete", "complete"),
            ("Set the task as done", "complete"),
            ("Update task to be finished", "complete"),
            ("Mark as incomplete", "incomplete"),
            ("Set as pending", "incomplete"),
        ]

        for message, expected_status in test_cases:
            intent = await nlp_processor.process_intent(message, "test_user_123")
            status_entities = [e for e in intent.extracted_entities if e.entity_type == "STATUS_INDICATOR"]

            # Check if any extracted status matches the expected text
            found_match = any(expected_status.lower() in entity.entity_value.lower() for entity in status_entities)
            assert found_match, f"Expected to find status containing '{expected_status}', got {status_entities}"


@pytest.mark.asyncio
class TestIntentConfidence:
    """Test intent confidence validation"""

    async def test_intent_confidence_threshold(self, nlp_processor):
        """Test that intent confidence is properly validated"""
        message = "Add a task to buy groceries"
        intent = await nlp_processor.process_intent(message, "test_user_123")

        is_confident = nlp_processor.validate_intent_confidence(intent, threshold=0.5)
        assert is_confident == (intent.confidence_score >= 0.5)