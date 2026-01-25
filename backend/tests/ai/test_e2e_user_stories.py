"""
End-to-end tests for all user stories
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.models.chat_models import UserIntent, IntentType, ExtractedEntity, EntityType
from src.ai.chatbot_orchestrator import ChatbotOrchestrator
from src.ai.nlp_intent_processor import NLPIntentProcessor
from src.ai.task_control import TaskControl
from src.ai.response_composer import ResponseComposer
from src.ai.quality_guard import QualityGuard


@pytest.fixture
def chatbot_orchestrator():
    """Create a test instance of the chatbot orchestrator"""
    return ChatbotOrchestrator()


@pytest.mark.asyncio
class TestUserStory1NaturalLanguageTaskCreation:
    """Test User Story 1: Natural Language Task Creation"""

    async def test_create_task_scenario_add_task_buy_groceries(self, chatbot_orchestrator):
        """Test the scenario: Add a task to buy groceries"""
        user_id = "user_123"
        message = "Add a task to buy groceries"

        # Mock the complete flow
        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.CREATE_TASK,
                       confidence_score=0.9,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="buy groceries",
                               confidence_score=0.9
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I've created a task 'buy groceries' for you.",
                       "response_type": "success",
                       "task_id": "task_123",
                       "task_title": "buy groceries"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've created a task 'buy groceries' for you."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've created a task 'buy groceries' for you.",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        # Verify success
        assert result["success"] is True
        assert "buy groceries" in result["response"]
        assert result["response_type"] == "success"
        assert result["task_id"] == "task_123"

    async def test_create_task_scenario_create_task_schedule_dentist(self, chatbot_orchestrator):
        """Test the scenario: Create a task called 'schedule dentist appointment' with description 'Call Dr. Smith'"""
        user_id = "user_123"
        message = "Create a task called 'schedule dentist appointment' with description 'Call Dr. Smith'"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.CREATE_TASK,
                       confidence_score=0.9,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="schedule dentist appointment",
                               confidence_score=0.9
                           ),
                           ExtractedEntity(
                               entity_type=EntityType.TASK_DESCRIPTION,
                               entity_value="Call Dr. Smith",
                               confidence_score=0.8
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I've created a task 'schedule dentist appointment' with description 'Call Dr. Smith' for you.",
                       "response_type": "success",
                       "task_id": "task_456",
                       "task_title": "schedule dentist appointment"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've created a task 'schedule dentist appointment' with description 'Call Dr. Smith' for you."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've created a task 'schedule dentist appointment' with description 'Call Dr. Smith' for you.",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "schedule dentist appointment" in result["response"]
        assert "Call Dr. Smith" in result["response"]
        assert result["response_type"] == "success"


@pytest.mark.asyncio
class TestUserStory2TaskUpdateAndCompletion:
    """Test User Story 2: Task Update and Completion"""

    async def test_update_task_mark_grocery_as_complete(self, chatbot_orchestrator):
        """Test the scenario: Mark the grocery task as complete"""
        user_id = "user_123"
        message = "Mark the grocery task as complete"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.UPDATE_TASK,
                       confidence_score=0.8,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="grocery",
                               confidence_score=0.8
                           ),
                           ExtractedEntity(
                               entity_type=EntityType.STATUS_INDICATOR,
                               entity_value="complete",
                               confidence_score=0.7
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I've updated the task 'buy groceries' to be complete.",
                       "response_type": "success",
                       "task_id": "task_123",
                       "task_title": "buy groceries"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've updated the task 'buy groceries' to be complete."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've updated the task 'buy groceries' to be complete.",
                       "confidence": 0.9
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "grocery" in result["response"]
        assert "complete" in result["response"]
        assert result["response_type"] == "success"

    async def test_update_task_change_dentist_description(self, chatbot_orchestrator):
        """Test the scenario: Update the dentist appointment task description to 'Call Dr. Smith at 9 AM'"""
        user_id = "user_123"
        message = "Update the dentist appointment task description to 'Call Dr. Smith at 9 AM'"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.UPDATE_TASK,
                       confidence_score=0.8,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="dentist appointment",
                               confidence_score=0.8
                           ),
                           ExtractedEntity(
                               entity_type=EntityType.TASK_DESCRIPTION,
                               entity_value="Call Dr. Smith at 9 AM",
                               confidence_score=0.7
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I've updated the task 'schedule dentist appointment' with the new description.",
                       "response_type": "success",
                       "task_id": "task_456",
                       "task_title": "schedule dentist appointment"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've updated the task 'schedule dentist appointment' with the new description."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've updated the task 'schedule dentist appointment' with the new description.",
                       "confidence": 0.9
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "dentist appointment" in result["response"]
        assert result["response_type"] == "success"


@pytest.mark.asyncio
class TestUserStory3TaskDeletionWithConfirmation:
    """Test User Story 3: Task Deletion with Confirmation"""

    async def test_delete_task_with_confirmation_flow(self, chatbot_orchestrator):
        """Test the scenario: Delete the grocery task with confirmation flow"""
        user_id = "user_123"
        message = "Delete the grocery task"

        # First call: request deletion, should ask for confirmation
        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.DELETE_TASK,
                       confidence_score=0.8,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="grocery",
                               confidence_score=0.8
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": False,
                       "response": "Are you sure you want to delete the task 'buy groceries'? Please confirm.",
                       "response_type": "confirmation_required",
                       "pending_action": "delete_task",
                       "task_id": "task_123"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="Are you sure you want to delete the task 'buy groceries'? Please confirm."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "Are you sure you want to delete the task 'buy groceries'? Please confirm.",
                       "confidence": 0.9
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert "Are you sure" in result["response"]
        assert result["response_type"] == "confirmation_required"
        assert "task_id" in result

    async def test_confirm_task_deletion(self, chatbot_orchestrator):
        """Test the scenario: Confirm task deletion after confirmation request"""
        user_id = "user_123"
        message = "Yes, delete it"

        # Simulate a session where a deletion is pending
        session_id = "session_123"
        chatbot_orchestrator.conversation_states[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "pending_actions": {
                "pending_action": "delete_task",
                "task_id": "task_123"
            }
        }

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value=chatbot_orchestrator.conversation_states[session_id]), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I've deleted the task 'buy groceries'.",
                       "response_type": "task_deleted",
                       "task_id": "task_123"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've deleted the task 'buy groceries'."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've deleted the task 'buy groceries'.",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "deleted" in result["response"]
        assert result["response_type"] == "success"


@pytest.mark.asyncio
class TestUserStory4TaskListingAndSearch:
    """Test User Story 4: Task Listing and Search"""

    async def test_list_all_tasks_scenario(self, chatbot_orchestrator):
        """Test the scenario: Show me all my tasks"""
        user_id = "user_123"
        message = "Show me all my tasks"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.LIST_TASKS,
                       confidence_score=0.9,
                       extracted_entities=[]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "You have 3 tasks:\n○ Buy groceries\n○ Schedule dentist appointment\n✓ Clean room",
                       "response_type": "success",
                       "task_count": 3
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="You have 3 tasks:\n○ Buy groceries\n○ Schedule dentist appointment\n✓ Clean room"), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "You have 3 tasks:\n○ Buy groceries\n○ Schedule dentist appointment\n✓ Clean room",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "3 tasks" in result["response"]
        assert "Buy groceries" in result["response"]
        assert result["response_type"] == "success"

    async def test_search_tasks_about_dentist(self, chatbot_orchestrator):
        """Test the scenario: Find tasks about dentist"""
        user_id = "user_123"
        message = "Find tasks about dentist"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.SEARCH_TASKS,
                       confidence_score=0.9,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.KEYWORD,
                               entity_value="dentist",
                               confidence_score=0.9
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I found 1 task containing 'dentist':\n○ Schedule dentist appointment",
                       "response_type": "success",
                       "matching_count": 1
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I found 1 task containing 'dentist':\n○ Schedule dentist appointment"), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I found 1 task containing 'dentist':\n○ Schedule dentist appointment",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "dentist" in result["response"]
        assert "Schedule dentist appointment" in result["response"]
        assert result["response_type"] == "success"


@pytest.mark.asyncio
class TestUserStory5UserInformationAccess:
    """Test User Story 5: User Information Access"""

    async def test_get_user_email_scenario(self, chatbot_orchestrator):
        """Test the scenario: What is my email?"""
        user_id = "user_123"
        message = "What is my email?"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.GET_USER_INFO,
                       confidence_score=0.9,
                       extracted_entities=[],
                       parameters={"original_message": "What is my email?"}
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "You are logged in as user_123@example.com.",
                       "response_type": "success",
                       "user_id": "user_123",
                       "email": "user_123@example.com"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="You are logged in as user_123@example.com."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "You are logged in as user_123@example.com.",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "user_123" in result["response"]
        assert "@" in result["response"]
        assert result["response_type"] == "success"

    async def test_get_user_identity_scenario(self, chatbot_orchestrator):
        """Test the scenario: Who am I logged in as?"""
        user_id = "user_456"
        message = "Who am I logged in as?"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.GET_USER_INFO,
                       confidence_score=0.9,
                       extracted_entities=[],
                       parameters={"original_message": "Who am I logged in as?"}
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "You are logged in as user_456.",
                       "response_type": "success",
                       "user_id": "user_456"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="You are logged in as user_456."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "You are logged in as user_456.",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "user_456" in result["response"]
        assert result["response_type"] == "success"


@pytest.mark.asyncio
class TestEdgeCaseScenarios:
    """Test edge case scenarios from the specification"""

    async def test_unauthenticated_user_trying_to_use_chatbot(self, chatbot_orchestrator):
        """Test what happens when an unauthenticated user tries to use the chatbot"""
        # This would typically be handled at the authentication layer
        # For this test, we'll simulate the scenario inside the orchestrator
        user_id = None  # Simulating unauthenticated user
        message = "Add a task to buy groceries"

        # In a real implementation, this would be caught by authentication middleware
        # For this test, we'll check that the system handles None user_id appropriately
        with patch.object(chatbot_orchestrator, '_get_or_create_user_context',
                         side_effect=Exception("User not authenticated")):

            try:
                result = await chatbot_orchestrator.process_message(user_id, message)
                # If we reach this point, the system allowed an unauthenticated user
                assert False, "System should not allow unauthenticated users to process messages"
            except Exception as e:
                # This is expected behavior
                assert "User not authenticated" in str(e)

    async def test_ambiguous_task_reference_multiple_similar_tasks(self, chatbot_orchestrator):
        """Test how the system handles ambiguous task references when multiple similar tasks exist"""
        user_id = "user_123"
        message = "Update that task"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.UPDATE_TASK,
                       confidence_score=0.6,  # Lower confidence due to ambiguity
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.REFERENCE_DEMONSTRATIVE,
                               entity_value="that",
                               confidence_score=0.7
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": False,
                       "response": "I couldn't find a specific task matching your request. Could you be more specific?",
                       "response_type": "clarification_needed"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I couldn't find a specific task matching your request. Could you be more specific."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I couldn't find a specific task matching your request. Could you be more specific.",
                       "confidence": 0.8
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["response_type"] == "clarification_needed"
        assert "more specific" in result["response"]

    async def test_search_returns_no_results(self, chatbot_orchestrator):
        """Test what happens when a search returns no results"""
        user_id = "user_123"
        message = "Find tasks about unicorns"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.SEARCH_TASKS,
                       confidence_score=0.9,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.KEYWORD,
                               entity_value="unicorns",
                               confidence_score=0.9
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": False,
                       "response": "I couldn't find any tasks containing 'unicorns'.",
                       "response_type": "success",  # Still successful, just no results
                       "matching_count": 0
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I couldn't find any tasks containing 'unicorns'."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I couldn't find any tasks containing 'unicorns'.",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True  # Operation succeeded, just no results found
        assert "couldn't find" in result["response"]
        assert "unicorns" in result["response"]

    async def test_multiple_intents_in_single_message(self, chatbot_orchestrator):
        """Test how the system handles multiple intents in a single message"""
        user_id = "user_123"
        message = "Add a task to buy groceries and mark the cleaning task as complete"

        # For simplicity in testing, we'll simulate handling the first intent
        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.CREATE_TASK,  # Primary intent
                       confidence_score=0.7,  # Lower confidence due to compound request
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="buy groceries",
                               confidence_score=0.8
                           )
                       ],
                       parameters={
                           "compound_request": True,
                           "total_intents_detected": 2,
                           "all_intents": ["CREATE_TASK", "UPDATE_TASK"]
                       }
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": True,
                       "response": "I've created a task 'buy groceries' for you. I noticed you also wanted to update another task - could you specify that separately?",
                       "response_type": "success",
                       "task_id": "task_123"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've created a task 'buy groceries' for you. I noticed you also wanted to update another task - could you specify that separately?"), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've created a task 'buy groceries' for you. I noticed you also wanted to update another task - could you specify that separately?",
                       "confidence": 0.8
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is True
        assert "buy groceries" in result["response"]
        assert "separately" in result["response"]  # Indicates handling of compound request

    async def test_backend_api_temporarily_unavailable(self, chatbot_orchestrator):
        """Test what occurs when backend APIs are temporarily unavailable"""
        user_id = "user_123"
        message = "Add a task to buy groceries"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   return_value=UserIntent(
                       intent_type=IntentType.CREATE_TASK,
                       confidence_score=0.9,
                       extracted_entities=[
                           ExtractedEntity(
                               entity_type=EntityType.TASK_TITLE,
                               entity_value="buy groceries",
                               confidence_score=0.9
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   side_effect=Exception("Backend API temporarily unavailable")), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I'm sorry, but I'm having trouble connecting to the service right now. Please try again in a moment."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I'm sorry, but I'm having trouble connecting to the service right now. Please try again in a moment.",
                       "confidence": 0.6
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert result["success"] is False  # Operation failed due to backend issue
        assert "trouble connecting" in result["response"] or "try again" in result["response"]
        assert result["response_type"] == "error"