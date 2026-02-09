import streamlit as st
import requests
import json
import time
from datetime import datetime
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from prompt import PROMPT_ENHANCEMENTS

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Assistant - Groq Powered",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and styling
st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        background: rgba(255, 255, 255, 0.08);
        border-color: #ff6b35;
        box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
        background: linear-gradient(135deg, #ff8c42 0%, #ffa500 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(255, 107, 53, 0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stSelectbox select {
        background: rgba(255, 255, 255, 0.05);
        color: #ffffff;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #ff6b35 0%, #ff8c42 100%);
    }
    
    /* Output container */
    .output-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(5px);
    }
    
    /* History item */
    .history-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .history-item:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 107, 53, 0.5);
    }
    
    /* Metrics footer */
    .metrics-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 8px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
        z-index: 999;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top: 3px solid #ff6b35;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_response' not in st.session_state:
    st.session_state.current_response = ""
if 'api_key' not in st.session_state:
    # Try to get API key from environment first, then session state
    env_api_key = os.getenv('GROQ_API_KEY', '')
    st.session_state.api_key = env_api_key

# Groq API configuration
GROQ_MODELS = {
    "llama-3.3-70b-versatile": "LLaMA 3.3 70B Versatile"
}

# Temperature presets for different modes
TEMPERATURE_PRESETS = {
    "General": 0.7,
    "Coding": 0.1,
    "Research": 0.3,
    "Web Article": 0.5,
    "Interview": 0.4
}

def call_groq_api(system_prompt: str, user_prompt: str, temperature: float, model: str) -> Optional[str]:
    """Call Groq API to generate response"""
    api_key = st.session_state.get('api_key', '')
    if not api_key:
        return "⚠️ Please enter your Groq API key in the sidebar."
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 4000
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"❌ API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def save_to_history(system_prompt: str, user_prompt: str, response: str, mode: str, temperature: float):
    """Save conversation to history"""
    history_item = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "response": response,
        "mode": mode,
        "temperature": temperature
    }
    st.session_state.history.insert(0, history_item)  # Add to beginning
    
    # Keep only last 50 items
    if len(st.session_state.history) > 50:
        st.session_state.history = st.session_state.history[:50]

# Sidebar
with st.sidebar:
    # API key from environment
    env_api_key = os.getenv('GROQ_API_KEY', '')
    if env_api_key:
        st.session_state.api_key = env_api_key
    else:
        st.error("❌ No API key found in .env file")
        api_key = st.text_input(
            "🔑 Groq API Key",
            type="password",
            placeholder="Enter your Groq API key...",
            help="Or add GROQ_API_KEY to your .env file"
        )
        if api_key:
            st.session_state.api_key = api_key
    
    st.markdown("### 📜 Conversation History")
    
    # Clear history button
    if st.button("🗑️ Clear History", key="clear_history"):
        st.session_state.history = []
        st.rerun()
    
    # Display history
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history[:10]):  # Show last 10
            with st.expander(f"🕐 {item['timestamp']} - {item['mode']}", expanded=False):
                st.write(f"**Mode:** {item['mode']}")
                st.write(f"**Temperature:** {item['temperature']}")
                st.write(f"**System:** {item['system_prompt'][:100]}...")
                st.write(f"**User:** {item['user_prompt'][:100]}...")
                st.write(f"**Response:** {item['response'][:200]}...")
                
                if st.button(f"📋 Load #{i+1}", key=f"load_{i}"):
                    st.session_state.system_prompt = item['system_prompt']
                    st.session_state.user_prompt = item['user_prompt']
                    st.session_state.output_mode = item['mode']
                    st.session_state.temperature = item['temperature']
                    st.rerun()
    else:
        st.write("No history yet. Start a conversation!")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🎯 Input Configuration")
    
    # Output mode selector
    output_mode = st.selectbox(
        "📝 Output Mode",
        options=["General", "Coding", "Research", "Web Article", "Interview"],
        index=0,
        help="Select the type of response you want. Temperature will auto-adjust."
    )
    
    # Auto-adjust temperature based on mode
    if 'output_mode' not in st.session_state or st.session_state.output_mode != output_mode:
        st.session_state.temperature = TEMPERATURE_PRESETS[output_mode]
        st.session_state.output_mode = output_mode
    
    # System prompt
    system_prompt = st.text_area(
        "🤖 System Prompt",
        placeholder="Enter the system prompt (e.g., 'You are a helpful AI assistant...')",
        height=100,
        value=st.session_state.get('system_prompt', '')
    )
    
    # User prompt
    user_prompt = st.text_area(
        "💬 User Prompt",
        placeholder="Enter your question or request here...",
        height=150,
        value=st.session_state.get('user_prompt', '')
    )
    
    # Temperature slider
    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls randomness: 0 = deterministic, 1 = creative"
    )
    
    # Generate button
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    with generate_col2:
        if st.button("🚀 Generate Response", key="generate", use_container_width=True):
            if not system_prompt or not user_prompt:
                st.error("⚠️ Please fill in both system and user prompts!")
            elif not st.session_state.api_key:
                st.error("⚠️ Please enter your Groq API key!")
            else:
                with st.spinner("🤔 Thinking..."):
                    start_time = time.time()
                    # Append enhancement instructions to system prompt
                    enhanced_system_prompt = f"{system_prompt}\n\nFormatting instructions: {PROMPT_ENHANCEMENTS[output_mode]}"
                    response = call_groq_api(enhanced_system_prompt, user_prompt, temperature, "llama-3.3-70b-versatile")
                    end_time = time.time()
                    
                    st.session_state.current_response = response
                    st.session_state.response_time = end_time - start_time
                    
                    # Save to history
                    save_to_history(system_prompt, user_prompt, response, output_mode, temperature)
                    
                    # Rerun to update the output
                    st.rerun()

with col2:
    st.markdown("### 📤 Response")
    
    # Output container
    if st.session_state.current_response:
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        st.write(st.session_state.current_response)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Copy button
        if st.button("📋 Copy Response", key="copy_response"):
            st.write("Response copied to clipboard!")
    else:
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        st.write("🤖 Your AI response will appear here...")
        st.markdown('</div>', unsafe_allow_html=True)

# Metrics footer
st.markdown("---")
metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)

with metrics_col1:
    st.metric("📊 History", len(st.session_state.history))

with metrics_col2:
    if hasattr(st.session_state, 'response_time'):
        st.metric("⚡ Response Time", f"{st.session_state.response_time:.2f}s")

with metrics_col3:
    st.metric("🌡️ Temperature", temperature)

with metrics_col4:
    st.metric("🎯 Mode", output_mode)

with metrics_col5:
    st.metric("🤖 Model", "LLaMA 3.3")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 20px; color: rgba(255, 255, 255, 0.5); font-size: 12px;">
    Made with ❤️ using Streamlit & Groq API
</div>
""", unsafe_allow_html=True)
