"""
Chat Service
Handles database operations for chat messages and sessions
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from ..models.chat import ChatMessage, ChatSession, ChatMessageBase, ChatSessionBase, ChatMessageType
from ..models.user import User


class ChatService:
    """Service class for handling chat-related database operations"""

    @staticmethod
    def create_chat_session(session: Session, user_id: int, session_id: str, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        chat_session = ChatSession(
            user_id=user_id,
            session_id=session_id,
            title=title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            is_active=True
        )
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        return chat_session

    @staticmethod
    def get_or_create_chat_session(session: Session, user_id: int, session_id: str, title: Optional[str] = None) -> ChatSession:
        """Get existing chat session or create a new one"""
        existing_session = session.exec(
            select(ChatSession).where(ChatSession.session_id == session_id)
        ).first()

        if existing_session:
            return existing_session

        return ChatService.create_chat_session(session, user_id, session_id, title)

    @staticmethod
    def create_chat_message(
        session: Session,
        user_id: int,
        session_id: str,
        content: str,
        message_type: ChatMessageType
    ) -> ChatMessage:
        """Create a new chat message"""
        # First get or create the chat session
        chat_session = ChatService.get_or_create_chat_session(session, user_id, session_id)

        chat_message = ChatMessage(
            content=content,
            message_type=message_type,
            user_id=user_id,
            session_id=session_id,
            chat_session_id=chat_session.id
        )
        session.add(chat_message)
        session.commit()
        session.refresh(chat_message)
        return chat_message

    @staticmethod
    def get_chat_messages_by_session(session: Session, session_id: str) -> List[ChatMessage]:
        """Get all messages for a specific session"""
        # First get the chat session to get its ID
        chat_session = session.exec(
            select(ChatSession)
            .where(ChatSession.session_id == session_id)
        ).first()

        if not chat_session:
            return []

        messages = session.exec(
            select(ChatMessage)
            .where(ChatMessage.chat_session_id == chat_session.id)
            .order_by(ChatMessage.created_at)
        ).all()
        return messages

    @staticmethod
    def get_user_chat_sessions(session: Session, user_id: int) -> List[ChatSession]:
        """Get all chat sessions for a specific user"""
        chat_sessions = session.exec(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        ).all()
        return chat_sessions

    @staticmethod
    def deactivate_chat_session(session: Session, session_id: str) -> bool:
        """Deactivate a chat session"""
        chat_session = session.exec(
            select(ChatSession).where(ChatSession.session_id == session_id)
        ).first()

        if chat_session:
            chat_session.is_active = False
            session.add(chat_session)
            session.commit()
            return True
        return False