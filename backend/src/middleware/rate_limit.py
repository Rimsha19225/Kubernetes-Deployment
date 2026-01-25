"""
Rate Limiting Middleware
Implements rate limiting for chat endpoints to prevent abuse
"""
import time
from typing import Dict, Optional
from collections import defaultdict
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to implement rate limiting for API endpoints
    """
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

        # Store request timestamps per key
        self.requests: Dict[str, list] = defaultdict(list)

    def _get_client_key(self, request: Request) -> str:
        """
        Extract rate limit key from request
        Uses IP address and user ID if available
        """
        # Get client IP
        client_host = request.client.host if request.client else "unknown"

        # Get user ID from headers if available
        user_id = request.headers.get("user-id", "anonymous")

        return f"{client_host}:{user_id}"

    def _is_allowed(self, key: str) -> bool:
        """
        Check if the key is allowed to make a request
        """
        now = time.time()
        # Remove requests older than 1 minute
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if now - timestamp < 60
        ]

        # Check if under limit
        if len(self.requests[key]) < self.requests_per_minute:
            # Add current request
            self.requests[key].append(now)
            return True

        return False

    async def dispatch(self, request: Request, call_next):
        # Only apply rate limiting to chat endpoints
        if request.url.path.startswith("/chat/"):
            key = self._get_client_key(request)

            if not self._is_allowed(key):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please slow down your requests."
                    }
                )

        response = await call_next(request)
        return response


def create_rate_limit_middleware(requests_per_minute: int = 60):
    """
    Factory function to create rate limiting middleware
    """
    def add_middleware(app):
        return RateLimitMiddleware(app, requests_per_minute=requests_per_minute)
    return add_middleware