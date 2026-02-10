import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="MediSecure AI", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None

def login_page():
    st.title("🔐 Doctor Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{API_URL}/login",
            data={"username": user, "password": pwd},
            timeout=10
        )

        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

def rag_page():
    st.title("🏥 Secure Medical RAG System")

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()

    query = st.text_area("Enter patient symptoms")

    if st.button("Search Similar Cases"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        res = requests.post(
            f"{API_URL}/ask",
            data={"question": query},
            headers=headers,
            timeout=60
        )

        if res.status_code == 200:
            st.write(res.json()["answer"])
        elif res.status_code == 401:
            st.error("Session expired")
            st.session_state.token = None
            st.rerun()
        else:
            st.error(f"Error {res.status_code}")
            st.code(res.text)

if st.session_state.token:
    rag_page()
else:
    login_page()
