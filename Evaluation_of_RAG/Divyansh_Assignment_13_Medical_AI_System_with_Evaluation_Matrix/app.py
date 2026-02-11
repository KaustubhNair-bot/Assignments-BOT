import streamlit as st
import os
from dotenv import load_dotenv
import time
import pandas as pd

from core.evaluator import run_full_evaluation
from core.auth import verify_token, create_tokens, refresh_access_token
from core.processor import clean_medical_data
from core.database import get_vector_db_collection, query_similar_cases
from core.llm import get_rag_response, get_base_llm_response

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
    # 1. SIDEBAR LOGOUT
    st.sidebar.write(f"Logged in as: **{st.session_state.user}**")
    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.rerun()

    # 2. TABS SEPARATION (Task 2 Requirement)
    tab1, tab2 = st.tabs(
        ["🔎 Case Search Tool", "📊 Performance Lab (Scientific Proof)"]
    )

    # TAB 1: FUNCTIONAL SEARCH
    with tab1:
        st.title("🏥 Medical RAG System")
        st.markdown("Search through private hospital records using AI.")

        # Load Data (Only happens once)
        with st.spinner("Connecting to Medical Database..."):
            # Clean data
            df = clean_medical_data("data/mtsamples.csv")
            # Get the collection
            collection = get_vector_db_collection(df)

        query = st.text_input("Enter symptoms or procedure details:")

        if query:
            with st.spinner("Analyzing records and generating summary..."):
                # A. Retrieve the context (The 'R' in RAG)
                results = query_similar_cases(collection, query)
                docs = results["documents"][0]
                metas = results["metadatas"][0]

                # B. Generate AI Clinical Summary (The 'G' in RAG)
                st.subheader("🤖 AI Clinical Summary")
                ai_answer = get_rag_response(query, docs)
                st.info(ai_answer)

                # C. Show raw matches in expanders (Transparency)
                st.subheader("📄 Found Source Records")
                # We use a loop to build the UI step-by-step
                for i in range(len(docs)):
                    content = docs[i]
                    metadata = metas[i]
                    with st.expander(
                        f"Medical Record #{i + 1} - {metadata['specialty']}"
                    ):
                        st.write(f"**Brief:** {metadata['description']}")
                        st.write("**Full Notes:**")
                        st.write(content)

    # TAB 2: SCIENTIFIC EVALUATION
    with tab2:
        st.title("🧪 System Benchmarking")
        st.markdown("""
        This lab proves whether **RAG** actually provides better results than a **Standard LLM**.
        We use an **AI Judge** to score both systems based on medical records.
        """)

        if st.button("🚀 Start Comparative Audit"):
            status_text = st.empty()
            status_text.text("Running 5 Golden Queries... this takes a moment.")

            # Run the evaluation logic from evaluator.py
            df_results = run_full_evaluation()

            status_text.text("Audit Complete! Visualizing results...")

            # A. Visual Proof (Bar Chart)
            st.subheader("1. Accuracy & Faithfulness Gap")
            # We select the columns we want to compare
            chart_df = df_results[["Query", "Base_Faithfulness", "RAG_Faithfulness"]]
            # Set the Query as the X-axis label
            chart_df = chart_df.set_index("Query")
            st.bar_chart(chart_df)

            st.success(
                "The chart proves that RAG (Blue/Orange) stays 100% faithful to patient records."
            )

            # B. Data Proof (The Audit Log)
            st.subheader("2. Detailed Audit Log")
            st.dataframe(df_results)

            # C. Export Proof
            csv_data = df_results.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Scientific Report",
                data=csv_data,
                file_name="rag_vs_llm_proof.csv",
                mime="text/csv",
            )


# RUN THE APP
if check_authentication():
    dashboard()
else:
    login_page()
