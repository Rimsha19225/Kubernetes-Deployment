"""
NLP Intent Processor
Processes natural language input to identify user intents and extract entities
"""
import re
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio

from src.models.chat_models import UserIntent, ExtractedEntity, IntentType, EntityType
from src.ai.cohere_service import cohere_service
from src.utils.ai_logging import ai_logger

logger = logging.getLogger(__name__)

class NLPIntentProcessor:
    """
    Processes natural language input to identify user intents and extract entities
    """
    def __init__(self):
        self.intent_patterns = {
            IntentType.CREATE_TASK: [
                r"task\s+(?:to\s+)?(.+)",  # Added: Handle "task ..." or "task to ..."
                r"(?:add|create|make|new)\s+(?:a\s+)?task\s+(?:called|named|to|for)?\s*(.+)",
                r"(?:add|create|make|new)\s+(?:a\s+)?(?:todo|item)\s+(?:called|named|to|for)?\s*(.+)",
                r"(?:please|can you)\s+(?:add|create|make)\s+(?:a\s+)?task\s+(?:called|named|to|for)?\s*(.+)",
                r"i\s+need\s+to\s+(.+)",
                r"remind\s+me\s+to\s+(.+)",
                r"don'?t\s+forget\s+to\s+(.+)"
            ],
            IntentType.UPDATE_TASK: [
                r"(?:update|change|modify|edit)\s+(?:the\s+)?(.+)\s+(?:title|description|status)",
                r"(?:update|change|modify|edit)\s+(?:task|the\s+.+?)\s+(?:to|with)\s+(.+)",
                r"(?:make|set)\s+(?:the\s+)?(.+)\s+(?:as\s+)?(?:complete|done|finished|incomplete|pending)",
                r"(?:mark|set)\s+(?:the\s+)?(.+)\s+(?:as\s+)?(?:complete|done|finished|incomplete|pending)",
                r"(?:update|change|modify|edit)\s+(?:the\s+)?(.+)\s+(?:to|and)\s+(?:be\s+)?(?:complete|done|finished|incomplete|pending)",
                # Patterns to handle "task update X with title/description Y" format
                r"task\s+update\s+(?:the\s+)?(.+)\s+with\s+(?:title|description)\s+(.+)",
                r"task\s+update\s+(?:the\s+)?(.+?)\s+(?:title|description)\s+(?:to|as)\s+(.+)",
                # New patterns to handle "task id X update title/description/to Y" format
                r"task\s+id\s+\d+\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(?:to|as)\s+(.+)",
                r"task\s+\d+\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(?:to|as)\s+(.+)",
                r"task\s+id\s+\d+\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(?:as|to)\s+(.+)",
                r"task\s+\d+\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(?:as|to)\s+(.+)",
                r"task\s+id\s+\d+\s+(?:update|change|modify|edit)\s+(?:the\s+)?(.+)",
                r"task\s+\d+\s+(?:update|change|modify|edit)\s+(?:the\s+)?(.+)",
                r"task\s+id\s+\d+\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(.+)",
                r"task\s+\d+\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(.+)",
                # New patterns for simple task updates like "update 'buy mobile' task to 'Buy Mobile'"
                r"(?:update|change|modify|edit)\s+(?:'|\"|\"|')[^'\"]+\s*(?:'|\"|\"|')\s+task\s+(?:to|as)\s+(?:'|\"|\"|')[^'\"]+\s*(?:'|\"|\"|')",
                # New patterns for simple task title updates like "bath update title to Bath"
                r"(.+)\s+(?:update|change|modify|edit)\s+(?:title|description)\s+(?:to|as)\s+(.+)",
                r"(.+)\s+(?:title|description)\s+(?:update|change|modify|edit)\s+(?:to|as)\s+(.+)",
                # New patterns for "update [task_name] task [field] to [value]" format
                r"(?:update|change|modify|edit)\s+(.+?)\s+task\s+(?:title|description)\s+(?:to|as)\s+(.+)",
                # Pattern for "update [task_name] task title to [value]" - specifically handle this case
                r"(?:update|change|modify|edit)\s+(.+?)\s+task\s+title\s+(?:to|as)\s+(.+)",
                # New patterns for "[task_name] task [field] update [value]" format
                r"(.+?)\s+task\s+(?:title|description)\s+(?:update|change|modify|edit)\s+(.+)",
                # New patterns for completing tasks like "complete this task", "finish this task"
                r"(?:complete|finish|done|do)\s+(?:this|the)\s+(?:task|it)",
                r"(?:mark|set)\s+(?:this|the)\s+(?:task|it)\s+(?:as\s+)?(?:complete|done|finished)"
            ],
            IntentType.DELETE_TASK: [
                r"(?:delete|remove|cancel|drop)\s+(?:the\s+)?(.+)",
                r"(?:delete|remove|cancel|drop)\s+(?:task|item)\s+(?:called|named)?\s*(.+)",
                r"(?:get\s+rid\s+of|dispose\s+of)\s+(?:the\s+)?(.+)",
                r"(?:please\s+)?(?:delete|remove|cancel|drop)\s+(?:the\s+)?(.+)",
                r"i\s+want\s+to\s+delete\s+(?:the\s+)?(.+)",
                r"i\s+don'?t\s+need\s+(?:the\s+)?(.+)\s+anymore",
                r"clean\s+up\s+(?:the\s+)?(.+)",
                # New pattern for "X delete this task" format
                r"(.+)\s+delete\s+(?:this\s+)?(?:task|it)",
                # New pattern for "delete 'task name' task" format
                r"(?:delete|remove|cancel|drop)\s+(?:'|\"|\"|')[^'\"]+\s*(?:'|\"|\"|')\s+task"
            ],
            IntentType.LIST_TASKS: [
                r"(?:show|list|display|get|see)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?tasks?",
                r"what\s+(?:are\s+)?(?:my\s+)?(?:current|pending|incomplete)?\s*tasks?",
                r"show\s+(?:me\s+)?(?:my\s+)?(?:current|pending|incomplete)?\s*tasks?",
                r"what\s+(?:do\s+i\s+have|tasks?\s+do\s+i\s+have)",
                r"(?:show|list|display|get|see)\s+(?:all\s+)?(?:my\s+)?(?:completed|done|finished)?\s*tasks?",
                r"what\s+is\s+on\s+(?:my\s+)?(?:todo|to-do)\s+list",
                r"i\s+want\s+to\s+see\s+(?:all\s+)?(?:my\s+)?tasks?",
                # New pattern for "show me the task list"
                r"show\s+(?:me\s+)?(?:the\s+)?(?:task\s+)?list"
            ],
            IntentType.SEARCH_TASKS: [
                r"(?:find|search|look\s+for|locate)\s+(?:tasks?|items?)\s+(?:about|for|containing|with)\s+(.+)",
                r"(?:find|search|look\s+for|locate)\s+(?:tasks?|items?)\s+(?:that|which)\s+(?:have|contain)\s+(.+)",
                r"show\s+(?:me\s+)?(?:tasks?|items?)\s+(?:about|for|containing|with)\s+(.+)",
                r"i\s+need\s+to\s+find\s+(?:tasks?|items?)\s+(?:about|for|containing|with)\s+(.+)",
                r"do\s+i\s+have\s+(?:any\s+)?tasks?\s+(?:about|for|containing|with)\s+(.+)",
                r"search\s+for\s+(?:tasks?|items?)\s+(?:about|for|containing|with)\s+(.+)",
                # New pattern for "search 'task name' task" format
                r"(?:search|find)\s+(?:'|\"|\"|')[^'\"]+\s*(?:'|\"|\"|')\s+task"
            ],
            IntentType.GET_USER_INFO: [
                r"who\s+am\s+i",
                r"what\s+is\s+my\s+(?:email|name|username|identity)",
                r"tell\s+me\s+about\s+myself",
                r"show\s+(?:me\s+)?(?:my\s+)?(?:profile|account|information)",
                r"what\s+is\s+my\s+(?:user\s+)?(?:name|id|identifier)",
                r"show\s+me\s+my\s+(?:email|profile|details)",
                r"i\s+want\s+to\s+know\s+my\s+(?:email|name|user\s+info)",
                r"what\s+email\s+am\s+i\s+using",
                r"who\s+is\s+logged\s+in",
                # New pattern for "what is my name"
                r"what\s+(?:is|are)\s+(?:my\s+)?name"
            ]
        }

        self.status_indicators = {
            "complete": ["complete", "done", "finished", "completed", "marked done"],
            "incomplete": ["incomplete", "pending", "not done", "not finished", "todo", "to do"]
        }

    async def process_intent(self, message: str, user_id: str) -> UserIntent:
        """
        Process the user message to identify intent and extract entities
        """
        with ai_logger.measure_duration("process_intent", user_id):
            # First check for multiple intents in the message
            multiple_intents = await self._detect_multiple_intents(message)

            if len(multiple_intents) > 1:
                # Handle compound requests with multiple intents
                intent_result = await self._handle_compound_request(message, multiple_intents)
            else:
                # First try pattern matching for quick identification
                intent_result = await self._identify_intent_by_pattern(message)

                if intent_result.intent_type == IntentType.UNKNOWN:
                    # If pattern matching fails, use AI for more sophisticated analysis
                    intent_result = await self._identify_intent_with_ai(message)

            # Extract entities regardless of how intent was identified
            entities = await self._extract_entities(message, intent_result.intent_type)
            intent_result.extracted_entities = entities

            # Store the original message in parameters for user info requests
            intent_result.parameters["original_message"] = message
            intent_result.parameters["multiple_intents_detected"] = len(multiple_intents) > 1

            ai_logger.log_intent_processing(
                user_id=user_id,
                message=message,
                intent_type=intent_result.intent_type.value,
                confidence=intent_result.confidence_score,
                entities=[entity.entity_value for entity in entities],
            )

            return intent_result

    async def _detect_multiple_intents(self, message: str) -> List[IntentType]:
        """
        Detect if the message contains multiple intents
        """
        intents_found = []
        message_lower = message.lower()

        # Look for conjunctions that might indicate multiple intents
        conjunctions = ['and', 'then', 'also', 'plus', 'with', ', and', ', then']
        has_conjunction = any(conj in message_lower for conj in conjunctions)

        # Count how many different intent patterns match
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    if intent_type not in intents_found:
                        intents_found.append(intent_type)

        # If conjunctions are present or multiple patterns match, return multiple intents
        if has_conjunction and len(intents_found) > 1:
            return intents_found

        return [intents_found[0]] if intents_found else []

    async def _handle_compound_request(self, message: str, intents: List[IntentType]) -> UserIntent:
        """
        Handle requests that contain multiple intents
        """
        # For now, return the primary intent (first detected)
        # In a more advanced implementation, we would handle multiple intents
        primary_intent = intents[0]

        # Create an intent result with compound information
        intent_result = UserIntent(
            intent_type=primary_intent,
            confidence_score=0.7,  # Lower confidence for compound requests
            parameters={
                "compound_request": True,
                "total_intents_detected": len(intents),
                "all_intents": [intent.value for intent in intents]
            }
        )

        return intent_result

    async def _identify_intent_by_pattern(self, message: str) -> UserIntent:
        """
        Identify intent using regex patterns
        Prioritize more specific patterns (like update/delete) over general ones (like create)
        """
        message_lower = message.lower().strip()

        # First, check for more specific patterns in order of specificity
        # Create patterns tend to be more general, so we check them last

        # Iterate through intent types in order of specificity (most specific first)
        ordered_intent_types = [
            IntentType.UPDATE_TASK,
            IntentType.DELETE_TASK,
            IntentType.LIST_TASKS,
            IntentType.SEARCH_TASKS,
            IntentType.GET_USER_INFO,
            IntentType.CREATE_TASK  # Most general, checked last
        ]

        for intent_type in ordered_intent_types:
            if intent_type in self.intent_patterns:
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        # Calculate confidence based on pattern match strength
                        confidence = 0.9  # High confidence for pattern match
                        return UserIntent(
                            intent_type=intent_type,
                            confidence_score=confidence,
                            parameters={"matched_pattern": pattern}
                        )

        # If no pattern matches, return unknown intent
        return UserIntent(intent_type=IntentType.UNKNOWN, confidence_score=0.1)

    async def _identify_intent_with_ai(self, message: str) -> UserIntent:
        """
        Use AI to identify intent when pattern matching fails
        For now, we'll simulate AI processing by using enhanced pattern matching
        In a real implementation, this would call the Cohere API
        """
        message_lower = message.lower().strip()

        # Enhanced semantic analysis
        if any(word in message_lower for word in ["add", "create", "new", "need to", "remind me to"]):
            return UserIntent(intent_type=IntentType.CREATE_TASK, confidence_score=0.8)
        elif any(word in message_lower for word in ["update", "change", "modify", "edit", "mark", "set"]):
            return UserIntent(intent_type=IntentType.UPDATE_TASK, confidence_score=0.8)
        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            return UserIntent(intent_type=IntentType.DELETE_TASK, confidence_score=0.8)
        elif any(word in message_lower for word in ["show", "list", "display", "what do i have"]):
            return UserIntent(intent_type=IntentType.LIST_TASKS, confidence_score=0.8)
        elif any(word in message_lower for word in ["find", "search", "look for"]):
            return UserIntent(intent_type=IntentType.SEARCH_TASKS, confidence_score=0.8)
        elif any(word in message_lower for word in ["who am i", "my email", "tell me about myself"]):
            return UserIntent(intent_type=IntentType.GET_USER_INFO, confidence_score=0.8)

        return UserIntent(intent_type=IntentType.UNKNOWN, confidence_score=0.3)

    async def _extract_entities(self, message: str, intent_type: IntentType) -> List[ExtractedEntity]:
        """
        Extract entities from the message based on the identified intent
        """
        entities = []
        message_lower = message.lower()

        # Extract task titles/descriptions based on intent
        if intent_type in [IntentType.CREATE_TASK, IntentType.UPDATE_TASK]:
            # For update operations, extract new title/description after "to" or "as" FIRST to avoid conflicts
            if intent_type == IntentType.UPDATE_TASK:
                # Look for patterns like "update task id 101 title reading to read"
                # or "update title reading to read"
                # or "update [task_name] task [field] to [value]"
                update_to_pattern = r"(?:update|change|modify|edit)\s+(.+?)\s+task\s+(?:title|description)\s+(.+?)\s+(?:to|as)\s+(.+)$"
                update_to_match = re.search(update_to_pattern, message_lower)

                if not update_to_match:
                    # Alternative pattern for "[task_name] task [field] update [value]" format
                    update_to_pattern = r"(.+?)\s+task\s+(?:title|description)\s+(?:update|change|modify|edit)\s+(.+)$"
                    update_to_match = re.search(update_to_pattern, message_lower)

                if not update_to_match:
                    # Alternative pattern for "update [task_name] task title to [value]" format
                    update_to_pattern = r"(?:update|change|modify|edit)\s+(.+?)\s+task\s+title\s+(?:to|as)\s+(.+)$"
                    update_to_match = re.search(update_to_pattern, message_lower)

                if not update_to_match:
                    # Alternative pattern for "update [field] to [value]" format
                    update_to_pattern = r"(?:update|change|modify|edit).*?(?:title|description)\s+(.+?)\s+(?:to|as)\s+(.+)$"
                    update_to_match = re.search(update_to_pattern, message_lower)

                if update_to_match:
                    if len(update_to_match.groups()) == 2:
                        # For pattern: "[task_name] task [field] update [value]" - groups are (task_name, new_value)
                        old_title = update_to_match.group(1).strip()
                        new_title = update_to_match.group(2).strip()
                    elif len(update_to_match.groups()) == 3:
                        # For pattern: "update [task_name] task [field] to [value]" - groups are (task_name, field, new_value)
                        old_title = update_to_match.group(1).strip()
                        new_title = update_to_match.group(3).strip()
                    else:
                        # For pattern: "update [field] to [value]" - groups are (field, new_value)
                        old_title = update_to_match.group(1).strip()
                        new_title = update_to_match.group(2).strip()

                    # Add the old title as TASK_TITLE entity to help identify which task to update
                    if old_title and old_title != new_title:
                        # Only add as TASK_TITLE if it's not already present
                        if not any(e.entity_type == EntityType.TASK_TITLE and e.entity_value == old_title for e in entities):
                            entities.append(ExtractedEntity(
                                entity_type=EntityType.TASK_TITLE,
                                entity_value=old_title,
                                confidence_score=0.85
                            ))

                    # Add the new title as a parameter for the update
                    # Only add if not already present
                    if not any(e.entity_type == EntityType.TASK_UPDATE_VALUE and e.entity_value == new_title for e in entities):
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.TASK_UPDATE_VALUE,
                            entity_value=new_title,
                            confidence_score=0.90
                        ))
                else:
                    # Alternative pattern for "update task id 101 title to read"
                    alt_update_pattern = r"(?:task\s+id\s+\d+\s+)?(?:update|change|modify|edit)\s+(?:the\s+)?(?:title|description)\s+(?:to|as)\s+(.+)$"
                    alt_update_match = re.search(alt_update_pattern, message_lower)
                    if alt_update_match:
                        new_value = alt_update_match.group(1).strip()
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.TASK_UPDATE_VALUE,
                            entity_value=new_value,
                            confidence_score=0.90
                        ))

            # First, check for structured formats like "Title: ..., Description: ..." before other patterns
            structured_patterns = [
                r".*?(?:Title|Task):\s*(.+?),\s*(?:Description|Desc):\s*(.+?)(?:\.|$)",  # Matches "Title: ... , Description: ..." format
                r".*?(?:Title|Task):\s*(.+?)\s+(?:Description|Desc):\s*(.+?)(?:\.|$)",  # Matches "Title: ... Description: ..." format
                # Additional pattern for "create title: ... description: ..." format
                r"(?:create|add|make|new)\s+(?:a\s+)?(?:task\s+)?title:\s*(.+?)\s+description:\s*(.+?)(?:\.|$| and|\s*$)",
                # Pattern for just "title: ... description: ..." format
                r".*?title:\s*(.+?)\s+description:\s*(.+?)(?:\.|$| and|\s*$)",
            ]

            structured_match_found = False
            for struct_pattern in structured_patterns:
                struct_match = re.search(struct_pattern, message, re.IGNORECASE)
                if struct_match:
                    title_part = struct_match.group(1).strip()
                    description_part = struct_match.group(2).strip()

                    if title_part:
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.TASK_TITLE,
                            entity_value=title_part,
                            confidence_score=0.95  # Higher confidence for structured format
                        ))

                    if description_part:
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.TASK_DESCRIPTION,
                            entity_value=description_part,
                            confidence_score=0.90  # Higher confidence for structured format
                        ))

                    structured_match_found = True
                    break

            # Check for the specific pattern "titled 'X' description Y" which is common phrasing
            if not structured_match_found:
                titled_desc_pattern = r".*?(?:titled|called|named)\s+[\"']([^\"']+)[\"']\s+description\s+(.+?)(?:\.|$|,|and|\s+with)"
                titled_desc_match = re.search(titled_desc_pattern, message, re.IGNORECASE)

                if titled_desc_match:
                    title_part = titled_desc_match.group(1).strip()
                    description_part = titled_desc_match.group(2).strip()

                    if title_part:
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.TASK_TITLE,
                            entity_value=title_part,
                            confidence_score=0.95
                        ))

                    if description_part:
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.TASK_DESCRIPTION,
                            entity_value=description_part,
                            confidence_score=0.90
                        ))

                    structured_match_found = True

            # Extract task ID if present (for update/delete operations)
            task_id_pattern = r"(?:task\s+id|task)\s+(\d+)"
            task_id_match = re.search(task_id_pattern, message, re.IGNORECASE)
            if task_id_match:
                task_id = task_id_match.group(1).strip()
                entities.append(ExtractedEntity(
                    entity_type=EntityType.TASK_ID,
                    entity_value=task_id,
                    confidence_score=0.95
                ))


            # Extract due date information
            date_patterns = [
                r"due date.*?(\d{1,2}\s*[/-]\s*\d{1,2}\s*[/-]\s*\d{2,4})",
                r"due date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"by\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"on\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"due date.*?(\d{1,2}\s+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+\d{2,4})",
                r"by\s+(\d{1,2}\s+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+\d{2,4})",
                r"on\s+(\d{1,2}\s+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+\d{2,4})",
                r"(\d{1,2}\s+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+\d{2,4})",
                r"due date.*?(\d{4}-\d{2}-\d{2})",
                r"(\d{4}-\d{2}-\d{2})",
            ]

            for date_pattern in date_patterns:
                date_match = re.search(date_pattern, message, re.IGNORECASE)
                if date_match:
                    date_part = date_match.group(1).strip()
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.DATE_REFERENCE,
                        entity_value=date_part,
                        confidence_score=0.85
                    ))
                    break

            # Additional check for day references like "25 Jan" without full year
            day_month_pattern = r"(\d{1,2}\s+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december))"
            day_month_match = re.search(day_month_pattern, message, re.IGNORECASE)
            if day_month_match and not any(e.entity_type == EntityType.DATE_REFERENCE for e in entities):
                date_part = day_month_match.group(1).strip()
                entities.append(ExtractedEntity(
                    entity_type=EntityType.DATE_REFERENCE,
                    entity_value=date_part,
                    confidence_score=0.80
                ))

            if not structured_match_found:
                # First, extract the main task content using the existing patterns
                # NOTE: Order matters - more specific patterns should come before general ones
                title_patterns = [
                    r"(?:called|named|to|for)\s+(?:\"([^\"]+)\"|\'([^\']+)\'|([^.!?]+?)(?:\.|$|,))",  # This pattern may need more refinement, but keeping original for now
                    r"(?:add|create|make|new)\s+(?:a\s+)?(?:task|todo|item)\s+(?:called|named|to|for)?\s+(.+?)(?:\.|$|,|and|\s+that)",
                    r"task\s+(?:to\s+)?(.+)",  # Added: Handle "task ..." or "task to ..." - captures everything after "task" or "task to"
                    r"i\s+need\s+to\s+(.+?)(?:\.|$|,|and|\s+so)",
                    # For UPDATE_TASK intent, avoid the generic "update X to Y" pattern as it conflicts with specific update formats
                    # Only use it for non-update tasks
                    r"(?:mark|set)\s+(?:the\s+)?(.+?)\s+(?:as|to)",
                ]

                # For UPDATE_TASK intent, avoid using the generic "(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:to|and|with)" pattern
                # since it conflicts with more specific update patterns
                if intent_type != IntentType.UPDATE_TASK:
                    title_patterns.append(r"(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+(?:to|and|with)")

                # For UPDATE_TASK intent, filter out patterns that might conflict with update expressions
                if intent_type == IntentType.UPDATE_TASK and ((" to " in message_lower or " as " in message_lower) and any(word in message_lower for word in ["update", "change", "modify", "edit"])):
                    # Remove the first pattern which catches "to read" incorrectly
                    title_patterns = title_patterns[1:]  # Exclude the first pattern that causes conflicts

                # Find the first successful match to get the actual task content
                main_task_content = None
                for pattern in title_patterns:
                    matches = re.findall(pattern, message)
                    for match in matches:
                        # Handle tuple results from grouped patterns
                        if isinstance(match, tuple):
                            match = next((m for m in match if m), "")

                        if match.strip():
                            # For UPDATE_TASK intents, avoid adding content that conflicts with already extracted update entities
                            current_match = match.strip()

                            # Skip if this match conflicts with already extracted update entities
                            if intent_type == IntentType.UPDATE_TASK:
                                # Check if this match contains or is contained in already extracted update values
                                skip_match = False
                                for entity in entities:
                                    if entity.entity_type == EntityType.TASK_UPDATE_VALUE:
                                        # If the current match contains the update value, it's likely a conflict
                                        if entity.entity_value.lower() in current_match.lower() or \
                                           current_match.lower() in entity.entity_value.lower():
                                            skip_match = True
                                            break

                                if skip_match:
                                    continue

                            main_task_content = current_match
                            break
                    if main_task_content:
                        break

                # If we extracted meaningful task content, check if it contains description separators
                if main_task_content:
                    # Look for potential descriptions in the task content
                    # Common patterns for separating title from description:
                    # - "title - description", "title : description", "title; description"
                    # - "title because description", "title since description"
                    description_patterns = [
                        r"(.+?)\s*[-–—:;]\s+(.+)",  # Matches "title - description" or "title: description"
                        r"(.+?)\s+(because|since|for|so|when)\s+(.+)",  # Matches "title because description"
                    ]

                    has_description = False
                    for desc_pattern in description_patterns:
                        desc_match = re.match(desc_pattern, main_task_content, re.IGNORECASE)
                        if desc_match:
                            # Extract both title and description
                            # For pattern r"(.+?)\s+(because|since|for|so|when)\s+(.+)",
                            # group(1) is title, group(2) is connector, group(3) is description
                            actual_title = desc_match.group(1).strip()
                            if desc_match.groups() and len(desc_match.groups()) >= 3:
                                description_part = desc_match.group(3).strip()
                            else:
                                # For pattern r"(.+?)\s*[-–—:;]\s+(.+)", group(2) is description
                                description_part = desc_match.group(2).strip()

                            if actual_title:
                                entities.append(ExtractedEntity(
                                    entity_type=EntityType.TASK_TITLE,
                                    entity_value=actual_title,
                                    confidence_score=0.9
                                ))

                            if description_part:
                                entities.append(ExtractedEntity(
                                    entity_type=EntityType.TASK_DESCRIPTION,
                                    entity_value=description_part,
                                    confidence_score=0.8
                                ))
                            has_description = True
                            break

                    # If no description was found in the task content, use the whole content as title
                    if not has_description:
                        # Only add as TASK_TITLE if not already present
                        if not any(e.entity_type == EntityType.TASK_TITLE and e.entity_value == main_task_content for e in entities):
                            entities.append(ExtractedEntity(
                                entity_type=EntityType.TASK_TITLE,
                                entity_value=main_task_content,
                                confidence_score=0.9
                            ))

            # Check if the entire message has a description separator (fallback approach)
            # For UPDATE_TASK intents, skip this fallback approach if we already have update-specific entities
            if intent_type != IntentType.UPDATE_TASK or not any(e.entity_type in [EntityType.TASK_UPDATE_VALUE, EntityType.TASK_ID] for e in entities):
                description_patterns = [
                    r"(.+?)\s*[-–—:;]\s+(.+)",  # Matches "title - description" or "title: description"
                    r"(.+?)\s+(because|since|for|so|when)\s+(.+)",  # Matches "title because description"
                ]

                found_separator = False
                for desc_pattern in description_patterns:
                    desc_match = re.match(desc_pattern, message, re.IGNORECASE)
                    if desc_match:
                        # Extract both title and description
                        # For pattern r"(.+?)\s+(because|since|for|so|when)\s+(.+)",
                        # group(1) is title, group(2) is connector, group(3) is description
                        # For pattern r"(.+?)\s*[-–—:;]\s+(.+)", group(1) is title, group(2) is description
                        actual_title = desc_match.group(1).strip()
                        if desc_match.groups() and len(desc_match.groups()) >= 3:
                            # This is the connector pattern
                            description_part = desc_match.group(3).strip()
                        else:
                            # This is the separator pattern
                            description_part = desc_match.group(2).strip()

                        if actual_title:
                            # Only add as TASK_TITLE if not already present
                            if not any(e.entity_type == EntityType.TASK_TITLE and e.entity_value == actual_title for e in entities):
                                entities.append(ExtractedEntity(
                                    entity_type=EntityType.TASK_TITLE,
                                    entity_value=actual_title,
                                    confidence_score=0.9
                                ))

                        if description_part:
                            entities.append(ExtractedEntity(
                                entity_type=EntityType.TASK_DESCRIPTION,
                                entity_value=description_part,
                                confidence_score=0.8
                            ))
                        found_separator = True
                        break
                # If we went through all patterns and none matched, found_separator remains False
            # For UPDATE_TASK intents when skipping the fallback entirely, set found_separator to True to skip the next part
            if intent_type == IntentType.UPDATE_TASK and any(e.entity_type in [EntityType.TASK_UPDATE_VALUE, EntityType.TASK_ID] for e in entities):
                found_separator = True

            # If no separator was found anywhere, try to extract a basic title from the message
            if not found_separator:
                # For UPDATE_TASK intents, skip this last resort if we already have update-specific entities
                if intent_type != IntentType.UPDATE_TASK or not any(e.entity_type in [EntityType.TASK_UPDATE_VALUE, EntityType.TASK_ID] for e in entities):
                    # As a last resort, just extract a title using the first available pattern
                    for pattern in title_patterns:
                        matches = re.findall(pattern, message)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = next((m for m in match if m), "")

                            task_title_value = match.strip()
                            if task_title_value:
                                # For UPDATE_TASK intents, avoid adding content that conflicts with already extracted update entities
                                skip_match = False
                                if intent_type == IntentType.UPDATE_TASK:
                                    # Check if this match contains or is contained in already extracted update values
                                    for entity in entities:
                                        if entity.entity_type == EntityType.TASK_UPDATE_VALUE:
                                            # If the current match contains the update value, it's likely a conflict
                                            if entity.entity_value.lower() in task_title_value.lower() or \
                                               task_title_value.lower() in entity.entity_value.lower():
                                                skip_match = True
                                                break

                                if skip_match:
                                    continue

                                # Only add as TASK_TITLE if not already present
                                if not any(e.entity_type == EntityType.TASK_TITLE and e.entity_value == task_title_value for e in entities):
                                    entities.append(ExtractedEntity(
                                        entity_type=EntityType.TASK_TITLE,
                                        entity_value=task_title_value,
                                        confidence_score=0.9
                                    ))
                                break
                        if entities and entities[-1].entity_type == EntityType.TASK_TITLE:
                            break

        # Extract keywords for search
        if intent_type == IntentType.SEARCH_TASKS:
            search_patterns = [
                r"(?:about|for|containing|with)\s+(?:\"([^\"]+)\"|\'([^\']+)\'|(\w+))",
                r"(?:find|search|look for)\s+(?:tasks?|items?)\s+(?:about|for|containing|with)\s+(.+?)(?:\.|$|,)",
                r"(?:do\s+i\s+have|have\s+i\s+got)\s+(?:any\s+)?(?:tasks?|items?)\s+(?:about|for|containing|with)\s+(.+?)(?:\.|$|,)"
            ]

            for pattern in search_patterns:
                matches = re.findall(pattern, message)
                for match in matches:
                    # Handle tuple results from grouped patterns
                    if isinstance(match, tuple):
                        match = next((m for m in match if m), "")

                    if match.strip():
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.KEYWORD,
                            entity_value=match.strip(),
                            confidence_score=0.8
                        ))

        # Extract filters for listing and searching
        if intent_type in [IntentType.LIST_TASKS, IntentType.SEARCH_TASKS]:
            # Look for status filters
            status_filters = [
                r"\b(completed?|done|finished)\b",
                r"\b(pending|incomplete|not done)\b",
                r"\b(active|current)\b"
            ]

            for pattern in status_filters:
                matches = re.findall(pattern, message_lower)
                for match in matches:
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.STATUS_INDICATOR,
                        entity_value=match.strip(),
                        confidence_score=0.7
                    ))

        # Extract status indicators only for task-related intents
        if intent_type in [IntentType.CREATE_TASK, IntentType.UPDATE_TASK, IntentType.LIST_TASKS, IntentType.SEARCH_TASKS]:
            for status_category, status_words in self.status_indicators.items():
                for word in status_words:
                    if word in message_lower:
                        entities.append(ExtractedEntity(
                            entity_type=EntityType.STATUS_INDICATOR,
                            entity_value=status_category,
                            confidence_score=0.8
                        ))

        # Extract specific completion/incompletion requests like "complete this task" or "mark task as incomplete"
        # Only for task-related intents
        if intent_type in [IntentType.UPDATE_TASK, IntentType.CREATE_TASK]:
            completion_patterns = [
                r"complete\s+(?:this|the)\s+(?:task|it)",
                r"finish\s+(?:this|the)\s+(?:task|it)",
                r"done\s+(?:with|this|the)\s+(?:task|it)",
                r"mark\s+(?:this|the)\s+(?:task|it)\s+as\s+(?:complete|done|finished)",
            ]

            for pattern in completion_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.STATUS_INDICATOR,
                        entity_value="complete",
                        confidence_score=0.95
                    ))
                    # Add reference demonstrative to identify which task to complete
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.REFERENCE_DEMONSTRATIVE,
                        entity_value="this",
                        confidence_score=0.95
                    ))

            # Extract incompletion requests like "mark task as incomplete"
            incompletion_patterns = [
                r"incomplete\s+(?:this|the)\s+(?:task|it)",
                r"mark\s+(?:this|the)\s+(?:task|it)\s+as\s+(?:incomplete|pending|not done)",
                r"mark\s+(?:task|it)\s+as\s+(?:incomplete|pending|not done)"
            ]

            for pattern in incompletion_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.STATUS_INDICATOR,
                        entity_value="incomplete",
                        confidence_score=0.95
                    ))
                    # Add reference demonstrative to identify which task to update
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.REFERENCE_DEMONSTRATIVE,
                        entity_value="this",
                        confidence_score=0.95
                    ))

        # Extract reference demonstratives only for task-related intents
        if intent_type in [IntentType.UPDATE_TASK, IntentType.DELETE_TASK, IntentType.LIST_TASKS]:
            reference_patterns = [r"\b(this|that|these|those|first|last|next|previous|one|ones)\b"]
            for pattern in reference_patterns:
                matches = re.finditer(pattern, message_lower)
                for match in matches:
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.REFERENCE_DEMONSTRATIVE,
                        entity_value=match.group(1),
                        confidence_score=0.7,
                        position_start=match.start(),
                        position_end=match.end()
                    ))

            # Extract ordinal references like "second", "third", etc.
            ordinal_patterns = [r"\b(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b"]
            for pattern in ordinal_patterns:
                matches = re.finditer(pattern, message_lower)
                for match in matches:
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.REFERENCE_DEMONSTRATIVE,
                        entity_value=match.group(1),
                        confidence_score=0.6,  # Lower confidence for ordinals
                        position_start=match.start(),
                        position_end=match.end()
                    ))

        return entities

    def validate_intent_confidence(self, intent: UserIntent, threshold: float = 0.5) -> bool:
        """
        Validate if the intent confidence is above the threshold
        """
        return intent.confidence_score >= threshold


# Global instance of the NLP intent processor
nlp_processor = NLPIntentProcessor()