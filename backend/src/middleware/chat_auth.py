"""
Chat Authentication Middleware
Validates authentication for chat endpoints
"""
from fastapi import HTTPException, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime
import logging

from src.config import settings
from src.models.user import User
from src.services.auth_service import decode_access_token, get_user_by_id

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def validate_chat_authentication(request: Request) -> Optional[User]:
    """
    Validates JWT token for chat endpoints and returns the authenticated user
    """
    try:
        # Get the authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        # Extract the token
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        if not token:
            raise HTTPException(status_code=401, detail="Token missing")

        # Decode and validate the token
        user_data = decode_access_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract user identifier from the token (sub field)
        user_identifier = user_data.get("sub")

        # Get the actual user from the database using the identifier
        user = get_user_by_id(str(user_identifier))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except jwt.ExpiredSignatureError:
        logger.warning("Expired token attempted for chat endpoint")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        logger.error(f"JWT error during chat authentication: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error during chat authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error")