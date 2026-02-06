"""
Configuration settings for the LLM Chat Interface
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Configuration
    MODEL_OPTIONS = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    
    # Default Parameters
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0
    TEMPERATURE_STEP = 0.1
    MIN_TOKENS = 1
    MAX_TOKENS = 4096
    TOKEN_STEP = 50
    
    # UI Configuration
    PAGE_TITLE = "LLM Chat Interface"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"
    
    # History Configuration
    MAX_HISTORY_DISPLAY = 5
    MAX_CONTEXT_MESSAGES = 10  # Maximum messages to include in context
    PREVIEW_LENGTH = {
        'system': 200,
        'user': 200,
        'response': 300
    }
    
    @classmethod
    def validate_api_key(cls):
        """Validate that API key is available"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return True
