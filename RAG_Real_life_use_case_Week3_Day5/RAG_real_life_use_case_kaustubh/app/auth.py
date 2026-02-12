"""
Mock Authentication Module for Airtel RAG Customer Support Chatbot.
Provides a simple username/password login gate before accessing the RAG engine.
"""

import streamlit as st
import hashlib

# ---------- Mock User Database ----------
# In production, this would be a real database with hashed passwords.
MOCK_USERS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "Admin User",
        "role": "Administrator",
    },
    "agent": {
        "password_hash": hashlib.sha256("agent123".encode()).hexdigest(),
        "name": "Airtel Support Agent",
        "role": "Customer Support",
    },
    "demo": {
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "name": "Demo User",
        "role": "Viewer",
    },
}


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password against the mock database."""
    if username in MOCK_USERS:
        return MOCK_USERS[username]["password_hash"] == _hash_password(password)
    return False


def get_user_info(username: str) -> dict:
    """Return user metadata (name, role) for a valid username."""
    if username in MOCK_USERS:
        return {
            "username": username,
            "name": MOCK_USERS[username]["name"],
            "role": MOCK_USERS[username]["role"],
        }
    return {}


def render_login_page():
    """
    Render the login form in Streamlit.
    Returns True if the user is authenticated, False otherwise.
    Sets session_state['authenticated'], session_state['user_info'].
    """
    if st.session_state.get("authenticated", False):
        return True

    # ---- Centered login card ----
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 420px;
            margin: 5rem auto;
            padding: 2.5rem;
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .login-title {
            text-align: center;
            color: #E40000;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .login-subtitle {
            text-align: center;
            color: #999;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        .cred-box {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 0.8rem 1rem;
            margin-top: 1rem;
            font-size: 0.82rem;
            color: #aaa;
            line-height: 1.7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p class="login-title">🔒 Airtel Support</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-subtitle">RAG-Powered Customer Support Portal</p>',
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password"
            )
            submit = st.form_submit_button("🚀 Sign In", use_container_width=True)

            if submit:
                if verify_credentials(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = get_user_info(username)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")

        st.markdown(
            """
            <div class="cred-box">
                <strong>Demo Credentials:</strong><br>
                👤 <code>admin</code> / <code>admin123</code><br>
                👤 <code>agent</code> / <code>agent123</code><br>
                👤 <code>demo</code> / <code>demo123</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return False


def render_logout_button():
    """Render a logout button in the sidebar."""
    user = st.session_state.get("user_info", {})
    if user:
        st.sidebar.markdown(f"**👤 {user.get('name', 'User')}**")
        st.sidebar.caption(f"Role: {user.get('role', 'N/A')}")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = {}
        st.session_state["messages"] = []
        st.rerun()
