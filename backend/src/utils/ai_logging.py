"""
AI Logging Utility
Provides logging and monitoring for AI components
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import time

from src.utils.log_config import logger

class AILogger:
    """
    Specialized logger for AI components with additional context
    """
    def __init__(self, name: str = "ai_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def log_intent_processing(
        self,
        user_id: str,
        message: str,
        intent_type: str,
        confidence: float,
        entities: list,
        duration_ms: float = None
    ):
        """
        Log intent processing event
        """
        event_data = {
            "event_type": "intent_processing",
            "user_id": user_id,
            "message": message,
            "intent_type": intent_type,
            "confidence": confidence,
            "entities_count": len(entities),
            "timestamp": datetime.utcnow().isoformat(),
            **({"duration_ms": duration_ms} if duration_ms is not None else {})
        }

        self.logger.info(f"AI Intent Processing: {json.dumps(event_data)}")

    def log_api_call(
        self,
        api_endpoint: str,
        user_id: str,
        request_data: Dict[str, Any],
        response_status: int,
        duration_ms: float
    ):
        """
        Log API call event
        """
        event_data = {
            "event_type": "api_call",
            "api_endpoint": api_endpoint,
            "user_id": user_id,
            "response_status": response_status,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(f"AI API Call: {json.dumps(event_data)}")

    def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log error event
        """
        event_data = {
            "event_type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            **({"user_id": user_id} if user_id is not None else {}),
            **({"context": context} if context is not None else {})
        }

        self.logger.error(f"AI Error: {json.dumps(event_data)}")

    def log_security_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log security-related event
        """
        event_data = {
            "event_type": "security_event",
            "security_sub_type": event_type,
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            **({"details": details} if details is not None else {})
        }

        self.logger.warning(f"AI Security Event: {json.dumps(event_data)}")

    def measure_duration(self, func_name: str, user_id: str):
        """
        Context manager to measure function duration
        """
        class DurationMeasure:
            def __enter__(measure_self):
                measure_self.start_time = time.time()
                return measure_self

            def __exit__(measure_self, exc_type, exc_val, exc_tb):
                duration = (time.time() - measure_self.start_time) * 1000  # Convert to milliseconds
                if exc_type is None:
                    self.logger.info(
                        f"Function {func_name} completed for user {user_id} in {duration:.2f}ms"
                    )
                else:
                    self.logger.error(
                        f"Function {func_name} failed for user {user_id} after {duration:.2f}ms: {exc_val}"
                    )

        return DurationMeasure()


# Global AI logger instance
ai_logger = AILogger()