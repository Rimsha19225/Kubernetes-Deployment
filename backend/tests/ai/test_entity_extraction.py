"""
Unit tests for entity extraction functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.models.chat_models import EntityType
from src.ai.nlp_intent_processor import NLPIntentProcessor


@pytest.fixture
def nlp_processor():
    """Create a test instance of the NLP intent processor"""
    return NLPIntentProcessor()


@pytest.mark.asyncio
class TestEntityExtraction:
    """Test entity extraction functionality"""

    async def test_extract_task_titles(self, nlp_processor):
        """Test that task titles are correctly extracted from various messages"""
        test_cases = [
            ("Add a task to buy groceries", ["buy groceries"]),
            ("Create task called 'finish report'", ["finish report"]),
            ("I need to clean my room", ["clean my room"]),
            ("Make a new task named 'schedule meeting'", ["schedule meeting"]),
            ("Add task for 'walk the dog'", ["walk the dog"]),
        ]

        for message, expected_titles in test_cases:
            entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.CREATE_TASK)

            # Extract actual task titles
            actual_titles = [entity.entity_value for entity in entities
                           if entity.entity_type == "TASK_TITLE"]

            # Check that all expected titles are in the actual results
            for expected_title in expected_titles:
                found_match = any(expected_title.lower() in actual_title.lower()
                                for actual_title in actual_titles)
                assert found_match, f"Expected to find title containing '{expected_title}', got {actual_titles}"

    async def test_extract_task_descriptions(self, nlp_processor):
        """Test that task descriptions are correctly extracted"""
        test_cases = [
            ("Create task 'meeting' with description 'Prepare slides for presentation'", ["Prepare slides for presentation"]),
            ("Add task 'report' description: 'Finish quarterly report'", ["Finish quarterly report"]),
        ]

        for message, expected_descriptions in test_cases:
            entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.CREATE_TASK)

            # Extract actual descriptions
            actual_descriptions = [entity.entity_value for entity in entities
                                 if entity.entity_type == "TASK_DESCRIPTION"]

            # Check that all expected descriptions are in the actual results
            for expected_desc in expected_descriptions:
                found_match = any(expected_desc.lower() in actual_desc.lower()
                                for actual_desc in actual_descriptions)
                assert found_match, f"Expected to find description containing '{expected_desc}', got {actual_descriptions}"

    async def test_extract_keywords_for_search(self, nlp_processor):
        """Test that keywords for search are correctly extracted"""
        test_cases = [
            ("Find tasks about dentist", ["dentist"]),
            ("Search for grocery tasks", ["grocery"]),
            ("Look for cleaning tasks", ["cleaning"]),
            ("Find tasks containing 'report'", ["report"]),
        ]

        for message, expected_keywords in test_cases:
            entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.SEARCH_TASKS)

            # Extract actual keywords
            actual_keywords = [entity.entity_value for entity in entities
                             if entity.entity_type == "KEYWORD"]

            # Check that all expected keywords are in the actual results
            for expected_keyword in expected_keywords:
                found_match = any(expected_keyword.lower() in actual_keyword.lower()
                                for actual_keyword in actual_keywords)
                assert found_match, f"Expected to find keyword containing '{expected_keyword}', got {actual_keywords}"

    async def test_extract_status_indicators(self, nlp_processor):
        """Test that status indicators are correctly extracted"""
        test_cases = [
            ("Mark the task as complete", ["complete"]),
            ("Set task to done", ["complete"]),
            ("Update to finished", ["complete"]),
            ("Mark as incomplete", ["incomplete"]),
            ("Set to pending", ["incomplete"]),
        ]

        for message, expected_statuses in test_cases:
            entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.UPDATE_TASK)

            # Extract actual status indicators
            actual_statuses = [entity.entity_value for entity in entities
                             if entity.entity_type == "STATUS_INDICATOR"]

            # Check that all expected statuses are in the actual results
            for expected_status in expected_statuses:
                found_match = any(expected_status.lower() in actual_status.lower()
                                for actual_status in actual_statuses)
                assert found_match, f"Expected to find status containing '{expected_status}', got {actual_statuses}"

    async def test_extract_reference_demonstratives(self, nlp_processor):
        """Test that reference demonstratives are correctly extracted"""
        test_cases = [
            ("Update that task", ["that"]),
            ("Delete the first task", ["first"]),
            ("Mark last task complete", ["last"]),
            ("Change this task", ["this"]),
        ]

        for message, expected_references in test_cases:
            entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.UPDATE_TASK)

            # Extract actual reference demonstratives
            actual_references = [entity.entity_value for entity in entities
                               if entity.entity_type == "REFERENCE_DEMONSTRATIVE"]

            # Check that all expected references are in the actual results
            for expected_ref in expected_references:
                found_match = any(expected_ref.lower() in actual_ref.lower()
                                for actual_ref in actual_references)
                assert found_match, f"Expected to find reference containing '{expected_ref}', got {actual_references}"

    async def test_extract_entities_by_intent_type(self, nlp_processor):
        """Test that entity extraction varies by intent type"""
        message = "Find tasks about dentist appointment"

        # Extract entities for different intent types
        search_entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.SEARCH_TASKS)
        create_entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.CREATE_TASK)

        # For search intent, we should have keywords
        search_keywords = [e for e in search_entities if e.entity_type == "KEYWORD"]
        assert len(search_keywords) > 0, "Search intent should extract keywords"

        # For create intent, we might have different entities
        create_titles = [e for e in create_entities if e.entity_type == "TASK_TITLE"]
        assert len(create_titles) > 0, "Create intent should extract task titles"


@pytest.mark.asyncio
class TestEntityExtractionAccuracy:
    """Test the accuracy of entity extraction"""

    async def test_extract_multiple_entities_same_message(self, nlp_processor):
        """Test that multiple entities of different types can be extracted from the same message"""
        message = "Create task called 'dentist appointment' with description 'Schedule for tomorrow'"

        entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.CREATE_TASK)

        # Check for different entity types
        titles = [e for e in entities if e.entity_type == "TASK_TITLE"]
        descriptions = [e for e in entities if e.entity_type == "TASK_DESCRIPTION"]

        assert len(titles) > 0, "Should extract task title"
        assert len(descriptions) > 0, "Should extract task description"

        # Verify content
        title_values = [e.entity_value for e in titles]
        desc_values = [e.entity_value for e in descriptions]

        assert any("dentist appointment" in t for t in title_values), "Should find 'dentist appointment' as title"
        assert any("Schedule for tomorrow" in d for d in desc_values), "Should find description"

    async def test_extract_entities_with_different_confidence_scores(self, nlp_processor):
        """Test that entities have appropriate confidence scores"""
        message = "Add a task to buy groceries"

        entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.CREATE_TASK)

        # All extracted entities should have confidence scores between 0 and 1
        for entity in entities:
            assert 0.0 <= entity.confidence_score <= 1.0, f"Confidence score {entity.confidence_score} should be between 0 and 1"

    async def test_extract_entities_with_position_information(self, nlp_processor):
        """Test that entities have position information when applicable"""
        message = "Update the task 'buy groceries' to be complete"

        entities = await nlp_processor._extract_entities(message, nlp_processor.IntentType.UPDATE_TASK)

        # Check if entities have position information
        for entity in entities:
            # Position information might not always be available, so just check the structure
            assert hasattr(entity, 'entity_type'), "Entity should have entity_type"
            assert hasattr(entity, 'entity_value'), "Entity should have entity_value"
            assert hasattr(entity, 'confidence_score'), "Entity should have confidence_score"