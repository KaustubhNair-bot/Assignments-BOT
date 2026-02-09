import streamlit as st
import requests
import os

# Create pages directory if it doesn't exist to avoid errors
# os.makedirs("frontend/pages", exist_ok=True) # Already done in init

st.set_page_config(
    page_title="Medical RAG System",
    page_icon="🏥",
    layout="wide"
)

API_URL = "http://localhost:8000"

# Initialize session state
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

if 'user' not in st.session_state:
    st.session_state.user = None

def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data['access_token']
            st.session_state.user = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend. Is it running?")

def signup(username, password):
    try:
        response = requests.post(
            f"{API_URL}/signup",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.success("Account created successfully! Please login.")
        else:
            st.error(f"Error: {response.json().get('detail', 'Signup failed')}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend.")

def logout():
    st.session_state.access_token = None
    st.session_state.user = None
    st.rerun()

# Main UI
if not st.session_state.access_token:
    st.title("🏥 Medical RAG System")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.header("Login")
        col1, col2 = st.columns([1, 2])
        with col1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                login(username, password)
                
        with col2:
            st.info("Default credentials: admin / admin")

    with tab2:
        st.header("Create Account")
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if new_user and new_pass:
                signup(new_user, new_pass)
            else:
                st.warning("Please fill in all fields")
else:
    st.title(f"Welcome, {st.session_state.user}")
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    
    if st.sidebar.button("Logout"):
        logout()
        
    st.markdown("""
    ### How to use
    1. Go to **Search** page to find similar patient cases.
    2. View **Dashboard** for system statistics.
    """)
