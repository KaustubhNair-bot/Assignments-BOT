import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="MediSecure AI", layout="wide")

# -------------------------
# Session State
# -------------------------
if "token" not in st.session_state:
    st.session_state.token = None


# -------------------------
# Login Page
# -------------------------
def login_page():
    st.title("🔐 Doctor Login - MediSecure")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{API_URL}/login",
            data={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


# -------------------------
# RAG Page
# -------------------------
def rag_page():
    st.title("🧠 Secure Medical RAG System")

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()

    query = st.text_area("Enter Patient Symptoms / Query")

    if st.button("Search Similar Cases"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{API_URL}/rag",
            data={"query": query},
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()

            st.subheader("📄 Generated Response")
            st.write(result["generated_response"])

            with st.expander("🔍 Retrieved Similar Cases"):
                for i, case in enumerate(result["retrieved_cases"]):
                    st.markdown(f"**Case {i+1}:**")
                    st.write(case)
                    st.markdown("---")

        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.token = None
            st.rerun()

        else:
            st.error("Something went wrong.")


# -------------------------
# App Flow
# -------------------------
if st.session_state.token:
    rag_page()
else:
    login_page()
