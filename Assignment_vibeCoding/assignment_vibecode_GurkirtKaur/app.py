import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
def get_groq_client():
    """
    Initialize and return Groq client with API key from Streamlit secrets.
    
    Security: API key is loaded from st.secrets for secure management.
    Falls back to environment variables for local development.
    """
    # Try to get API key from Streamlit secrets first (recommended for production)
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fallback to environment variables for local development
        api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("GROQ_API_KEY not found. Please set it in .streamlit/secrets.toml or .env file.")
        return None
    return Groq(api_key=api_key)

# Initialize session state for chat history
def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = ""
    if 'user_prompt_value' not in st.session_state:
        st.session_state.user_prompt_value = ""
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7

# Send prompts to Groq API and get response
def get_llm_response(system_prompt, user_prompt, temperature):
    """
    Send system and user prompts to Groq API and return the response.
    
    Args:
        system_prompt (str): The system prompt to set context
        user_prompt (str): The user's input prompt
        temperature (float): Temperature for response generation (0.0-2.0)
    
    Returns:
        str: The model's response or error message
    """
    client = get_groq_client()
    if not client:
        return "Error: Unable to initialize Groq client. Please check your API key."
    
    try:
        # Create chat completion with Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            model="llama-3.1-8b-instant",  # Using Llama 3.1 8B Instant model for good performance
            temperature=temperature,
            max_tokens=1024
        )
        
        # Extract and return the response content
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        return f"Error communicating with Groq API: {str(e)}"

# Handle the Send button click
def handle_send_click():
    """Handle the Send button click event."""
    system_prompt = st.session_state.system_prompt
    user_prompt = st.session_state.user_prompt_value
    temperature = st.session_state.temperature
    
    # Validate inputs
    if not system_prompt.strip() and not user_prompt.strip():
        st.warning("Please enter at least a system prompt or user prompt before sending.")
        return
    
    if not user_prompt.strip():
        st.warning("Please enter a user prompt before sending.")
        return
    
    # Get LLM response
    with st.spinner("Generating response..."):
        response = get_llm_response(system_prompt, user_prompt, temperature)
    
    # Add to chat history
    st.session_state.chat_history.insert(0, {
        "system": system_prompt,
        "user": user_prompt,
        "response": response
    })
    
    # Clear user prompt by updating session state before next rerun
    st.session_state.user_prompt_value = ""

# Display chat history
def display_chat_history():
    """Display the chat history in the output panel."""
    if not st.session_state.chat_history:
        st.info("No conversation history yet. Send your first message to get started!")
        return
    
    for i, chat in enumerate(st.session_state.chat_history):
        # Display system prompt if it exists
        if chat["system"].strip():
            with st.expander(f"System Prompt", expanded=False):
                st.text(chat["system"])
        
        # Display user prompt
        st.write(f"**User {i+1}:**")
        st.text(chat["user"])
        
        # Display model response
        st.write(f"**Assistant:**")
        st.markdown(f"{chat['response']}")
        
        st.divider()

# Main application
def main():
    """Main Streamlit application function."""
    st.set_page_config(
        page_title="LLM Chat Interface",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("🤖 LLM Chat Interface")
    st.markdown("Your one-stop application to interact with Groq's language models using custom system and user prompts to answer your queries.")
    
    # Initialize session state
    initialize_session_state()
    
    # Create main layout with columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Inputs Panel")
        
        # System Prompt text area
        st.text_area(
            "System Prompt",
            placeholder="Enter the system prompt to set the context for the AI assistant...",
            key="system_prompt",
            height=150,
            help="The system prompt sets the behavior and context for the AI assistant."
        )
        
        # User Prompt text area
        user_input = st.text_area(
            "User Prompt",
            placeholder="Enter your message or question here...",
            value=st.session_state.user_prompt_value,
            key="user_input_widget",
            height=150,
            help="This is your actual input to the AI assistant."
        )
        
        # Update session state when user types
        if user_input != st.session_state.user_prompt_value:
            st.session_state.user_prompt_value = user_input
        
        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Controls randomness in responses. Lower values = more focused, Higher values = more creative."
        )
        
        # Update session state when slider changes
        if temperature != st.session_state.temperature:
            st.session_state.temperature = temperature
        
        # Send button
        send_button = st.button(
            "Submit",
            type="primary",
            use_container_width=True,
            help="Click to send your prompts to the AI model"
        )
        
        # Handle button click
        if send_button:
            handle_send_click()
    
    with col2:
        st.subheader("Response Panel")
        
        # Display chat history
        display_chat_history()
    
    # Add footer with instructions
    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Enter a system prompt to define the AI's behavior (optional)
    2. Enter your user prompt/question
    3. Click "Send" to get the AI response
    4. View the conversation history in the response panel
    """)

# Run the application
if __name__ == "__main__":
    main()
