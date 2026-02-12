
from __future__ import annotations

import hashlib
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import requests
import streamlit as st

from frontend.components.chat_widget import render_chat
from frontend.components.sidebar import render_sidebar


st.set_page_config(
    page_title="DP World Assistant",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)


MOCK_USERS = {
    "admin": hashlib.sha256("dpworld2026".encode()).hexdigest(),
    "analyst": hashlib.sha256("logistics123".encode()).hexdigest(),
    "demo": hashlib.sha256("demo123".encode()).hexdigest(),
}



def load_css() -> None:
    """Load custom CSS styles."""
    try:
        with open("frontend/assets/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass



def render_login() -> bool:
    """
    Render a mock login page. Returns True if authenticated.
    
    Credentials (displayed on the login page for demo purposes):
    - admin / dpworld2026
    - analyst / logistics123  
    - demo / demo123
    """
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 1rem;">
        <h1 style="
            background: linear-gradient(135deg, #0066CC 0%, #00AAFF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
        ">🚢 DP World Assistant</h1>
        <p style="color: #888; font-size: 1.1rem; margin-top: 0.5rem;">
            AI-Powered Logistics Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1d23 0%, #262a33 100%);
            border: 1px solid #2a2e37;
            border-radius: 16px;
            padding: 2rem;
            margin: 1rem 0;
        ">
            <h3 style="text-align: center; color: #E6E9EF; margin-bottom: 1rem;">
                🔐 Secure Login
            </h3>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        if st.button("🔓 Sign In", use_container_width=True, type="primary"):
            if username in MOCK_USERS:
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                if MOCK_USERS[username] == pwd_hash:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
            else:
                st.error("❌ User not found")


        st.markdown("---")
        st.markdown("""
        <div style="
            background: rgba(0, 102, 204, 0.1);
            border: 1px solid rgba(0, 102, 204, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 0.5rem;
        ">
            <p style="color: #00AAFF; font-weight: 600; margin-bottom: 0.5rem;">
                📋 Demo Credentials
            </p>
            <table style="width: 100%; color: #ccc; font-size: 0.85rem;">
                <tr><td><code>admin</code></td><td><code>dpworld2026</code></td><td>Full access</td></tr>
                <tr><td><code>analyst</code></td><td><code>logistics123</code></td><td>Analyst role</td></tr>
                <tr><td><code>demo</code></td><td><code>demo123</code></td><td>Read-only demo</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    return False


def main() -> None:
    """Main Streamlit application."""
    load_css()


    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = "http://localhost:8000"
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.3
    if "top_p" not in st.session_state:
        st.session_state.top_p = 0.7
    if "show_chunks" not in st.session_state:
        st.session_state.show_chunks = True
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


    if not st.session_state.authenticated:
        render_login()
        return


    render_sidebar()


    render_chat()


if __name__ == "__main__":
    main()
