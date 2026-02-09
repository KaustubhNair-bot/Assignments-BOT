import streamlit as st
import os
from src.ui_components import render_ui
from src.llm_logic import get_groq_response

def main():
    st.set_page_config(page_title="VibeCode AI Dashboard", page_icon="🤖", layout="wide")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Get UI inputs
    user_task, sys_bh, temp_v, model_n, role_n, gen_btn, clear_btn = render_ui()

    if clear_btn:
        st.session_state.chat_history = []
        st.rerun()

    if gen_btn:
        if not user_task.strip():
            st.warning("Please enter a task.")
        else:
            with st.spinner(f"🤖 AI {role_n} is thinking..."):
                # Pass the role into the behavior
                full_behavior = f"Current Role: {role_n}\nAdditional Instructions: {sys_bh}"
                ans, count = get_groq_response(user_task, full_behavior, temp_v, model_n)
                
                st.session_state.chat_history.append({
                    'user': user_task, 'bot': ans, 'word_count': count, 'model': model_n, 'role': role_n
                })
                st.rerun()

if __name__ == "__main__":
    main()