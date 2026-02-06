import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from prompt import get_structured_prompt, combine_prompts

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Groq Chat App",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Groq Chat App")
st.markdown("Interact with Groq API using custom system prompts, user prompts, and temperature settings.")

# Initialize session state for conversation history and sidebar control
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = False

# Check for API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

# Main content area for inputs
st.header("Input Configuration")

# Conversation controls
col_clear, col_history = st.columns([1, 2])
with col_clear:
    if st.button("🗑️ Clear History", help="Clear all conversation history"):
        st.session_state.conversation_history = []
        if "response" in st.session_state:
            del st.session_state.response
        if "usage_info" in st.session_state:
            del st.session_state.usage_info
        st.session_state.sidebar_expanded = False
        st.success("Conversation history cleared!")
        st.rerun()

with col_history:
    if st.session_state.conversation_history:
        st.info(f"📚 Conversation has {len(st.session_state.conversation_history)} exchanges")

# Two column layout for prompts
col1, col2 = st.columns(2)

with col1:
    # System prompt input
    system_prompt = st.text_area(
        "System Prompt:",
        value="You are a helpful assistant.",
        height=200,
        help="This sets the behavior and context for the AI assistant."
    )

with col2:
    # User prompt input
    user_prompt = st.text_area(
        "User Prompt:",
        value="Hello! How are you?",
        height=200,
        help="This is your actual question or request to the AI."
    )

# Temperature slider
temperature = st.slider(
    "Temperature:",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1,
    help="Controls randomness: Lower values make responses more focused, higher values more creative."
)

# Context retention options
st.subheader("Context Settings")
context_enabled = st.checkbox("🧠 Enable Context Retention", value=True, help="Include previous conversation history for better contextual responses")

# Show context summary if enabled
if context_enabled and st.session_state.conversation_history:
    with st.expander("📖 Conversation Context Preview"):
        for i, exchange in enumerate(st.session_state.conversation_history[-3:], 1):  # Show last 3 exchanges
            st.markdown(f"**Exchange {i}:**")
            st.markdown(f"*User:* {exchange['user'][:100]}...")
            st.markdown(f"*Assistant:* {exchange['assistant'][:100]}...")
            st.markdown("---")

# Response format selection
st.subheader("Response Format")
response_format = st.selectbox(
    "Choose response format:",
    options=["general", "steps", "comparison", "code", "data", "troubleshoot", "educational"],
    format_func=lambda x: {
        "general": "📝 General (Basic formatting)",
        "steps": "📋 Step-by-Step Guide",
        "comparison": "⚖️ Comparison Analysis",
        "code": "💻 Code Solution",
        "data": "📊 Data Analysis",
        "troubleshoot": "🔧 Troubleshooting Guide",
        "educational": "📚 Educational Content"
    }.get(x, x),
    help="Select how you want the response to be structured"
)

# Show format preview
format_descriptions = {
    "general": "Basic structured formatting with headings and bullet points",
    "steps": "Step-by-step instructions with prerequisites and tips",
    "comparison": "Detailed comparison with tables and recommendations",
    "code": "Code solutions with explanations and examples",
    "data": "Data analysis with insights and visualizations",
    "troubleshoot": "Problem diagnosis with solutions and prevention",
    "educational": "Learning content with objectives and key takeaways"
}

st.info(f"**Format:** {format_descriptions[response_format]}")

# Generate button
if st.button("Generate Response", type="primary"):
    if not user_prompt.strip():
        st.error("Please enter a user prompt!")
    else:
        try:
            with st.spinner("Generating response..."):
                # Initialize Groq client
                try:
                    client = Groq(api_key=api_key)
                except Exception as init_error:
                    st.error(f"Failed to initialize Groq client: {str(init_error)}")
                    st.info("Please try updating the groq package: pip install --upgrade groq")
                    st.stop()
                
                # Get structured instruction based on selected format
                structured_instruction = get_structured_prompt(response_format)
                
                # Combine system prompt with structured instruction
                enhanced_system_prompt = f"{system_prompt}\n\n{structured_instruction}"
                
                # Build conversation messages
                messages = [{"role": "system", "content": enhanced_system_prompt}]
                
                # Add conversation history if context is enabled
                if context_enabled and st.session_state.conversation_history:
                    for exchange in st.session_state.conversation_history:
                        messages.append({"role": "user", "content": exchange["user"]})
                        messages.append({"role": "assistant", "content": exchange["assistant"]})
                
                # Add current user prompt
                messages.append({"role": "user", "content": user_prompt})
                
                # Create the chat completion with default model
                try:
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model="llama-3.3-70b-versatile",  # Default model
                        temperature=temperature,
                        max_tokens=1024
                    )
                except Exception as api_error:
                    st.error(f"API call failed: {str(api_error)}")
                    st.info("Please check your API key and internet connection.")
                    st.stop()
                
                # Store response in session state for sidebar display
                response = chat_completion.choices[0].message.content
                st.session_state.response = response
                st.session_state.usage_info = {
                    "Model": "llama-3.3-70b-versatile",
                    "Temperature": temperature,
                    "Format": response_format,
                    "Context Enabled": context_enabled,
                    "History Length": len(st.session_state.conversation_history),
                    "Tokens Used": chat_completion.usage.total_tokens if chat_completion.usage else "N/A",
                    "Prompt Tokens": chat_completion.usage.prompt_tokens if chat_completion.usage else "N/A",
                    "Completion Tokens": chat_completion.usage.completion_tokens if chat_completion.usage else "N/A"
                }
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "user": user_prompt,
                    "assistant": response
                })
                
                # Limit history to last 10 exchanges to prevent token overflow
                if len(st.session_state.conversation_history) > 10:
                    st.session_state.conversation_history = st.session_state.conversation_history[-10:]
                
                # Set sidebar to expanded state
                st.session_state.sidebar_expanded = True
                
                st.success("Response generated! Check the sidebar for the output.")
                st.rerun()
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your API key and internet connection.")

# Sidebar for output
with st.sidebar:
    st.header("📝 AI Response")
    
    # Auto-expand sidebar when response is generated
    if st.session_state.sidebar_expanded and "response" in st.session_state:
        # Reset the flag after expanding
        st.session_state.sidebar_expanded = False
        
        # Show success message and highlight the response
        st.success("🎉 New response available!")
        st.markdown("---")
    
    if "response" in st.session_state:
        st.write(st.session_state.response)
        
        with st.expander("📊 Response Details", expanded=True):
            st.json(st.session_state.usage_info)
            
        # Show conversation history
        if st.session_state.conversation_history:
            st.markdown("---")
            st.subheader("💬 Conversation History")
            
            for i, exchange in enumerate(reversed(st.session_state.conversation_history[-5:]), 1):  # Show last 5 exchanges
                with st.expander(f"Exchange {len(st.session_state.conversation_history) - i + 1}"):
                    st.markdown("**👤 User:**")
                    st.write(exchange["user"])
                    st.markdown("**🤖 Assistant:**")
                    st.write(exchange["assistant"])
    else:
        st.info("No response yet. Generate a response to see the output here.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Adjust the temperature to control response creativity - lower for factual answers, higher for creative content.")
