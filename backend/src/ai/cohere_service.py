"""
Cohere Service Module
Handles all AI operations using the Cohere API
"""
import os
from typing import Dict, List, Optional
from src.config import settings


class CohereService:
    """
    Service class to interact with the Cohere API
    """

    def __init__(self):
        """
        Initialize the Cohere service with the API key from configuration
        """
        self.api_key = settings.cohere_api_key
        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set")

    def get_api_key(self) -> str:
        """
        Returns the Cohere API key from configuration
        """
        return self.api_key

    def is_configured(self) -> bool:
        """
        Check if the Cohere service is properly configured with an API key
        """
        return bool(self.api_key)


# Global instance of the Cohere service
cohere_service = CohereService()