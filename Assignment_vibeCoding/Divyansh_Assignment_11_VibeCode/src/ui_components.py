import streamlit as st

def render_ui():
    """
    Final professional UI with Role Selection, Model Selection, and Newest-First History.
    """
    st.markdown(
        """
    <style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem !important; margin-top: -1.5rem !important; }
    .stApp { background-color: #0E1117; }
    .main-header {
        font-size: 2.2rem; font-weight: 800; text-align: center; margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #1a1f2e !important; color: #ffffff !important;
        border: 1px solid #2d3748 !important; border-radius: 8px !important;
    }
    .stTextArea label, .stSelectbox label { color: #667eea !important; font-weight: 700 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: #111827 !important; border-radius: 12px !important; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<h1 class="main-header">VibeCode AI Dashboard</h1>', unsafe_allow_html=True)

    # Data Mappings
    roles = ["Interviewer", "Teacher", "Coder", "Storyteller", "Analyst"]
    temp_options = {"Precise (0.1)": 0.1, "Focused (0.35)": 0.35, "Balanced (0.4)": 0.4, "Creative (0.7)": 0.7, "Innovative (0.9)": 0.9}
    model_options = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    col1, col2 = st.columns([1.2, 2.0], gap="large")

    with col1:
        with st.container(border=True):
            user_task = st.text_area(label="🎯 USER TASK", value="Explain how a car engine works.", height=120)
            system_behavior = st.text_area(label="🤖 SYSTEM BEHAVIOR (CUSTOM)", value="Be very detailed.", height=100)
            
            # THE NEW ROLE SELECTOR
            selected_role = st.selectbox(label="👤 SELECT AI ROLE", options=roles, index=1)
            
            model_name = st.selectbox(label="🧠 SELECT MODEL", options=model_options)
            temp_label = st.selectbox(label="🌡️ TEMPERATURE", options=list(temp_options.keys()), index=2)
            temperature_value = temp_options[temp_label]

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                button_clicked = st.button("🚀 GENERATE", use_container_width=True, type="primary")
            with btn_col2:
                clear_clicked = st.button("🗑️ CLEAR CHAT", use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("### ✨ CONVERSATION HISTORY")
            chat_container = st.container(height=490)
            with chat_container:
                if "chat_history" in st.session_state and st.session_state.chat_history:
                    for chat in reversed(st.session_state.chat_history):
                        # User Block
                        st.markdown(f'''<div style="background-color: #2d3748; padding: 12px; border-radius: 10px; border-left: 5px solid #667eea; margin-bottom: 5px;">
                            <b style="color: #667eea;">👤 TASK ({chat['role']}):</b><br>{chat['user']}</div>''', unsafe_allow_html=True)
                        # AI Block
                        st.markdown(f'''<div style="background-color: #1a2634; padding: 15px; border-radius: 10px; border-left: 5px solid #764ba2; margin-bottom: 5px;">
                            <b style="color: #a78bfa;">🤖 AI RESPONSE:</b><br>{chat['bot']}</div>''', unsafe_allow_html=True)
                        # Stats
                        st.markdown(f'''<div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 30px; padding-left: 10px;">
                            📏 {chat['word_count']} words | Model: {chat['model']}</div>''', unsafe_allow_html=True)
                        st.markdown("<hr style='border: 0.1px solid #374151; margin: 10px 0;'>", unsafe_allow_html=True)
                else:
                    st.info("Pick a role and click 'Generate'!")

    return user_task, system_behavior, temperature_value, model_name, selected_role, button_clicked, clear_clicked