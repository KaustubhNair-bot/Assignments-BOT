"""
Prompt Engineering Playground - Streamlit Frontend

A clean, interactive interface for experimenting with LLM prompts using the Groq API.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from backend.llm_handler import generate_response, get_available_models


st.set_page_config(
    page_title="Prompt Engineering Playground",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTextArea textarea {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧪 Prompt Engineering Playground")

st.markdown(
    """
    Experiment with **system prompts**, **user prompts**, and **temperature settings** 
    to understand how LLMs respond to different inputs. Powered by Groq's fast inference API.
    """
)

st.divider()

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📝 Inputs")
    
    system_prompt = st.text_area(
        label="System Prompt",
        height=150,
        placeholder="You are a helpful assistant that explains complex topics in simple terms...",
        help="Optional context or persona for the AI. This is combined with the app's base instructions.",
    )
    
    user_prompt = st.text_area(
        label="User Prompt",
        height=150,
        placeholder="Explain quantum entanglement in simple terms",
        help="Your question or task for the AI.",
    )
    
    st.markdown("##### ⚙️ Settings")
    
    settings_col1, settings_col2 = st.columns([2, 1])
    
    with settings_col1:
        temperature = st.slider(
            label="Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Lower = more focused and deterministic. Higher = more creative and varied.",
        )
    
    with settings_col2:
        model = st.selectbox(
            label="Model",
            options=get_available_models(),
            index=0,
            help="Select the Groq model to use.",
        )
    
    st.markdown("")
    
    generate_button = st.button(
        "🚀 Generate Response",
        type="primary",
        use_container_width=True,
    )

with col_right:
    st.subheader("💬 Response")
    
    response_container = st.container()
    
    with response_container:
        if generate_button:
            if not user_prompt.strip():
                st.warning("Please enter a user prompt to generate a response.")
            else:
                with st.spinner("Generating response..."):
                    result = generate_response(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=temperature,
                        model=model,
                    )
                
                if result.startswith("⚠️"):
                    st.error(result)
                else:
                    st.markdown(result)
        else:
            st.markdown(
                """
                <div style="
                    border: 1px dashed #555;
                    border-radius: 8px;
                    padding: 2rem;
                    text-align: center;
                    color: #888;
                    min-height: 200px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    Enter your prompts and click <strong>Generate Response</strong> to see the output here.
                </div>
                """,
                unsafe_allow_html=True,
            )

st.divider()

with st.expander("ℹ️ How This Works"):
    st.markdown(
        """
        **Prompt Layering Architecture**
        
        This application uses a three-layer prompt system:
        
        1. **Developer Instructions** (fixed) — Core behavior rules, safety guidelines, and output formatting 
           that always apply. Defined in `backend/prompt.py`.
        2. **Your System Prompt** — Additional context or persona you provide above.
        3. **Your User Prompt** — The actual question or task.
        
        This mirrors how production LLM applications separate developer intent from user input.
        
        ---
        
        **Temperature Guide**
        - `0.0 - 0.3`: Very focused, deterministic responses
        - `0.4 - 0.7`: Balanced creativity and consistency
        - `0.8 - 1.2`: More creative and varied
        - `1.3 - 2.0`: Highly creative, may be less coherent
        """
    )
