"""
Quality Guard
Validates responses for safety and accuracy, preventing hallucinations
"""
from typing import Dict, Any, List, Optional
import logging
import re
from datetime import datetime

from src.models.chat_models import UserIntent
from src.utils.ai_logging import ai_logger

logger = logging.getLogger(__name__)

class QualityGuard:
    """
    Validates responses for safety and accuracy, preventing hallucinations
    """
    def __init__(self):
        self.sensitive_patterns = [
            # Patterns that might reveal system internals or enable prompt injection
            r"(system|internal|config|setting|environment|variable|password|secret|token|key)[:\s]+",
            r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bCREATE\b|\bALTER\b|\bEXEC\b|\bUNION\b)",
            r"(admin|root|superuser|privileged).*access",
            r"(\.\./|\.\.\\|~/.*)",  # Path traversal attempts
            r"(cmd|sh|bash|powershell|script)[:\s]+"
        ]

        self.hallucination_keywords = [
            # Keywords that indicate potential hallucinations
            "imagined", "made-up", "fictional", "hypothetical", "invented",
            "pretend", "supposed", "alleged", "rumored", "unverified"
        ]

        self.personal_data_patterns = [
            # Patterns that might accidentally expose personal data
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone number
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email (but we need to allow legitimate emails)
        ]

    def validate_response(
        self,
        response: str,
        intent: UserIntent,
        user_context: Dict[str, Any],
        api_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate the response for safety and accuracy
        """
        try:
            validation_result = {
                "is_valid": True,
                "issues": [],
                "sanitized_response": response,
                "confidence": 1.0
            }

            # Check for sensitive information disclosure
            sensitive_check = self._check_sensitive_disclosure(response)
            if sensitive_check["has_issues"]:
                validation_result["is_valid"] = False
                validation_result["issues"].extend(sensitive_check["issues"])
                validation_result["sanitized_response"] = sensitive_check["sanitized_response"]

            # Check for potential hallucinations
            hallucination_check = self._check_hallucinations(response, api_result)
            if hallucination_check["has_issues"]:
                validation_result["is_valid"] = False
                validation_result["issues"].extend(hallucination_check["issues"])

            # Check for data isolation violations
            isolation_check = self._check_data_isolation(response, user_context)
            if isolation_check["has_issues"]:
                validation_result["is_valid"] = False
                validation_result["issues"].extend(isolation_check["issues"])

            # Calculate confidence based on validation results
            validation_result["confidence"] = self._calculate_confidence(validation_result["issues"])

            if not validation_result["is_valid"]:
                # If validation failed, provide a safer fallback response
                validation_result["sanitized_response"] = self._generate_safe_fallback(intent, validation_result["issues"])

            return validation_result

        except Exception as e:
            # Use user_context from parameters, but handle case where it might be problematic
            user_id = user_context.get("user_id") if user_context and isinstance(user_context, dict) else "unknown"
            ai_logger.log_error("response_validation_failed", str(e), user_id)
            return {
                "is_valid": False,
                "issues": ["Error during response validation"],
                "sanitized_response": "I'm sorry, but I encountered an error processing your request.",
                "confidence": 0.0
            }

    def _check_sensitive_disclosure(self, response: str) -> Dict[str, Any]:
        """
        Check if the response contains sensitive system information
        """
        issues = []
        sanitized_response = response
        has_issues = False

        for pattern in self.sensitive_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                has_issues = True
                issues.append({
                    "type": "sensitive_disclosure",
                    "description": "Response may contain sensitive system information",
                    "pattern": pattern
                })

        return {
            "has_issues": has_issues,
            "issues": issues,
            "sanitized_response": sanitized_response
        }

    def _check_hallucinations(self, response: str, api_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check for potential hallucinations in the response
        """
        issues = []
        has_issues = False

        # Check for hallucination keywords
        for keyword in self.hallucination_keywords:
            if keyword.lower() in response.lower():
                has_issues = True
                issues.append({
                    "type": "hallucination",
                    "description": f"Response contains potential hallucination keyword: {keyword}",
                    "keyword": keyword
                })

        # Check if response contradicts API result
        if api_result and "error" in api_result and "error" not in response.lower():
            has_issues = True
            issues.append({
                "type": "inconsistency",
                "description": "Response doesn't acknowledge API error"
            })

        # Check for unsafe operations
        if "delete" in response.lower() and not api_result.get("confirmed", False):
            has_issues = True
            issues.append({
                "type": "safety_violation",
                "description": "Response suggests completed deletion without confirmation"
            })

        # Check for privacy violations - ensure user only sees their own information
        if "email" in response.lower() or "user" in response.lower():
            # Verify that the user context matches the information being returned
            if api_result and "user_id" in api_result:
                result_user_id = api_result["user_id"]
                context_user_id = user_context.get("user_id")
                if result_user_id != context_user_id:
                    has_issues = True
                    issues.append({
                        "type": "privacy_violation",
                        "description": "Response contains information for wrong user"
                    })

        return {
            "has_issues": has_issues,
            "issues": issues
        }

    def _check_data_isolation(self, response: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for potential data isolation violations
        """
        issues = []
        has_issues = False

        # In a real implementation, this would check that the response
        # only contains data belonging to the current user
        # For now, we'll just log the check
        user_id = user_context.get("user_id")

        # Check if response contains patterns that might indicate cross-user data access
        # This is a simplified check - in reality, we'd need to verify that all
        # data in the response belongs to the current user
        if user_id and f"user_{user_id}" not in response:
            # This is a very basic check - in practice, we'd need more sophisticated validation
            pass

        return {
            "has_issues": has_issues,
            "issues": issues
        }

    def validate_intent_accuracy(
        self,
        user_message: str,
        identified_intent: UserIntent,
        extracted_entities: List[Any]
    ) -> Dict[str, Any]:
        """
        Validate that the identified intent accurately reflects the user's message
        """
        try:
            validation_result = {
                "is_accurate": True,
                "confidence": identified_intent.confidence_score,
                "suggestions": []
            }

            # Check if intent seems appropriate for the message
            message_lower = user_message.lower()
            intent_value = identified_intent.intent_type.value.lower()

            # Some basic heuristics to validate intent accuracy
            if "create" in message_lower and "CREATE_TASK" not in intent_value:
                validation_result["is_accurate"] = False
                validation_result["confidence"] *= 0.5
                validation_result["suggestions"].append("Consider if this is a task creation request")

            if "delete" in message_lower and "DELETE_TASK" not in intent_value:
                validation_result["is_accurate"] = False
                validation_result["confidence"] *= 0.5
                validation_result["suggestions"].append("Consider if this is a task deletion request")

            if "list" in message_lower and "LIST_TASKS" not in intent_value:
                validation_result["is_accurate"] = False
                validation_result["confidence"] *= 0.5
                validation_result["suggestions"].append("Consider if this is a task listing request")

            # Adjust confidence based on entity extraction quality
            if not extracted_entities:
                validation_result["confidence"] *= 0.8

            return validation_result

        except Exception as e:
            ai_logger.log_error("intent_validation_failed", str(e))
            return {
                "is_accurate": False,
                "confidence": 0.0,
                "suggestions": ["Error during intent validation"]
            }

    def validate_deletion_safety(
        self,
        user_context: Dict[str, Any],
        target_task_id: str,
        confirmation_required: bool = True
    ) -> Dict[str, Any]:
        """
        Validate that a deletion operation is safe to perform
        """
        try:
            user_id = user_context.get("user_id")

            # Check if user has permission to delete tasks
            permission_check = self.validate_user_permissions(
                user_context,
                "delete_task",
                target_task_id
            )

            if not permission_check["has_permission"]:
                return {
                    "is_safe": False,
                    "reason": "User does not have permission to delete tasks",
                    "requires_confirmation": False
                }

            # Deletion should always require confirmation for safety
            if confirmation_required:
                return {
                    "is_safe": True,
                    "reason": "Deletion is safe but requires user confirmation",
                    "requires_confirmation": True
                }
            else:
                return {
                    "is_safe": True,
                    "reason": "Deletion is safe to proceed",
                    "requires_confirmation": False
                }

        except Exception as e:
            ai_logger.log_error("deletion_safety_validation_failed", str(e), user_id)
            return {
                "is_safe": False,
                "reason": "Error during safety validation",
                "requires_confirmation": True
            }

    def _calculate_confidence(self, issues: List[Dict[str, Any]]) -> float:
        """
        Calculate overall confidence based on validation issues
        """
        if not issues:
            return 1.0

        # Base confidence starts high and decreases with each issue
        confidence = 1.0
        for issue in issues:
            issue_type = issue.get("type", "")
            if issue_type in ["sensitive_disclosure", "security_violation", "safety_violation"]:
                confidence -= 0.4  # Major issues significantly reduce confidence
            elif issue_type in ["hallucination", "inconsistency"]:
                confidence -= 0.2  # Moderate issues reduce confidence
            else:
                confidence -= 0.1  # Minor issues slightly reduce confidence

        return max(0.0, min(1.0, confidence))  # Clamp between 0 and 1

    def _generate_safe_fallback(self, intent: UserIntent, issues: List[Dict[str, Any]]) -> str:
        """
        Generate a safe fallback response when validation fails
        """
        if intent.intent_type.value == "CREATE_TASK":
            return "I had trouble creating that task. Could you try rephrasing your request?"
        elif intent.intent_type.value == "DELETE_TASK":
            return "I couldn't delete that task. Please check the task name and try again."
        elif intent.intent_type.value == "LIST_TASKS":
            return "I'm having trouble retrieving your tasks. Please try again in a moment."
        elif intent.intent_type.value == "GET_USER_INFO":
            return "I'm having trouble retrieving your user information. Please try again."
        else:
            return "I'm having trouble processing your request. Could you try rephrasing that?"

    def validate_user_permissions(
        self,
        user_context: Dict[str, Any],
        requested_operation: str,
        target_resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate that the user has permission to perform the requested operation
        """
        try:
            user_id = user_context.get("user_id")
            permissions = user_context.get("permissions", [])

            # Define required permissions for each operation
            permission_map = {
                "create_task": ["create_own_tasks"],
                "read_task": ["read_own_tasks"],
                "update_task": ["update_own_tasks"],
                "delete_task": ["delete_own_tasks"],
                "read_profile": ["read_own_profile"]
            }

            required_perms = permission_map.get(requested_operation, [])

            has_permission = any(perm in permissions for perm in required_perms)

            return {
                "has_permission": has_permission,
                "required_permissions": required_perms,
                "user_permissions": permissions
            }

        except Exception as e:
            user_id = user_context.get("user_id") if user_context and isinstance(user_context, dict) else "unknown"
            ai_logger.log_error("permission_validation_failed", str(e), user_id)
            return {
                "has_permission": False,
                "required_permissions": [],
                "user_permissions": []
            }


# Global instance of the quality guard
quality_guard = QualityGuard()