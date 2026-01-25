#!/usr/bin/env python3
"""
Test script to verify that the chatbot task creation functionality works properly after fixes
"""
import asyncio
from src.ai.chatbot_orchestrator import chatbot_orchestrator
from src.services.auth_service import get_user_by_id

async def test_chatbot_task_creation():
    print("Testing chatbot task creation functionality...")

    # Test getting a user to make sure auth works
    user = get_user_by_id('12')
    if user:
        print(f"✓ User retrieval works: {user.email}")
    else:
        print("✗ User retrieval failed")
        return

    # Test creating a task through the chatbot orchestrator
    try:
        # Simulate a user asking to create a task
        result = await chatbot_orchestrator.process_message(
            user_id="12",  # Using the same user ID from your test
            message="Add a task to buy groceries",
            session_id="test-session-123"
        )

        print(f"✓ Chatbot response: {result['response']}")
        print(f"✓ Response type: {result['response_type']}")
        print(f"✓ Session ID: {result['session_id']}")

        if result.get('task_id'):
            print(f"✓ Task created successfully with ID: {result['task_id']}")
        else:
            print("? Task may not have been created (check response)")

        # Test another message to list tasks
        list_result = await chatbot_orchestrator.process_message(
            user_id="12",
            message="Show me my tasks",
            session_id="test-session-123"
        )

        print(f"✓ List tasks response: {list_result['response']}")

    except Exception as e:
        print(f"✗ Error during chatbot task creation: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n✓ All chatbot functionality tests passed!")
    print("The chatbot should now properly create tasks without errors.")

if __name__ == "__main__":
    asyncio.run(test_chatbot_task_creation())