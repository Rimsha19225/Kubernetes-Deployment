"""
Chat Router Module
Defines the API endpoints for the AI chatbot functionality
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import logging

from sqlmodel import Session
from src.database.session import get_session
from src.utils.auth import get_current_user
from src.models.user import User
from src.ai.chatbot_orchestrator import ChatbotOrchestrator
from src.services.chat_service import ChatService
from src.models.chat import ChatMessageType

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)

class ChatMessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    response: str
    response_type: str  # success, clarification_needed, confirmation_required, error
    session_id: str
    task_id: Optional[str] = None
    suggestions: Optional[list[str]] = []

@router.post("/message", response_model=ChatMessageResponse)
async def process_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Process a user message through the AI chatbot
    """
    try:
        # Initialize the chatbot orchestrator
        chatbot = ChatbotOrchestrator()

        # Check if this is a confirmation response (yes/no) and if there's a pending action
        user_message_lower = request.message.lower().strip()

        # Check if this looks like a confirmation response and there might be a pending action
        is_confirmation_response = (
            user_message_lower in ['yes', 'y', 'no', 'n', 'yes.', 'no.', 'yes!', 'no!'] or
            user_message_lower in ['confirm', 'ok', 'sure', 'please', 'yeah', 'yep', 'go ahead',
                                   'cancel', 'no thanks', 'stop', 'nope', 'never mind', 'nevermind']
        )

        # If it's a confirmation response, handle it specially
        if is_confirmation_response and request.session_id:
            # Check if there are pending actions in the conversation state
            if hasattr(chatbot, 'conversation_states') and request.session_id in chatbot.conversation_states:
                session_state = chatbot.conversation_states[request.session_id]
                if session_state.get('pending_actions'):
                    # This is a confirmation response, handle it as such
                    result = await chatbot.handle_confirmation(
                        session_id=request.session_id,
                        user_response=request.message
                    )

                    # Save the user's message to the database
                    session_id = result.get('session_id', request.session_id or '')
                    ChatService.create_chat_message(
                        session=db_session,
                        user_id=current_user.id,
                        session_id=session_id,
                        content=request.message,
                        message_type=ChatMessageType.USER_INPUT
                    )

                    # Save the AI's response to the database
                    ChatService.create_chat_message(
                        session=db_session,
                        user_id=current_user.id,
                        session_id=session_id,
                        content=result.get('response', ''),
                        message_type=ChatMessageType.AI_RESPONSE
                    )

                    # Create or update chat session if it doesn't exist
                    ChatService.get_or_create_chat_session(
                        session=db_session,
                        user_id=current_user.id,
                        session_id=session_id
                    )

                    return ChatMessageResponse(
                        response=result.get('response', ''),
                        response_type=result.get('response_type', 'success'),
                        session_id=session_id,
                        task_id=str(result.get('task_id')) if result.get('task_id') is not None else None,
                        suggestions=result.get('suggestions', [])
                    )

        # Process the user message normally
        result = await chatbot.process_message(
            user_id=str(current_user.id),  # Convert to string to match expected format
            message=request.message,
            session_id=request.session_id
        )

        # Save the user's message to the database
        session_id = result.get('session_id', request.session_id or '')
        ChatService.create_chat_message(
            session=db_session,
            user_id=current_user.id,
            session_id=session_id,
            content=request.message,
            message_type=ChatMessageType.USER_INPUT
        )

        # Save the AI's response to the database
        ChatService.create_chat_message(
            session=db_session,
            user_id=current_user.id,
            session_id=session_id,
            content=result.get('response', ''),
            message_type=ChatMessageType.AI_RESPONSE
        )

        # Create or update chat session if it doesn't exist
        ChatService.get_or_create_chat_session(
            session=db_session,
            user_id=current_user.id,
            session_id=session_id
        )

        return ChatMessageResponse(
            response=result.get('response', ''),
            response_type=result.get('response_type', 'success'),
            session_id=session_id,
            task_id=str(result.get('task_id')) if result.get('task_id') is not None else None,
            suggestions=result.get('suggestions', [])
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")