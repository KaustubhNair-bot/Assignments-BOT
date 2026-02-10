"""
JWT Authentication Module for Secure Medical RAG System
Handles user login, token generation, and authentication validation
"""

import jwt
import datetime
from typing import Optional, Dict
import streamlit as st
from app.config import Config, DEMO_USERS

class AuthManager:
    """Manages JWT authentication for the application"""
    
    def __init__(self):
        self.secret_key = Config.JWT_SECRET_KEY
        self.algorithm = Config.JWT_ALGORITHM
        self.expiration_hours = Config.JWT_EXPIRATION_HOURS
    
    def generate_token(self, username: str) -> str:
        """
        Generate a JWT token for authenticated user
        
        Args:
            username: The username of the authenticated user
            
        Returns:
            JWT token string
        """
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=self.expiration_hours)
        
        payload = {
            'username': username,
            'name': DEMO_USERS[username]['name'],
            'specialization': DEMO_USERS[username]['specialization'],
            'exp': expiration_time,
            'iat': datetime.datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials
        
        Args:
            username: Username
            password: Password
            
        Returns:
            True if credentials are valid, False otherwise
        """
        if username in DEMO_USERS:
            return DEMO_USERS[username]['password'] == password
        return False
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Get current authenticated user from session state
        
        Returns:
            User information if authenticated, None otherwise
        """
        if 'token' in st.session_state:
            token = st.session_state.token
            user_info = self.verify_token(token)
            return user_info
        return None
    
    def login_required(self):
        """
        Decorator function to check if user is authenticated
        Redirects to login page if not authenticated
        """
        if 'token' not in st.session_state:
            st.error("Please login to access this page.")
            st.stop()
        
        user_info = self.get_current_user()
        if user_info is None:
            st.error("Session expired. Please login again.")
            if 'token' in st.session_state:
                del st.session_state.token
            st.stop()
        
        return user_info

def login_page(auth_manager: AuthManager):
    """
    Display login page and handle authentication
    
    Args:
        auth_manager: Instance of AuthManager
    """
    st.title("🏥 Doctor Login")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Secure Medical RAG System")
        st.write("Please enter your credentials to access patient case search.")
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit_button = st.form_submit_button("Login", type="primary")
            
            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif auth_manager.authenticate_user(username, password):
                    # Generate and store token
                    token = auth_manager.generate_token(username)
                    st.session_state.token = token
                    st.success(f"Welcome {DEMO_USERS[username]['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        
        st.markdown("---")
        st.subheader("Demo Credentials")
        st.info("""
        **Available Demo Users:**
        - Username: `dr_smith`, Password: `password123` (Cardiology)
        - Username: `dr_johnson`, Password: `password123` (Neurology)  
        - Username: `dr_wilson`, Password: `password123` (General Medicine)
        """)
