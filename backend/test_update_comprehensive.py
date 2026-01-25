#!/usr/bin/env python3
"""
Test script to verify the complete fix for updating task titles
"""

import asyncio
import sys
import os

# Add the backend src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.nlp_intent_processor import nlp_processor
from src.ai.task_control import task_controller
from src.models.chat_models import IntentType, UserIntent, ExtractedEntity, EntityType


async def test_complete_update_flow():
    """Test the complete flow from NLP processing to task control execution"""

    print("Testing complete update task flow...")

    # Test case: "update task id 101 title reading to read"
    message = "update task id 101 title reading to read"

    # Step 1: Process intent with NLP
    intent = await nlp_processor.process_intent(message, "1")

    print(f"Message: {message}")
    print(f"Intent type: {intent.intent_type}")
    print(f"Confidence: {intent.confidence_score}")
    print(f"Entities: {[{'type': e.entity_type, 'value': e.entity_value} for e in intent.extracted_entities]}")
    print()

    # Verify the intent is correctly identified
    assert intent.intent_type == IntentType.UPDATE_TASK, f"Expected UPDATE_TASK, got {intent.intent_type}"

    # Verify the entities are correctly extracted
    entity_types = [e.entity_type for e in intent.extracted_entities]
    assert EntityType.TASK_ID in entity_types, "Missing TASK_ID entity"
    assert EntityType.TASK_UPDATE_VALUE in entity_types, "Missing TASK_UPDATE_VALUE entity"

    # Find the specific values
    task_id = None
    old_title = None
    new_title = None

    for entity in intent.extracted_entities:
        if entity.entity_type == EntityType.TASK_ID:
            task_id = entity.entity_value
        elif entity.entity_type == EntityType.TASK_TITLE and entity.entity_value == "reading":
            old_title = entity.entity_value
        elif entity.entity_type == EntityType.TASK_UPDATE_VALUE:
            new_title = entity.entity_value

    print(f"Extracted - Task ID: {task_id}, Old Title: {old_title}, New Title: {new_title}")
    assert task_id == "101", f"Expected task_id '101', got {task_id}"
    assert old_title == "reading", f"Expected old title 'reading', got {old_title}"
    assert new_title == "read", f"Expected new title 'read', got {new_title}"

    print()
    print("SUCCESS: Complete update task flow test passed!")


async def test_simple_update_flow():
    """Test the simpler update flow without explicit task ID"""

    print("Testing simple update task flow...")

    # Test case: "update title reading to read"
    message = "update title reading to read"

    # Step 1: Process intent with NLP
    intent = await nlp_processor.process_intent(message, "1")

    print(f"Message: {message}")
    print(f"Intent type: {intent.intent_type}")
    print(f"Confidence: {intent.confidence_score}")
    print(f"Entities: {[{'type': e.entity_type, 'value': e.entity_value} for e in intent.extracted_entities]}")
    print()

    # Verify the intent is correctly identified
    assert intent.intent_type == IntentType.UPDATE_TASK, f"Expected UPDATE_TASK, got {intent.intent_type}"

    # Verify the entities are correctly extracted
    entity_types = [e.entity_type for e in intent.extracted_entities]
    assert EntityType.TASK_UPDATE_VALUE in entity_types, "Missing TASK_UPDATE_VALUE entity"

    # Find the specific values
    old_title = None
    new_title = None

    for entity in intent.extracted_entities:
        if entity.entity_type == EntityType.TASK_TITLE and entity.entity_value == "reading":
            old_title = entity.entity_value
        elif entity.entity_type == EntityType.TASK_UPDATE_VALUE:
            new_title = entity.entity_value

    print(f"Extracted - Old Title: {old_title}, New Title: {new_title}")
    assert old_title == "reading", f"Expected old title 'reading', got {old_title}"
    assert new_title == "read", f"Expected new title 'read', got {new_title}"

    print()
    print("SUCCESS: Simple update task flow test passed!")


if __name__ == "__main__":
    print("Running comprehensive update task tests...\n")
    asyncio.run(test_complete_update_flow())
    print()
    asyncio.run(test_simple_update_flow())
    print("\nAll tests completed successfully!")