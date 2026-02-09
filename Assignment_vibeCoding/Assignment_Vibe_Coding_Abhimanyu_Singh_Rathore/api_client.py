"""
API client for handling Groq API calls
"""

import streamlit as st
from datetime import datetime
from groq import Groq
from config import Config
from custom_instructions import combine_instructions

class LLMClient:
    """Client for interacting with LLM APIs"""
    
    def __init__(self):
        """Initialize the LLM client"""
        try:
            Config.validate_api_key()
            self.client = Groq(api_key=Config.GROQ_API_KEY)
        except ValueError as e:
            st.error(f"Configuration error: {str(e)}")
            self.client = None
    
    def generate_response(self, system_prompt, user_prompt, model, temperature, max_tokens, 
                         instruction_category=None, custom_instructions="", use_context=True):
        """
        Generate response from LLM
        
        Args:
            system_prompt (str): System prompt for the AI
            user_prompt (str): User's question/request
            model (str): Model to use
            temperature (float): Temperature for response generation
            max_tokens (int): Maximum tokens in response
            instruction_category (str): Category of formatting instructions
            custom_instructions (str): Additional custom instructions
            use_context (bool): Whether to include conversation context
            
        Returns:
            dict: Interaction data with response and metadata
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        try:
            # Import here to avoid circular imports
            from utils import get_conversation_context
            
            # Combine system prompt with custom instructions
            category = instruction_category if instruction_category != "None" else None
            combined_system_prompt = combine_instructions(
                system_prompt, 
                category, 
                custom_instructions
            )
            
            # Prepare messages for the API
            messages = []
            
            # Add conversation context if enabled and history exists
            if use_context and 'history' in st.session_state and st.session_state.history:
                context_messages = get_conversation_context()
                messages.extend(context_messages)
            else:
                # Add combined system prompt if provided (new conversation)
                if combined_system_prompt.strip():
                    messages.append({"role": "system", "content": combined_system_prompt})
            
            # Add current user prompt
            messages.append({"role": "user", "content": user_prompt})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the response content
            response_content = response.choices[0].message.content
            
            # Create interaction record
            interaction = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'system_prompt': system_prompt,
                'instruction_category': instruction_category,
                'custom_instructions': custom_instructions,
                'user_prompt': user_prompt,
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'response': response_content
            }
            
            return interaction
            
        except Exception as e:
            raise Exception(f"Error calling LLM API: {str(e)}")
    
    def test_connection(self):
        """Test the API connection"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            # Make a simple API call to test connection
            response = self.client.chat.completions.create(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
