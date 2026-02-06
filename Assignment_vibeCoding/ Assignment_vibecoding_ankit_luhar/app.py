"""
Production-ready Streamlit AI Assistant Application.
"""

import streamlit as st
import time
import logging
from typing import Dict, Any, Optional
from utils import (
    create_groq_client, validate_inputs, generate_response, format_response,
    calculate_metrics, get_model_info, check_rate_limit, export_conversation
)
from config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, DEFAULT_TEMPERATURE, DEFAULT_SYSTEM_PROMPT,
    MODEL_CONFIGS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for professional styling
def inject_custom_css():
    """Inject custom CSS for permanent dark mode theme."""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f9fafb;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #d1d5db;
        margin-bottom: 1rem;
    }
    
    .stTextArea textarea {
        font-size: 14px;
        line-height: 1.5;
        border-radius: 8px;
        background-color: #374151;
        color: #f9fafb;
        border-color: #4b5563;
    }
    
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .response-container {
        background-color: #1f2937;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #374151;
        color: #f9fafb;
        max-height: 400px;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: #4b5563 #1f2937;
    }
    
    .response-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .response-container::-webkit-scrollbar-track {
        background: #1f2937;
        border-radius: 4px;
    }
    
    .response-container::-webkit-scrollbar-thumb {
        background: #4b5563;
        border-radius: 4px;
    }
    
    .response-container::-webkit-scrollbar-thumb:hover {
        background: #6b7280;
    }
    
    .metric-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        color: #f9fafb;
    }
    
    .success-message {
        background-color: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .error-message {
        background-color: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .info-message {
        background-color: #3b82f6;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .stSelectbox > div > div {
        background-color: #374151;
        color: #f9fafb;
    }
    
    .stSlider > div > div > div {
        background-color: #4b5563;
    }
    
    .copy-button {
        background-color: #10b981;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .copy-button:hover {
        background-color: #059669;
        transform: translateY(-1px);
    }
    
    .copy-success {
        background-color: #059669;
        animation: fadeInOut 2s ease-in-out;
    }
    
    @keyframes fadeInOut {
        0% { opacity: 0; }
        20% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; }
    }
    
    /* Hide streamlit's default footer and menu */
    .stDeployButton {
        display: none;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #10b981;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 10px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_response' not in st.session_state:
        st.session_state.current_response = ""
    
    if 'current_metadata' not in st.session_state:
        st.session_state.current_metadata = {}
    
    if 'last_inputs' not in st.session_state:
        st.session_state.last_inputs = {
            'system_prompt': DEFAULT_SYSTEM_PROMPT,
            'user_prompt': '',
            'temperature': DEFAULT_TEMPERATURE,
            'model': list(MODEL_CONFIGS.keys())[0]
        }

def render_sidebar():
    """Render the sidebar with additional features."""
    with st.sidebar:
        st.markdown("### 🎛️ Advanced Settings")
        
        st.markdown("### 📊 Conversation History")
        if st.session_state.conversation_history:
            for i, conv in enumerate(st.session_state.conversation_history[-5:]):
                with st.expander(f"Conversation {i+1}"):
                    st.text_area("User:", conv['user_prompt'], height=100, disabled=True)
                    st.text_area("Response:", conv['response'][:200] + "..." if len(conv['response']) > 200 else conv['response'], height=100, disabled=True)
        else:
            st.info("No conversations yet")
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Lower temperature (0.0-0.5): More focused responses
        - Higher temperature (0.7-1.0): More creative responses
        - System prompt helps set AI behavior
        - Use clear, specific prompts for better results
        """)

def render_input_section():
    """Render the left column input section."""
    with st.container():
        st.markdown('<h2 class="section-header">📝 Input Configuration</h2>', unsafe_allow_html=True)
        
        # Temperature slider with tooltip
        temperature = st.slider(
            "🌡️ Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.last_inputs['temperature'],
            step=0.1,
            help="Controls randomness: Lower values make output more focused and deterministic, higher values make it more creative."
        )
        
        # Model selector
        model_options = list(MODEL_CONFIGS.keys())
        selected_model = st.selectbox(
            "🤖 AI Model",
            options=model_options,
            index=model_options.index(st.session_state.last_inputs['model']),
            help="Choose the AI model. Different models have different capabilities and token limits."
        )
        
        # Display model info
        model_info = get_model_info(selected_model)
        st.caption(f"ℹ️ {model_info['description']} (Max tokens: {model_info['max_tokens']})")
        
        # System Prompt text area
        system_prompt = st.text_area(
            "🎯 System Prompt",
            value=st.session_state.last_inputs['system_prompt'],
            height=180,
            help="Define the AI's role, personality, and behavior. This sets the context for all responses.",
            placeholder="You are a helpful assistant..."
        )
        
        # User Prompt text area (required)
        user_prompt = st.text_area(
            "💬 User Prompt",
            value=st.session_state.last_inputs['user_prompt'],
            height=180,
            help="Your question or request for the AI. This field is required.",
            placeholder="Ask me anything..."
        )
        
        # Word count for user prompt
        if user_prompt:
            word_count = len(user_prompt.split())
            char_count = len(user_prompt)
            st.caption(f"📊 {word_count} words, {char_count} characters")
        
        # Submit and Clear buttons
        col1, col2 = st.columns([2, 1])
        
        with col1:
            submit_button = st.button(
                "🚀 Generate Response",
                type="primary",
                use_container_width=True,
                help="Generate AI response (Ctrl+Enter)"
            )
        
        with col2:
            clear_button = st.button(
                "🗑️ Clear",
                type="secondary",
                use_container_width=True,
                help="Clear all inputs and outputs (Ctrl+L)"
            )
        
        # Handle clear button
        if clear_button:
            st.session_state.last_inputs = {
                'system_prompt': DEFAULT_SYSTEM_PROMPT,
                'user_prompt': '',
                'temperature': DEFAULT_TEMPERATURE,
                'model': model_options[0]
            }
            st.session_state.current_response = ""
            st.session_state.current_metadata = {}
            st.rerun()
        
        return {
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'temperature': temperature,
            'model': selected_model,
            'submit_button': submit_button
        }

def render_output_section():
    """Render the right column output section."""
    with st.container():
        st.markdown('<h2 class="section-header">💬 AI Response</h2>', unsafe_allow_html=True)
        
        if st.session_state.current_response:
            # Response container with improved copy button
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown('<div class="response-container">', unsafe_allow_html=True)
                    st.markdown(st.session_state.current_response)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Store response in a hidden component for JavaScript access
                    st.markdown(f"""
                    <textarea id="response-text" style="display: none;">{st.session_state.current_response}</textarea>
                    """, unsafe_allow_html=True)
                    
                    # More reliable JavaScript copy button
                    st.components.v1.html("""
                    <button class="copy-button" id="copy-btn" style="width: 100%; margin-bottom: 10px;">
                        📋 Copy Response
                    </button>
                    <div id="copy-status" style="color: #10b981; font-weight: 600; text-align: center; font-size: 0.9rem; height: 20px;"></div>
                    <script>
                    function initCopyButton() {
                        const copyBtn = document.getElementById('copy-btn');
                        const copyStatus = document.getElementById('copy-status');
                        
                        if (!copyBtn || !copyStatus) {
                            setTimeout(initCopyButton, 100);
                            return;
                        }
                        
                        copyBtn.onclick = function() {
                            // Get the response text from the hidden textarea
                            const responseText = document.getElementById('response-text');
                            const textToCopy = responseText ? responseText.value : '';
                            
                            if (!textToCopy) {
                                copyStatus.textContent = '❌ No text to copy';
                                copyBtn.style.backgroundColor = '#ef4444';
                                setTimeout(function() {
                                    copyStatus.textContent = '';
                                    copyBtn.style.backgroundColor = '#10b981';
                                }, 2000);
                                return;
                            }
                            
                            // Try modern clipboard API first
                            if (navigator.clipboard && window.isSecureContext) {
                                navigator.clipboard.writeText(textToCopy).then(function() {
                                    copyStatus.textContent = '✅ Copied!';
                                    copyBtn.style.backgroundColor = '#059669';
                                    setTimeout(function() {
                                        copyStatus.textContent = '';
                                        copyBtn.style.backgroundColor = '#10b981';
                                    }, 2000);
                                }).catch(function(err) {
                                    console.error('Clipboard API failed:', err);
                                    fallbackCopy(textToCopy);
                                });
                            } else {
                                fallbackCopy(textToCopy);
                            }
                        };
                        
                        function fallbackCopy(text) {
                            const textArea = document.createElement('textarea');
                            textArea.value = text;
                            textArea.style.position = 'fixed';
                            textArea.style.left = '-999999px';
                            textArea.style.top = '-999999px';
                            document.body.appendChild(textArea);
                            textArea.focus();
                            textArea.select();
                            
                            try {
                                const successful = document.execCommand('copy');
                                if (successful) {
                                    copyStatus.textContent = '✅ Copied!';
                                    copyBtn.style.backgroundColor = '#059669';
                                } else {
                                    throw new Error('execCommand failed');
                                }
                            } catch (err) {
                                console.error('Fallback copy failed:', err);
                                copyStatus.textContent = '❌ Copy failed';
                                copyBtn.style.backgroundColor = '#ef4444';
                            }
                            
                            setTimeout(function() {
                                copyStatus.textContent = '';
                                copyBtn.style.backgroundColor = '#10b981';
                            }, 2000);
                            
                            document.body.removeChild(textArea);
                        }
                    }
                    
                    // Initialize when DOM is ready
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', initCopyButton);
                    } else {
                        initCopyButton();
                    }
                    </script>
                    """, height=80)
            
            # Token usage metrics (collapsible)
            if st.session_state.current_metadata:
                with st.expander("📊 Token Usage & Metrics", expanded=False):
                    metrics = calculate_metrics(st.session_state.current_metadata)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("Response Time", f"{st.session_state.current_metadata.get('response_time', 0)}s")
                        st.metric("Tokens/Second", f"{metrics.get('tokens_per_second', 0)}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("Total Tokens", st.session_state.current_metadata.get('total_tokens', 0))
                        st.metric("Est. Cost", f"${metrics.get('cost_estimate', 0):.6f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.write(f"**Model:** {st.session_state.current_metadata.get('model', 'Unknown')}")
                    st.write(f"**Temperature:** {st.session_state.current_metadata.get('temperature', 'Unknown')}")
                    st.write(f"**Prompt Tokens:** {st.session_state.current_metadata.get('prompt_tokens', 0)}")
                    st.write(f"**Completion Tokens:** {st.session_state.current_metadata.get('completion_tokens', 0)}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Export options
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📄 Export as Text", help="Export conversation as text file"):
                    export_text = export_conversation(
                        st.session_state.last_inputs['system_prompt'],
                        st.session_state.last_inputs['user_prompt'],
                        st.session_state.current_response,
                        st.session_state.current_metadata
                    )
                    st.download_button(
                        label="💾 Download",
                        data=export_text,
                        file_name=f"ai_conversation_{int(time.time())}.txt",
                        mime="text/plain"
                    )
            
            with col2:
                if st.button("📜 Save to History", help="Save conversation to history"):
                    st.session_state.conversation_history.append({
                        'system_prompt': st.session_state.last_inputs['system_prompt'],
                        'user_prompt': st.session_state.last_inputs['user_prompt'],
                        'response': st.session_state.current_response,
                        'metadata': st.session_state.current_metadata,
                        'timestamp': time.time()
                    })
                    st.success("Conversation saved to history!")
        
        else:
            st.info("👈 Configure your inputs and click 'Generate Response' to see the AI's response here")

def handle_api_call(inputs: Dict[str, Any]):
    """Handle the API call when submit button is clicked."""
    # Validate inputs
    is_valid, error_message = validate_inputs(
        inputs['system_prompt'],
        inputs['user_prompt'],
        inputs['temperature']
    )
    
    if not is_valid:
        st.error(f"❌ {error_message}")
        return
    
    # Check rate limit
    rate_limit_ok, rate_limit_error = check_rate_limit()
    if not rate_limit_ok:
        st.error(f"⏱️ {rate_limit_error}")
        return
    
    # Create Groq client
    client = create_groq_client()
    if not client:
        st.error("❌ Failed to initialize AI client. Please check your API configuration.")
        return
    
    # Show loading state with custom animation
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem; background-color: #1f2937; border-radius: 12px; border: 1px solid #374151;">
            <div class="loading-spinner"></div>
            <span style="color: #f9fafb; font-size: 1.1rem; font-weight: 600;">🤖 Generating response...</span>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        # Generate response
        response, metadata, error = generate_response(
            client,
            inputs['system_prompt'],
            inputs['user_prompt'],
            inputs['model'],
            inputs['temperature']
        )
        
        # Clear loading indicator
        loading_placeholder.empty()
        
        if error:
            st.error(f"❌ {error}")
        else:
            # Format and store response
            formatted_response = format_response(response)
            st.session_state.current_response = formatted_response
            st.session_state.current_metadata = metadata or {}
            
            # Update last inputs
            st.session_state.last_inputs = {
                'system_prompt': inputs['system_prompt'],
                'user_prompt': inputs['user_prompt'],
                'temperature': inputs['temperature'],
                'model': inputs['model']
            }
            
            st.success("✅ Response generated successfully!")
            
    except Exception as e:
        # Clear loading indicator
        loading_placeholder.empty()
        logger.error(f"Unexpected error: {str(e)}")
        st.error("❌ An unexpected error occurred. Please try again.")

def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.markdown(f'<h1 class="main-header">{PAGE_ICON} {PAGE_TITLE}</h1>', unsafe_allow_html=True)
    
    # Create two equal columns
    left_col, right_col = st.columns([1, 1])
    
    # Render input section (left column)
    with left_col:
        inputs = render_input_section()
    
    # Handle API call if submit button clicked
    if inputs.get('submit_button'):
        handle_api_call(inputs)
    
    # Render output section (right column)
    with right_col:
        render_output_section()
    
    # Render sidebar
    render_sidebar()

if __name__ == "__main__":
    main()
