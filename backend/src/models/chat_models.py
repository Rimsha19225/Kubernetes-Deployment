"""
Chat Models
Pydantic models for chat functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Types of user intents that the chatbot can recognize"""
    CREATE_TASK = "CREATE_TASK"
    UPDATE_TASK = "UPDATE_TASK"
    DELETE_TASK = "DELETE_TASK"
    LIST_TASKS = "LIST_TASKS"
    SEARCH_TASKS = "SEARCH_TASKS"
    FILTER_TASKS = "FILTER_TASKS"
    SORT_TASKS = "SORT_TASKS"
    GET_USER_INFO = "GET_USER_INFO"
    UNKNOWN = "UNKNOWN"


class EntityType(str, Enum):
    """Types of entities that can be extracted from user messages"""
    TASK_TITLE = "TASK_TITLE"
    TASK_DESCRIPTION = "TASK_DESCRIPTION"
    KEYWORD = "KEYWORD"
    STATUS_INDICATOR = "STATUS_INDICATOR"
    REFERENCE_DEMONSTRATIVE = "REFERENCE_DEMONSTRATIVE"
    DATE_REFERENCE = "DATE_REFERENCE"
    TASK_ID = "TASK_ID"
    TASK_UPDATE_VALUE = "TASK_UPDATE_VALUE"


class ExtractedEntity(BaseModel):
    """Represents an entity extracted from user input"""
    entity_type: EntityType
    entity_value: str
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    position_start: Optional[int] = None
    position_end: Optional[int] = None


class UserIntent(BaseModel):
    """Represents the intent identified from user input"""
    intent_type: IntentType
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    extracted_entities: List[ExtractedEntity] = []
    parameters: Dict[str, Any] = {}


class ChatMessage(BaseModel):
    """Represents a chat message"""
    message_id: str
    user_id: str
    message_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: str = "input"  # input or output
    session_id: Optional[str] = None


class ChatSession(BaseModel):
    """Represents a chat session"""
    session_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    conversation_state: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Represents a chat response from the bot"""
    response: str
    response_type: str = "success"  # success, clarification_needed, confirmation_required, error
    session_id: str
    task_id: Optional[str] = None
    suggestions: Optional[List[str]] = []
    intent_processed: Optional[UserIntent] = None
    metadata: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    """Represents a request to the chat system"""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None