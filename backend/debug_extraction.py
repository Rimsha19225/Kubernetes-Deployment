#!/usr/bin/env python3
"""
Debug script to understand entity extraction in detail
"""

import asyncio
import sys
import os
import re

# Add the backend src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.nlp_intent_processor import nlp_processor
from src.models.chat_models import IntentType


async def debug_extraction():
    """Debug the extraction process in detail"""

    print("Debugging entity extraction...")

    message = "update task id 101 title reading to read"
    message_lower = message.lower()

    print(f"Original message: {message}")
    print(f"Lowercase: {message_lower}")
    print()

    # Check the update-specific pattern
    update_to_pattern = r"(?:update|change|modify|edit).*?(?:title|description)\s+(.+?)\s+(?:to|as)\s+(.+)$"
    update_to_match = re.search(update_to_pattern, message_lower)
    print(f"Update pattern '{update_to_pattern}' matches: {bool(update_to_match)}")
    if update_to_match:
        print(f"  Group 1 (old): '{update_to_match.group(1)}'")
        print(f"  Group 2 (new): '{update_to_match.group(2)}'")
    print()

    # Check other title patterns that might interfere
    title_patterns = [
        r"(?:called|named|to|for)\s+(?:\"([^\"]+)\"|\'([^\']+)\'|([^.!?]+?)(?:\.|$|,))",  # This pattern may need more refinement, but keeping original for now
        r"(?:add|create|make|new)\s+(?:a\s+)?(?:task|todo|item)\s+(?:called|named|to|for)?\s+(.+?)(?:\.|$|,|and|\s+that)",
        r"task\s+(?:to\s+)?(.+)",  # Added: Handle "task ..." or "task to ..." - captures everything after "task" or "task to"
        r"i\s+need\s+to\s+(.+?)(?:\.|$|,|and|\s+so)",
        r"(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:to|and|with)",
        r"(?:mark|set)\s+(?:the\s+)?(.+?)\s+(?:as|to)",
    ]

    print("Checking general title patterns:")
    for i, pattern in enumerate(title_patterns):
        matches = re.findall(pattern, message)
        print(f"Pattern {i}: '{pattern}' -> {matches}")
        for match in matches:
            if isinstance(match, tuple):
                match = next((m for m in match if m), "")
            if match.strip():
                print(f"  -> Match: '{match.strip()}'")
    print()

    # Now test the actual NLP processor
    intent = await nlp_processor.process_intent(message, "1")
    print(f"Final entities from NLP processor: {[{'type': e.entity_type, 'value': e.entity_value} for e in intent.extracted_entities]}")


if __name__ == "__main__":
    asyncio.run(debug_extraction())