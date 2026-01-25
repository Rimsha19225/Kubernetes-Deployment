"""
Test suite for verifying chat message storage in the database
"""
from sqlmodel import Session, select
from src.database.session import get_session
from src.models.chat import ChatMessage, ChatSession
from src.models.user import User
from src.services.chat_service import ChatService
from src.models.chat import ChatMessageType


def test_chat_message_storage():
    """Test that chat messages are properly stored in the database"""

    # Import the engine from the session module
    from src.database.session import engine

    with Session(engine) as session:
        # Create a test user (if not exists)
        test_user = session.exec(select(User).limit(1)).first()
        if not test_user:
            test_user = User(
                email="test@example.com",
                name="Test User",
                hashed_password="fake_hashed_password"
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

        # Test creating a chat session
        session_id = "test-session-id-123"
        chat_session = ChatService.create_chat_session(
            session=session,
            user_id=test_user.id,
            session_id=session_id,
            title="Test Chat Session"
        )

        assert chat_session.session_id == session_id
        assert chat_session.user_id == test_user.id

        # Test creating a user message
        user_message = ChatService.create_chat_message(
            session=session,
            user_id=test_user.id,
            session_id=session_id,
            content="Hello, how are you?",
            message_type=ChatMessageType.USER_INPUT
        )

        assert user_message.content == "Hello, how are you?"
        assert user_message.message_type == ChatMessageType.USER_INPUT
        assert user_message.session_id == session_id

        # Test creating an AI response
        ai_response = ChatService.create_chat_message(
            session=session,
            user_id=test_user.id,
            session_id=session_id,
            content="I'm doing great, thank you for asking!",
            message_type=ChatMessageType.AI_RESPONSE
        )

        assert ai_response.content == "I'm doing great, thank you for asking!"
        assert ai_response.message_type == ChatMessageType.AI_RESPONSE
        assert ai_response.session_id == session_id

        # Test retrieving messages by session
        messages = ChatService.get_chat_messages_by_session(session, session_id)
        assert len(messages) == 2
        assert messages[0].content == "Hello, how are you?"
        assert messages[1].content == "I'm doing great, thank you for asking!"

        # Test retrieving user's chat sessions
        user_sessions = ChatService.get_user_chat_sessions(session, test_user.id)
        assert len(user_sessions) >= 1
        session_found = any(s.session_id == session_id for s in user_sessions)
        assert session_found

        print("✅ All chat message storage tests passed!")

        # Clean up
        session.delete(ai_response)
        session.delete(user_message)
        session.delete(chat_session)
        session.commit()


if __name__ == "__main__":
    test_chat_message_storage()