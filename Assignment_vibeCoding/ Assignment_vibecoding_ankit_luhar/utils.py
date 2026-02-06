"""
Utility functions for the AI Assistant application.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from groq import Groq
from dotenv import load_dotenv
import streamlit as st
from config import (
    TIMEOUT_SECONDS, MAX_RETRIES, DEFAULT_TEMPERATURE, MAX_TOKENS,
    MODEL_CONFIGS, MAX_PROMPT_LENGTH, MIN_PROMPT_LENGTH,
    RATE_LIMIT_REQUESTS_PER_MINUTE, RATE_LIMIT_WINDOW_SECONDS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_groq_client() -> Optional[Groq]:
    """
    Create and return a configured Groq client.
    
    Returns:
        Groq client instance or None if API key is not found
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            return None
        
        client = Groq(api_key=api_key)
        logger.info("Groq client created successfully")
        return client
    except Exception as e:
        logger.error(f"Error creating Groq client: {str(e)}")
        return None

def validate_inputs(system_prompt: str, user_prompt: str, temperature: float) -> Tuple[bool, str]:
    """
    Validate user inputs.
    
    Args:
        system_prompt: System prompt text
        user_prompt: User prompt text
        temperature: Temperature value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not user_prompt or len(user_prompt.strip()) < MIN_PROMPT_LENGTH:
        return False, "User prompt is required and cannot be empty"
    
    if len(user_prompt) > MAX_PROMPT_LENGTH:
        return False, f"User prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters"
    
    if len(system_prompt) > MAX_PROMPT_LENGTH:
        return False, f"System prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters"
    
    if not (0.0 <= temperature <= 2.0):
        return False, "Temperature must be between 0.0 and 2.0"
    
    return True, ""

def generate_response(
    client: Groq,
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float = DEFAULT_TEMPERATURE
) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    """
    Generate AI response using Groq API with retry logic.
    
    Args:
        client: Groq client instance
        system_prompt: System prompt text
        user_prompt: User prompt text
        model: Model name to use
        temperature: Temperature for generation
        
    Returns:
        Tuple of (response, metadata, error_message)
    """
    messages = []
    
    # Add system prompt if provided
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    
    # Add user prompt
    messages.append({"role": "user", "content": user_prompt.strip()})
    
    start_time = time.time()
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Attempt {attempt + 1} to generate response using model: {model}")
            
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=MAX_TOKENS,
                timeout=TIMEOUT_SECONDS
            )
            
            response = chat_completion.choices[0].message.content
            end_time = time.time()
            
            # Calculate metadata
            metadata = {
                "model": model,
                "temperature": temperature,
                "response_time": round(end_time - start_time, 2),
                "prompt_tokens": getattr(chat_completion.usage, 'prompt_tokens', 0) if chat_completion.usage else 0,
                "completion_tokens": getattr(chat_completion.usage, 'completion_tokens', 0) if chat_completion.usage else 0,
                "total_tokens": getattr(chat_completion.usage, 'total_tokens', 0) if chat_completion.usage else 0,
                "attempt": attempt + 1
            }
            
            logger.info(f"Response generated successfully in {metadata['response_time']} seconds")
            return response, metadata, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Attempt {attempt + 1} failed: {error_msg}")
            
            if attempt == MAX_RETRIES - 1:
                return None, None, f"Failed to generate response after {MAX_RETRIES} attempts: {error_msg}"
            
            # Exponential backoff
            time.sleep(2 ** attempt)
    
    return None, None, "Unknown error occurred"

def format_response(response: str) -> str:
    """
    Format and sanitize the AI response.
    
    Args:
        response: Raw response from AI
        
    Returns:
        Formatted and sanitized response
    """
    if not response:
        return ""
    
    # Basic sanitization
    response = response.strip()
    
    # Ensure proper markdown formatting
    if not response.startswith('#') and not response.startswith('*') and not response.startswith('-'):
        # Add basic formatting if missing
        lines = response.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('-', '*', '#', '>', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        response = '\n'.join(formatted_lines)
    
    return response

def calculate_metrics(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate additional metrics from response metadata.
    
    Args:
        metadata: Response metadata
        
    Returns:
        Dictionary with calculated metrics
    """
    if not metadata:
        return {}
    
    metrics = {
        "tokens_per_second": 0,
        "cost_estimate": 0.0
    }
    
    if metadata.get("response_time", 0) > 0:
        metrics["tokens_per_second"] = round(
            metadata.get("total_tokens", 0) / metadata["response_time"], 2
        )
    
    # Rough cost estimation (adjust based on actual pricing)
    cost_per_1k_tokens = 0.001  # Example rate
    metrics["cost_estimate"] = round(
        metadata.get("total_tokens", 0) * cost_per_1k_tokens / 1000, 6
    )
    
    return metrics

def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get model information and configuration.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model configuration dictionary
    """
    return MODEL_CONFIGS.get(model_name, {
        "max_tokens": 4096,
        "description": "Unknown model"
    })

def check_rate_limit() -> Tuple[bool, Optional[str]]:
    """
    Check if the user has exceeded the rate limit.
    
    Returns:
        Tuple of (is_allowed, error_message)
    """
    if 'request_history' not in st.session_state:
        st.session_state.request_history = []
    
    current_time = time.time()
    
    # Remove old requests outside the time window
    st.session_state.request_history = [
        req_time for req_time in st.session_state.request_history
        if current_time - req_time < RATE_LIMIT_WINDOW_SECONDS
    ]
    
    # Check if rate limit exceeded
    if len(st.session_state.request_history) >= RATE_LIMIT_REQUESTS_PER_MINUTE:
        return False, f"Rate limit exceeded. Please wait {RATE_LIMIT_WINDOW_SECONDS} seconds before making another request."
    
    # Add current request
    st.session_state.request_history.append(current_time)
    return True, None

def export_conversation(system_prompt: str, user_prompt: str, response: str, metadata: Dict[str, Any]) -> str:
    """
    Export conversation to a formatted text string.
    
    Args:
        system_prompt: System prompt used
        user_prompt: User prompt
        response: AI response
        metadata: Response metadata
        
    Returns:
        Formatted conversation string
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    export_text = f"""AI Assistant Conversation Export
Generated: {timestamp}
{'='*50}

SYSTEM PROMPT:
{system_prompt if system_prompt else 'No system prompt provided'}

USER PROMPT:
{user_prompt}

AI RESPONSE:
{response}

METADATA:
- Model: {metadata.get('model', 'Unknown')}
- Temperature: {metadata.get('temperature', 'Unknown')}
- Response Time: {metadata.get('response_time', 'Unknown')} seconds
- Total Tokens: {metadata.get('total_tokens', 'Unknown')}
- Prompt Tokens: {metadata.get('prompt_tokens', 'Unknown')}
- Completion Tokens: {metadata.get('completion_tokens', 'Unknown')}
{'='*50}
"""
    return export_text
