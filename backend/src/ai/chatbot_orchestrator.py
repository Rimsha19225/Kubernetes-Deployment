"""
Chatbot Orchestrator
Coordinates the overall chatbot operation flow and manages conversation state
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import uuid

from src.models.chat_models import UserIntent, ChatResponse, ChatRequest
from src.ai.nlp_intent_processor import nlp_processor
from src.ai.task_control import task_controller
from src.ai.response_composer import response_composer
from src.ai.quality_guard import quality_guard
from src.ai.user_context_handler import UserContextHandler
from src.utils.ai_logging import ai_logger

logger = logging.getLogger(__name__)

class ChatbotOrchestrator:
    """
    Coordinates the overall chatbot operation flow and manages conversation state
    """
    def __init__(self):
        self.user_context_handler = UserContextHandler()
        self.conversation_states = {}  # In production, this should be stored in a persistent store

    async def process_message(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the complete chatbot flow
        """
        start_time = datetime.utcnow()

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        with ai_logger.measure_duration("full_message_processing", user_id):
            try:
                # Step 1: Get user context
                user_context = await self._get_or_create_user_context(user_id)

                # Step 2: Validate user permissions
                permission_check = quality_guard.validate_user_permissions(
                    user_context.to_dict(),
                    "read_profile"
                )

                if not permission_check["has_permission"]:
                    return {
                        "response": "You don't have permission to access this feature.",
                        "response_type": "error",
                        "session_id": session_id
                    }

                # Step 3: Process intent and extract entities
                intent = await nlp_processor.process_intent(message, user_id)

                # Step 4: Validate intent accuracy
                intent_validation = quality_guard.validate_intent_accuracy(
                    message,
                    intent,
                    intent.extracted_entities
                )

                # Step 5: Check if intent confidence is sufficient
                if not nlp_processor.validate_intent_confidence(intent):
                    return {
                        "response": f"I'm not sure what you mean by '{message}'. Could you rephrase that?",
                        "response_type": "clarification_needed",
                        "session_id": session_id
                    }

                # Step 6: Get conversation context
                conversation_context = await self._get_conversation_context(session_id, user_id)

                # Step 7: Execute the intent
                operation_result = await task_controller.execute_intent(
                    user_id=user_id,
                    intent=intent,
                    session_context=conversation_context
                )

                # Step 8: Compose response
                composed_response = response_composer.compose_response(
                    operation_result,
                    message
                )

                # Step 9: Validate response for safety and accuracy
                response_validation = quality_guard.validate_response(
                    composed_response,
                    intent,
                    user_context.to_dict(),
                    operation_result
                )

                # Step 10: Update conversation state if needed
                await self._update_conversation_state(
                    session_id,
                    user_id,
                    intent,
                    operation_result
                )

                # Step 11: Handle pending actions and confirmations
                if operation_result.get("response_type") == "confirmation_required":
                    if session_id not in self.conversation_states:
                        await self._get_conversation_context(session_id, user_id)

                    # Store the pending action for later confirmation
                    self.conversation_states[session_id]["pending_actions"] = {
                        "action": operation_result.get("pending_action"),
                        "task_id": operation_result.get("task_id"),
                        "timestamp": datetime.utcnow().isoformat()
                    }

                    # Store the original intent for re-execution after confirmation
                    self.conversation_states[session_id]["original_intent_for_confirmation"] = intent
                    self.conversation_states[session_id]["user_id"] = user_id

                # Step 12: Store last referenced task ID if a task was operated on
                if operation_result.get("task_id"):
                    if session_id not in self.conversation_states:
                        await self._get_conversation_context(session_id, user_id)
                    self.conversation_states[session_id]["last_referenced_task_id"] = operation_result["task_id"]

                # Calculate processing duration
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000  # in milliseconds

                # Prepare the final response
                response_data = {
                    "response": response_validation["sanitized_response"],
                    "response_type": operation_result.get("response_type", "success"),
                    "session_id": session_id,
                    "task_id": operation_result.get("task_id"),
                    "intent_processed": intent.dict() if hasattr(intent, 'dict') else intent.__dict__,
                    "metadata": {
                        "processing_time_ms": duration,
                        "confidence": response_validation["confidence"],
                        "validation_passed": response_validation["is_valid"]
                    }
                }

                # Add suggestions if available
                suggestions = response_composer.add_suggestions(composed_response, operation_result)
                if suggestions:
                    response_data["suggestions"] = suggestions

                # Log the complete interaction
                ai_logger.log_intent_processing(
                    user_id=user_id,
                    message=message,
                    intent_type=intent.intent_type.value,
                    confidence=intent.confidence_score,
                    entities=[entity.entity_value for entity in intent.extracted_entities],
                    duration_ms=duration
                )

                return response_data

            except Exception as e:
                ai_logger.log_error("message_processing_failed", str(e), user_id)
                # Log the specific error for debugging but return a generic message to the user
                logger.error(f"Error processing message for user {user_id}: {str(e)}")
                return {
                    "response": "I'm sorry, but I encountered an error processing your request.",
                    "response_type": "error",
                    "session_id": session_id
                }

    async def _get_or_create_user_context(self, user_id: str):
        """
        Get or create user context for the current user
        """
        try:
            context = await self.user_context_handler.get_context(user_id)
            if not context:
                # Create a new context based on user information
                # Fetch user details from the database using the auth service
                from src.services.auth_service import get_user_by_id
                user = get_user_by_id(user_id)
                if user:
                    context = await self.user_context_handler.create_context(user)
                else:
                    # Fallback to mock user if real user not found
                    from src.models.user import User
                    # Create mock user with required fields, using a unique ID derived from the user_id string
                    # Convert user_id to a number if it's numeric, otherwise use a hash-based ID
                    try:
                        mock_user_id = int(user_id) if user_id.isdigit() else abs(hash(user_id)) % 1000000
                    except:
                        mock_user_id = 999999  # fallback ID

                    mock_user = User(id=mock_user_id, email=f"user_{user_id}@example.com", name=f"User {user_id}", hashed_password="temp_password")
                    context = await self.user_context_handler.create_context(mock_user)
            return context
        except Exception as e:
            ai_logger.log_error("_get_or_create_user_context_failed", str(e), user_id)
            # Fallback to creating a context with basic information
            from src.models.user import User
            # Create mock user with required fields, using a unique ID derived from the user_id string
            # Convert user_id to a number if it's numeric, otherwise use a hash-based ID
            try:
                mock_user_id = int(user_id) if user_id.isdigit() else abs(hash(user_id)) % 1000000
            except:
                mock_user_id = 999999  # fallback ID

            mock_user = User(id=mock_user_id, email=f"user_{user_id}@example.com", name=f"User {user_id}", hashed_password="temp_password")
            return await self.user_context_handler.create_context(mock_user)

    async def _get_conversation_context(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get conversation context for the current session
        """
        if session_id in self.conversation_states:
            return self.conversation_states[session_id]
        else:
            # Create a new conversation context
            context = {
                "session_id": session_id,
                "user_id": user_id,
                "turn_count": 0,
                "last_intent": None,
                "pending_actions": {},
                "conversation_history": []
            }
            self.conversation_states[session_id] = context
            return context

    async def _update_conversation_state(
        self,
        session_id: str,
        user_id: str,
        intent: UserIntent,
        operation_result: Dict[str, Any]
    ):
        """
        Update conversation state based on the interaction
        """
        if session_id not in self.conversation_states:
            await self._get_conversation_context(session_id, user_id)

        context = self.conversation_states[session_id]
        context["turn_count"] += 1
        context["last_intent"] = intent.intent_type.value
        context["conversation_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "intent": intent.intent_type.value,
            "result": operation_result.get("success", False),
            "response_type": operation_result.get("response_type", "success")
        })

        # Clean up old conversation history (keep last 10 interactions)
        if len(context["conversation_history"]) > 10:
            context["conversation_history"] = context["conversation_history"][-10:]

    async def handle_confirmation(self, session_id: str, user_response: str) -> Dict[str, Any]:
        """
        Handle user confirmation responses (yes/no) in the context of pending actions
        """
        if session_id not in self.conversation_states:
            return {
                "response": "I don't have any pending actions to confirm.",
                "response_type": "error",
                "session_id": session_id
            }

        context = self.conversation_states[session_id]
        pending_action = context.get("pending_actions", {})

        if not pending_action:
            return {
                "response": "I don't have any pending actions to confirm.",
                "response_type": "error",
                "session_id": session_id
            }

        user_response_lower = user_response.lower().strip()

        if user_response_lower in ['yes', 'y', 'confirm', 'ok', 'sure', 'please', 'yeah', 'yep', 'go ahead']:
            # User confirmed, proceed with the action
            # Mark the action as confirmed in the context
            context["pending_actions"]["confirmed_action"] = pending_action.get("action")
            context["confirmed_deletion"] = True  # For backward compatibility

            # Re-execute the original intent that required confirmation
            # Get the original intent that led to the confirmation request
            original_intent = context.get("original_intent_for_confirmation")
            if original_intent:
                # Execute the intent again with the confirmation context
                # We need to temporarily remove the confirmation requirement to allow the action to proceed
                operation_result = await task_controller.execute_intent(
                    user_id=context.get("user_id"),
                    intent=original_intent,
                    session_context=context
                )

                # Update the response based on the result
                composed_response = response_composer.compose_response(
                    operation_result,
                    "confirmation"
                )

                # Clear the pending action after successful completion
                context["pending_actions"] = {}

                return {
                    "response": composed_response,
                    "response_type": operation_result.get("response_type", "success"),
                    "session_id": session_id,
                    "task_id": operation_result.get("task_id")
                }
            else:
                # If no original intent is available, we need to reconstruct the action based on the pending action
                # This is a fallback for cases where we only have the action type and task_id
                task_id = pending_action.get("task_id")

                if task_id and pending_action.get("action") == "delete_task":
                    # Create a minimal intent for deletion
                    from src.models.chat_models import UserIntent, IntentType, ExtractedEntity
                    intent_for_deletion = UserIntent(
                        intent_type=IntentType.DELETE_TASK,
                        confidence_score=0.95,
                        parameters={"original_message": f"delete task id {task_id}"}
                    )

                    operation_result = await task_controller.execute_intent(
                        user_id=context.get("user_id"),
                        intent=intent_for_deletion,
                        session_context=context
                    )

                    # Update the response based on the result
                    composed_response = response_composer.compose_response(
                        operation_result,
                        "confirmation"
                    )

                    # Clear the pending action after successful completion
                    context["pending_actions"] = {}

                    return {
                        "response": composed_response,
                        "response_type": operation_result.get("response_type", "success"),
                        "session_id": session_id,
                        "task_id": operation_result.get("task_id")
                    }

                # If no original intent is available and we can't reconstruct, just return a success response
                action = pending_action.get("action", "the action")
                return {
                    "response": f"I've processed {action}.",
                    "response_type": "success",
                    "session_id": session_id
                }
        elif user_response_lower in ['no', 'n', 'cancel', 'no thanks', 'stop', 'nope', 'never mind', 'nevermind']:
            # User declined, cancel the action
            context["pending_actions"] = {}
            return {
                "response": "I've canceled that action.",
                "response_type": "success",
                "session_id": session_id
            }
        else:
            # Unclear response, ask for clarification
            action = pending_action.get("action", "the action")
            return {
                "response": f"Please respond with yes to confirm {action} or no to cancel.",
                "response_type": "clarification_needed",
                "session_id": session_id
            }

    async def request_clarification(self, user_query: str, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Request clarification from the user for ambiguous inputs
        """
        # Identify what kind of clarification is needed
        if "task" in user_query.lower():
            return {
                "response": f"I'm not sure which task you mean. Could you specify the task by its title or provide more details?",
                "response_type": "clarification_needed",
                "session_id": session_id
            }
        elif "update" in user_query.lower() or "change" in user_query.lower():
            return {
                "response": f"I need more information. Which task would you like to update, and what changes do you want to make?",
                "response_type": "clarification_needed",
                "session_id": session_id
            }
        else:
            return {
                "response": f"I'm not sure what you mean by '{user_query}'. Could you rephrase that?",
                "response_type": "clarification_needed",
                "session_id": session_id
            }

    async def cleanup_session(self, session_id: str):
        """
        Clean up session data when session is complete
        """
        if session_id in self.conversation_states:
            del self.conversation_states[session_id]


# Global instance of the chatbot orchestrator
chatbot_orchestrator = ChatbotOrchestrator()