import jwt
import datetime
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# two different secrets for higher security
ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET")
REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")

# Mock Database
MOCK_USERS = {"admin@tesla.com": "elon123"}


def create_access_token(email):
    """Creates a short-lived 15-minute token."""
    payload = {
        "sub": email,
        # Using timezone-aware UTC for modern Python compatibility
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=15),
        "type": "access",
    }
    return jwt.encode(payload, ACCESS_SECRET, algorithm="HS256")


def create_refresh_token(email):
    """Creates a long-lived 7-day token."""
    payload = {
        "sub": email,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=7),
        "type": "refresh",
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")


def login_user(email, password):
    """The Entry Gate: Checks credentials and issues both tokens."""
    if email in MOCK_USERS and MOCK_USERS[email] == password:
        return {
            "access_token": create_access_token(email),
            "refresh_token": create_refresh_token(email),
        }
    return None


def verify_access_token(token):
    """Checks if the access token is valid and not expired."""
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=["HS256"])
        return "VALID"
    except jwt.ExpiredSignatureError:
        return "EXPIRED"  # This triggers the silent refresh logic
    except jwt.InvalidTokenError:
        return "INVALID"


def refresh_access_token(refresh_token):
    """Validates the refresh token and issues a NEW access token."""
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET, algorithms=["HS256"])
        if payload["type"] == "refresh":
            return create_access_token(payload["sub"])
    except:
        return None


def check_auth():
    """The Security Guard: Used by app.py to protect the RAG engine."""
    # 1. Check if token exists in session
    if "access_token" not in st.session_state or st.session_state.access_token is None:
        return False

    # 2. Verify current token
    status = verify_access_token(st.session_state.access_token)

    if status == "VALID":
        return True

    # 3. Handle Silent Refresh if expired
    if status == "EXPIRED":
        new_token = refresh_access_token(st.session_state.refresh_token)
        if new_token:
            st.session_state.access_token = new_token
            return True

    # 4. Final fail: User must log in again
    return False
