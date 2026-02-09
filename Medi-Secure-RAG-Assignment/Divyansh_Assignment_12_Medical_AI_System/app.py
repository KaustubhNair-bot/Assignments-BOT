import streamlit as st
import os
from dotenv import load_dotenv
import time

from core.auth import verify_token, create_tokens, refresh_access_token
from core.processor import clean_medical_data
from core.database import get_vector_db_collection, query_similar_cases
from core.llm import generate_medical_summary

# Load environment variables
load_dotenv()

# STEP 1: INITIALIZE SESSION STATE
# In Streamlit, 'session_state' is like the app's short-term memory.
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None
if "user" not in st.session_state:
    st.session_state.user = None


# STEP 2: TOKEN RENEWAL LOGIC
def check_authentication():
    """
    Checks if the doctor is logged in.
    If the access token is expired, it tries to renew it silently.
    """
    if st.session_state.access_token is None:
        return False

    # Verify the current access token
    status = verify_token(st.session_state.access_token)

    # Case A: Access Token is still valid
    if status != "EXPIRED" and status is not None:
        return True

    # Case B: Access Token is expired, try to use Refresh Token
    if status == "EXPIRED":
        st.info("Access expired. Attempting silent renewal...")
        new_access = refresh_access_token(st.session_state.refresh_token)

        if new_access:
            st.session_state.access_token = new_access
            st.success("Session renewed!")
            time.sleep(1)  # Small pause so the user sees the renewal happened
            return True
        else:
            # Refresh token also expired (7 days passed)
            st.error("Session completely expired. Please log in again.")
            return False

    return False


# STEP 3: LOGIN UI
def login_page():
    st.title("🏥 Hospital Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Here we are using a simple check.
        if username == "doctor123" and password == "secure_pass":
            access, refresh = create_tokens(username)
            st.session_state.access_token = access
            st.session_state.refresh_token = refresh
            st.session_state.user = username
            st.rerun()  # Refresh the page to show the dashboard
        else:
            st.error("Invalid credentials.")


# STEP 4: MAIN SEARCH DASHBOARD
def dashboard():
    st.sidebar.write(f"Logged in as: **{st.session_state.user}**")
    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.rerun()

    st.title("🔎 Similar Case Search (RAG System)")
    st.markdown("Search through thousands of past cases safely and privately.")

    with st.spinner("Preparing Medical Brain..."):
        # 1. Clean data
        df = clean_medical_data("data/mtsamples.csv")
        # 2. Get the collection
        collection = get_vector_db_collection(df)

    # Search Bar
    query = st.text_input(
        "Enter symptoms or case details (e.g., 'patient with knee pain'):"
    )

    if query:
        with st.spinner("Searching past cases..."):
            results = query_similar_cases(collection, query)

            # 1. Generate the AI Summary
            st.subheader("🤖 AI Clinical Summary")
            # We pass the query and the documents found to our local AI
            ai_summary = generate_medical_summary(query, results["documents"][0])
            st.info(ai_summary)

            # 2. Showing the raw cases below
            st.subheader("📄 Matching Historical Records")

            # We use a loop to show the results one by one
            for i in range(len(results["documents"][0])):
                content = results["documents"][0][i]
                metadata = results["metadatas"][0][i]

                with st.expander(
                    f"Case Match #{i + 1} - Specialty: {metadata['specialty']}"
                ):
                    st.write(f"**Summary:** {metadata['description']}")
                    st.write("**Full Transcription:**")
                    st.write(content)


# RUN THE APP
if check_authentication():
    dashboard()
else:
    login_page()
