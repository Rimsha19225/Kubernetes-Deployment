#!/usr/bin/env python3
"""
Test script to verify the fix for updating task titles
"""

import asyncio
import sys
import os

# Add the backend src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.nlp_intent_processor import nlp_processor
from src.ai.task_control import task_controller
from src.models.chat_models import IntentType


async def test_update_task_parsing():
    """Test that the NLP processor correctly identifies update task intents"""

    print("Testing NLP intent processing for update tasks...")

    # Test case 1: "update task id 101 title reading to read"
    message1 = "update task id 101 title reading to read"
    intent1 = await nlp_processor.process_intent(message1, "test_user_123")

    print(f"Message: {message1}")
    print(f"Intent type: {intent1.intent_type}")
    print(f"Confidence: {intent1.confidence_score}")
    print(f"Entities: {[{'type': e.entity_type, 'value': e.entity_value} for e in intent1.extracted_entities]}")
    print()

    # Test case 2: "update title reading to read"
    message2 = "update title reading to read"
    intent2 = await nlp_processor.process_intent(message2, "test_user_123")

    print(f"Message: {message2}")
    print(f"Intent type: {intent2.intent_type}")
    print(f"Confidence: {intent2.confidence_score}")
    print(f"Entities: {[{'type': e.entity_type, 'value': e.entity_value} for e in intent2.extracted_entities]}")
    print()

    # Test case 3: Verify it's identified as an UPDATE_TASK intent
    assert intent1.intent_type == IntentType.UPDATE_TASK, f"Expected UPDATE_TASK, got {intent1.intent_type}"
    assert intent2.intent_type == IntentType.UPDATE_TASK, f"Expected UPDATE_TASK, got {intent2.intent_type}"

    print("SUCCESS: NLP processing tests passed!")


if __name__ == "__main__":
    asyncio.run(test_update_task_parsing())