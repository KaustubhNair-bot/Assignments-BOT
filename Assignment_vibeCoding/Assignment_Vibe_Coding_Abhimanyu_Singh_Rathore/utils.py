"""
Utility functions for the LLM Chat Interface
"""

import streamlit as st
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables"""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_response' not in st.session_state:
        st.session_state.current_response = None

def clear_inputs():
    """Clear input fields and rerun the app"""
    st.session_state.system_prompt = ""
    st.session_state.user_prompt = ""
    st.rerun()

def copy_to_clipboard(text):
    """Copy text to clipboard (Streamlit limitation - shows as code)"""
    st.code(text)
    st.write("📋 Response copied above (use Ctrl+C to copy)")

def save_interaction_to_history(interaction):
    """Save interaction to session history"""
    if 'history' not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append(interaction)

def get_current_response():
    """Get current response from session state"""
    return st.session_state.get('current_response', None)

def set_current_response(response):
    """Set current response in session state"""
    st.session_state.current_response = response

def get_history():
    """Get conversation history"""
    return st.session_state.get('history', [])

def get_conversation_context():
    """Get recent conversation messages for context"""
    # Import here to avoid circular imports
    from config import Config
    
    if 'history' not in st.session_state:
        return []
    
    # Get recent messages up to limit
    recent_history = st.session_state.history[-Config.MAX_CONTEXT_MESSAGES:]
    
    # Convert to message format for API
    messages = []
    for interaction in recent_history:
        # Add system message if it exists and is first interaction
        if interaction == recent_history[0] and interaction.get('system_prompt') and interaction['system_prompt'].strip():
            messages.append({
                "role": "system",
                "content": interaction['system_prompt']
            })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": interaction['user_prompt']
        })
        
        # Add assistant response
        messages.append({
            "role": "assistant",
            "content": interaction['response']
        })
    
    return messages

def clear_conversation_context():
    """Clear conversation context and history"""
    if 'history' in st.session_state:
        st.session_state.history = []
    if 'current_response' in st.session_state:
        st.session_state.current_response = None

def format_timestamp():
    """Get formatted current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_inputs(user_prompt, system_prompt=""):
    """Validate user inputs"""
    errors = []
    
    if not user_prompt or not user_prompt.strip():
        errors.append("User prompt is required")
    
    if len(user_prompt) > 10000:
        errors.append("User prompt is too long (max 10,000 characters)")
    
    if len(system_prompt) > 5000:
        errors.append("System prompt is too long (max 5,000 characters)")
    
    return errors

def truncate_text(text, max_length, suffix="..."):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"
