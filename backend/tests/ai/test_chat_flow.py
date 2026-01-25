"""
Integration tests for the complete chatbot flow
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
class TestCompleteChatFlow:
    """Test the complete chatbot flow from input to output"""

    async def test_complete_task_creation_flow(self, chatbot_orchestrator):
        """Test the complete flow for creating a task"""
        user_id = "user_123"
        message = "Add a task to buy groceries"

        # Mock all the components in the flow
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
                       "task_id": "task_123"
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

        assert result["response"] == "I've created a task 'buy groceries' for you."
        assert result["response_type"] == "success"
        assert result["task_id"] == "task_123"

    async def test_complete_task_update_flow(self, chatbot_orchestrator):
        """Test the complete flow for updating a task"""
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
                               entity_value="grocery task",
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
                       "response": "I've updated the task 'grocery task' to be complete.",
                       "response_type": "success",
                       "task_id": "task_123"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've updated the task 'grocery task' to be complete."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I've updated the task 'grocery task' to be complete.",
                       "confidence": 0.9
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert "grocery task" in result["response"]
        assert "complete" in result["response"]
        assert result["response_type"] == "success"

    async def test_complete_task_deletion_flow_with_confirmation(self, chatbot_orchestrator):
        """Test the complete flow for deleting a task with confirmation"""
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
                               entity_value="grocery task",
                               confidence_score=0.8
                           )
                       ]
                   )), \
             patch('src.ai.task_control.task_controller.execute_intent',
                   return_value={
                       "success": False,
                       "response": "Are you sure you want to delete the task 'grocery task'? Please confirm.",
                       "response_type": "confirmation_required",
                       "pending_action": "delete_task",
                       "task_id": "task_123"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="Are you sure you want to delete the task 'grocery task'? Please confirm."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "Are you sure you want to delete the task 'grocery task'? Please confirm.",
                       "confidence": 0.9
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert "Are you sure" in result["response"]
        assert result["response_type"] == "confirmation_required"
        assert "task_id" in result

    async def test_complete_task_listing_flow(self, chatbot_orchestrator):
        """Test the complete flow for listing tasks"""
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
                       "response": "You have 2 tasks:\n○ Buy groceries\n✓ Clean room",
                       "response_type": "success",
                       "task_count": 2
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="You have 2 tasks:\n○ Buy groceries\n✓ Clean room"), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "You have 2 tasks:\n○ Buy groceries\n✓ Clean room",
                       "confidence": 1.0
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert "2 tasks" in result["response"]
        assert "Buy groceries" in result["response"]
        assert result["response_type"] == "success"

    async def test_complete_task_search_flow(self, chatbot_orchestrator):
        """Test the complete flow for searching tasks"""
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

        assert "dentist" in result["response"]
        assert "Schedule dentist appointment" in result["response"]
        assert result["response_type"] == "success"

    async def test_complete_user_info_flow(self, chatbot_orchestrator):
        """Test the complete flow for getting user information"""
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
                       "user_id": "user_123"
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

        assert "user_123" in result["response"]
        assert result["response_type"] == "success"


@pytest.mark.asyncio
class TestConversationStateManagement:
    """Test conversation state management"""

    async def test_conversation_context_persistence(self, chatbot_orchestrator):
        """Test that conversation context is properly managed"""
        session_id = "session_123"
        user_id = "user_123"

        # Get conversation context for the first time
        context1 = await chatbot_orchestrator._get_conversation_context(session_id, user_id)
        assert context1["session_id"] == session_id
        assert context1["user_id"] == user_id
        assert context1["turn_count"] == 0

        # Update the context
        chatbot_orchestrator.conversation_states[session_id]["turn_count"] = 1
        chatbot_orchestrator.conversation_states[session_id]["last_intent"] = "CREATE_TASK"

        # Get the same context again
        context2 = await chatbot_orchestrator._get_conversation_context(session_id, user_id)

        assert context2["turn_count"] == 1
        assert context2["last_intent"] == "CREATE_TASK"

    async def test_conversation_state_updates(self, chatbot_orchestrator):
        """Test that conversation state is properly updated"""
        session_id = "session_456"
        user_id = "user_123"

        from src.models.chat_models import UserIntent, IntentType
        intent = UserIntent(intent_type=IntentType.CREATE_TASK, confidence_score=0.9)
        operation_result = {"success": True, "response_type": "success"}

        # Update conversation state
        await chatbot_orchestrator._update_conversation_state(session_id, user_id, intent, operation_result)

        # Check that state was updated
        assert session_id in chatbot_orchestrator.conversation_states
        state = chatbot_orchestrator.conversation_states[session_id]
        assert state["turn_count"] == 1
        assert state["last_intent"] == "CREATE_TASK"
        assert len(state["conversation_history"]) == 1


@pytest.mark.asyncio
class TestErrorHandlingInFlow:
    """Test error handling in the complete flow"""

    async def test_error_handling_when_nlp_fails(self, chatbot_orchestrator):
        """Test that the flow handles NLP processing errors gracefully"""
        user_id = "user_123"
        message = "This is an unusual message that might cause problems"

        with patch.object(chatbot_orchestrator, '_get_or_create_user_context'), \
             patch.object(chatbot_orchestrator.user_context_handler, 'create_context'), \
             patch.object(chatbot_orchestrator, '_get_conversation_context', return_value={}), \
             patch.object(chatbot_orchestrator, '_update_conversation_state'), \
             patch('src.ai.nlp_intent_processor.nlp_processor.process_intent',
                   side_effect=Exception("NLP processing failed")), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I'm sorry, but I encountered an error processing your message."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I'm sorry, but I encountered an error processing your message.",
                       "confidence": 0.5
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert "error processing" in result["response"]
        assert result["response_type"] == "error"

    async def test_error_handling_when_task_execution_fails(self, chatbot_orchestrator):
        """Test that the flow handles task execution errors gracefully"""
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
                   side_effect=Exception("Task execution failed")), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I'm sorry, but I encountered an error processing your message."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": True,
                       "issues": [],
                       "sanitized_response": "I'm sorry, but I encountered an error processing your message.",
                       "confidence": 0.5
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        assert "error processing" in result["response"]
        assert result["response_type"] == "error"

    async def test_quality_guard_validation_failure(self, chatbot_orchestrator):
        """Test that the flow handles quality guard validation failures"""
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
                   return_value={
                       "success": True,
                       "response": "I've created a task 'buy groceries' for you.",
                       "response_type": "success",
                       "task_id": "task_123"
                   }), \
             patch('src.ai.response_composer.response_composer.compose_response',
                   return_value="I've created a task 'buy groceries' for you."), \
             patch('src.ai.quality_guard.quality_guard.validate_response',
                   return_value={
                       "is_valid": False,
                       "issues": [{"type": "safety_violation", "description": "Response contains unsafe content"}],
                       "sanitized_response": "I'm sorry, but I encountered an error processing your request.",
                       "confidence": 0.1
                   }):

            result = await chatbot_orchestrator.process_message(user_id, message)

        # Should return the sanitized response from quality guard
        assert "error processing" in result["response"] or "sorry" in result["response"].lower()
        assert result["response_type"] == "error"


@pytest.mark.asyncio
class TestMultiTurnConversations:
    """Test multi-turn conversation handling"""

    async def test_conversation_history_tracking(self, chatbot_orchestrator):
        """Test that conversation history is properly tracked"""
        session_id = "session_789"
        user_id = "user_123"

        from src.models.chat_models import UserIntent, IntentType
        intent = UserIntent(intent_type=IntentType.CREATE_TASK, confidence_score=0.9)
        operation_result = {
            "success": True,
            "response_type": "success",
            "intent_processed": {"intent_type": "CREATE_TASK"}
        }

        # Update conversation state multiple times
        for i in range(3):
            await chatbot_orchestrator._update_conversation_state(session_id, user_id, intent, operation_result)

        # Check that history is maintained
        state = chatbot_orchestrator.conversation_states[session_id]
        assert state["turn_count"] == 3
        assert len(state["conversation_history"]) == 3

    async def test_conversation_history_limited_to_10_entries(self, chatbot_orchestrator):
        """Test that conversation history is limited to 10 entries"""
        session_id = "session_999"
        user_id = "user_123"

        from src.models.chat_models import UserIntent, IntentType
        intent = UserIntent(intent_type=IntentType.CREATE_TASK, confidence_score=0.9)
        operation_result = {
            "success": True,
            "response_type": "success",
            "intent_processed": {"intent_type": "CREATE_TASK"}
        }

        # Update conversation state 15 times
        for i in range(15):
            await chatbot_orchestrator._update_conversation_state(session_id, user_id, intent, operation_result)

        # Check that history is limited to 10 entries
        state = chatbot_orchestrator.conversation_states[session_id]
        assert len(state["conversation_history"]) == 10