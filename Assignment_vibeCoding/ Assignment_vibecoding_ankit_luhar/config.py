"""
Configuration constants and settings for the AI Assistant application.
"""

# API Configuration
MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.7
TIMEOUT_SECONDS = 30
MAX_RETRIES = 3

# Default System Prompt
DEFAULT_SYSTEM_PROMPT = """You are a helpful, professional AI assistant. 
Provide accurate, concise, and well-structured responses. 
Always be respectful and considerate in your interactions."""

# Model Configuration with token limits (Updated with latest Groq models)
MODEL_CONFIGS = {
    "llama-3.3-70b-versatile": {
        "max_tokens": 131072,
        "description": "Latest Llama 3.3 70B model for versatile tasks"
    },
    "llama-3.1-8b-instant": {
        "max_tokens": 131072,
        "description": "Fast Llama 3.1 8B model for quick responses"
    },
    "gpt-oss-120b": {
        "max_tokens": 8192,
        "description": "OpenAI GPT OSS 120B model for complex tasks"
    },
    "gpt-oss-20b": {
        "max_tokens": 8192,
        "description": "OpenAI GPT OSS 20B model for balanced performance"
    },
    "llama-guard-4-12b": {
        "max_tokens": 131072,
        "description": "Llama Guard 4 12B for content moderation"
    },
    "compound": {
        "max_tokens": 8192,
        "description": "Compound system with web search and code execution"
    },
    "compound-mini": {
        "max_tokens": 4096,
        "description": "Compact compound system for quick tasks"
    }
}

# UI Configuration
PAGE_TITLE = "AI Assistant"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# Input Validation
MAX_PROMPT_LENGTH = 10000
MIN_PROMPT_LENGTH = 1

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_WINDOW_SECONDS = 60

# Security
ALLOWED_HTML_TAGS = ["p", "br", "strong", "em", "ul", "ol", "li", "code", "pre"]
XSS_PROTECTION_ENABLED = True

# Performance
CACHE_TTL_SECONDS = 300
DEBOUNCE_DELAY_MS = 500
