"""
Chat Database Models
SQLModel classes for storing chat conversations, messages, and sessions
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChatMessageType(str, Enum):
    """Types of chat messages"""
    USER_INPUT = "user_input"
    AI_RESPONSE = "ai_response"


class ChatMessageBase(SQLModel):
    """Base model for chat messages"""
    content: str = Field(nullable=False)
    message_type: ChatMessageType = Field(default=ChatMessageType.USER_INPUT)
    user_id: int = Field(nullable=False, foreign_key="user.id")
    session_id: str = Field(nullable=False)  # Store the UUID session_id as string for external reference


class ChatMessage(ChatMessageBase, table=True):
    """Database model for chat messages"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    chat_session_id: Optional[int] = Field(default=None, foreign_key="chatsession.id")  # Foreign key to ChatSession table

    # Relationships
    user: Optional["User"] = Relationship(back_populates="chat_messages")
    session: Optional["ChatSession"] = Relationship(back_populates="messages")


class ChatSessionBase(SQLModel):
    """Base model for chat sessions"""
    user_id: int = Field(nullable=False, foreign_key="user.id")
    session_id: str = Field(nullable=False, unique=True)
    title: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)


class ChatSession(ChatSessionBase, table=True):
    """Database model for chat sessions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="chat_sessions")
    messages: List["ChatMessage"] = Relationship(back_populates="session", cascade_delete=True)


# Add relationships to User model
if "User" not in globals():
    # Forward reference for relationship
    from .user import User