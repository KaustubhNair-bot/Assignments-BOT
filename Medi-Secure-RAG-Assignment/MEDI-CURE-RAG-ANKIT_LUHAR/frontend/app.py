import streamlit as st
import requests

st.set_page_config(
    page_title="Medical RAG System",
    page_icon="🏥",
    layout="wide",
)

API_URL = "http://localhost:8000"

# ── Initialize session state ─────────────────────────────────────────────────
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None


# ── Auth helpers ─────────────────────────────────────────────────────────────
def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user = username
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to backend. Is it running?")


def signup(username, password):
    try:
        response = requests.post(
            f"{API_URL}/signup",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            st.success("✅ Account created successfully! Please login.")
        else:
            st.error(f"❌ {response.json().get('detail', 'Signup failed')}")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to backend.")


def logout():
    st.session_state.access_token = None
    st.session_state.user = None
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Main UI
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.access_token:
    # ── Custom CSS for login page ────────────────────────────────────────
    st.markdown("""
    <style>
        .main .block-container { max-width: 700px; padding-top: 3rem; }
        .login-hero {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .login-hero h1 { color: #fff; font-size: 2rem; margin: 0 0 0.5rem 0; }
        .login-hero p  { color: #b8b8d4; font-size: 1rem; margin: 0; }
        .demo-box {
            background: linear-gradient(135deg, #1b5e20, #2e7d32);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin: 1rem 0 1.5rem 0;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }
        .demo-box h4 { color: #a5d6a7; margin: 0 0 0.5rem 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
        .demo-creds {
            display: flex;
            gap: 2rem;
            justify-content: center;
        }
        .demo-cred {
            text-align: center;
        }
        .demo-cred .label { color: #81c784; font-size: 0.75rem; margin-bottom: 0.2rem; }
        .demo-cred .value {
            color: #ffffff;
            font-size: 1.3rem;
            font-weight: 700;
            background: rgba(0,0,0,0.3);
            padding: 0.3rem 1rem;
            border-radius: 8px;
            font-family: monospace;
        }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="login-hero">
        <h1>🏥 Medical RAG System</h1>
        <p>AI-powered patient case search with Retrieval-Augmented Generation</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Demo credentials box ─────────────────────────────────────────────
    st.markdown("""
    <div class="demo-box">
        <h4>🔑 Demo Credentials — Use these to login instantly</h4>
        <div class="demo-creds">
            <div class="demo-cred">
                <div class="label">Username</div>
                <div class="value">admin</div>
            </div>
            <div class="demo-cred">
                <div class="label">Password</div>
                <div class="value">admin</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Login / Sign Up tabs ─────────────────────────────────────────────
    tab_login, tab_signup = st.tabs(["🔓 Login", "📝 Sign Up"])

    with tab_login:
        username = st.text_input("Username", key="login_user", placeholder="Enter username")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
        if st.button("Login", use_container_width=True, type="primary"):
            if username and password:
                login(username, password)
            else:
                st.warning("Please enter both username and password.")

    with tab_signup:
        new_user = st.text_input("New Username", key="signup_user", placeholder="Choose a username")
        new_pass = st.text_input("New Password", type="password", key="signup_pass", placeholder="Choose a password")
        if st.button("Create Account", use_container_width=True, type="primary"):
            if new_user and new_pass:
                signup(new_user, new_pass)
            else:
                st.warning("Please fill in all fields.")

    # ── Block sidebar navigation ─────────────────────────────────────────
    st.sidebar.warning("🔒 Please login to access the system.")

else:
    # ── Logged-in home page ──────────────────────────────────────────────
    st.title(f"Welcome, {st.session_state.user} 👋")
    st.sidebar.success(f"✅ Logged in as **{st.session_state.user}**")

    if st.sidebar.button("🚪 Logout"):
        logout()

    st.markdown("""
    ### 🏥 How to Use This System

    | Page | What It Does |
    |------|-------------|
    | **🔍 Search** | Search patient cases with RAG-powered answers + compare RAG vs Base LLM |
    | **📊 Dashboard** | View system statistics and case distribution |
    | **📁 Upload Case** | Add new patient cases to the knowledge base |
    | **📈 Evaluation** | Interactive dashboard comparing RAG vs Base LLM evaluation results |

    Navigate using the **sidebar** on the left. 👈
    """)
