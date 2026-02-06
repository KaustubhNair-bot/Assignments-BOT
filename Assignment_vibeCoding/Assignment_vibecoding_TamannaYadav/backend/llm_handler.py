"""
LLM Handler module for the Prompt Engineering Playground.

This module handles all interactions with the Groq API, including
building the final prompt structure and managing API calls.
"""

import os
from groq import Groq

from backend.prompt import build_full_system_prompt


DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_groq_client() -> Groq:
    """
    Creates and returns a Groq client using the API key from environment variables.
    
    Raises:
        ValueError: If GROQ_API_KEY is not set in environment.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    
    return Groq(api_key=api_key)


def generate_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    model: str = DEFAULT_MODEL
) -> str:
    """
    Generates a response from the Groq LLM.
    
    The final prompt is constructed as:
    1. Fixed developer instructions (from prompt.py)
    2. User-provided system prompt
    3. User message
    
    Args:
        system_prompt: User-provided system context from the UI.
        user_prompt: The user's message/question.
        temperature: Sampling temperature (0.0 to 2.0).
        model: The Groq model to use.
        
    Returns:
        The LLM's response text, or an error message if something fails.
    """
    try:
        client = get_groq_client()
        
        full_system_prompt = build_full_system_prompt(system_prompt)
        
        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        chat_completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4096,
        )
        
        return chat_completion.choices[0].message.content
        
    except ValueError as e:
        return f"⚠️ Configuration Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


def get_available_models() -> list[str]:
    """
    Returns a list of recommended Groq models for the playground.
    """
    return [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
