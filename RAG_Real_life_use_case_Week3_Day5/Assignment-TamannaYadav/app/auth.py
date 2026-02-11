"""
Authentication Module for Tesla RAG Streamlit App.
Provides mock authentication for demo purposes.
"""

import streamlit as st
from typing import Tuple, Optional
import hashlib


# Hardcoded credentials for demo
VALID_CREDENTIALS = {
    "tesla_admin": "tesla123",
    "demo_user": "demo123"
}


def hash_password(password: str) -> str:
    """Hash password for comparison."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username: str, password: str) -> bool:
    """
    Verify user credentials.
    
    Args:
        username: Username to verify
        password: Password to verify
        
    Returns:
        True if credentials are valid
    """
    if username in VALID_CREDENTIALS:
        return VALID_CREDENTIALS[username] == password
    return False


def init_session_state():
    """Initialize authentication session state."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0


def login_user(username: str) -> None:
    """Set user as logged in."""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.login_attempts = 0


def logout_user() -> None:
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = None
    if 'chat_history' in st.session_state:
        st.session_state.chat_history = []


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[str]:
    """Get current logged in username."""
    return st.session_state.get('username', None)


def render_login_page() -> bool:
    """
    Render the login page.
    
    Returns:
        True if login successful, False otherwise
    """
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }
    .tesla-logo {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        color: #e82127;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="tesla-logo">TESLA</div>', unsafe_allow_html=True)
        st.markdown("### Knowledge Assistant Login")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password.")
                    return False
                
                if verify_credentials(username, password):
                    login_user(username)
                    st.success("Login successful!")
                    st.rerun()
                    return True
                else:
                    st.session_state.login_attempts += 1
                    if st.session_state.login_attempts >= 3:
                        st.error("Too many failed attempts. Please try again later.")
                    else:
                        st.error("Invalid credentials. Please try again.")
                    return False
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
        Demo Credentials:<br>
        Username: <code>tesla_admin</code><br>
        Password: <code>tesla123</code>
        </div>
        """, unsafe_allow_html=True)
    
    return False


def render_logout_button() -> None:
    """Render logout button in sidebar."""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.rerun()
