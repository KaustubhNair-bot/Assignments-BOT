import streamlit as st
import os
from dotenv import load_dotenv
from src.auth import check_auth, login_user, refresh_access_token
from src.evaluator import RAGEvaluator

# Load environment variables
load_dotenv()

# --- 1. INITIALIZATION ---
st.set_page_state = "wide"  # Better for the Benchmark Tab
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None


# --- 2. AUTHENTICATION UI ---
def login_screen():
    st.title("🔒 Tesla Secure Internal Access")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        tokens = login_user(email, password)
        if tokens:
            st.session_state.access_token = tokens["access_token"]
            st.session_state.refresh_token = tokens["refresh_token"]
            st.success("Access Granted.")
            st.rerun()
        else:
            st.error("Invalid Credentials.")


# --- 3. MAIN INTERFACE ---
def main_interface():
    # Sidebar for Settings & Metadata
    st.sidebar.header("⚙️ Auditor Settings")
    temp_val = st.sidebar.slider("Temperature (0 = Fact, 1 = Creative)", 0.0, 1.0, 0.1)
    top_p_val = st.sidebar.slider("Top-P (0 = Strict, 1 = Diverse)", 0.0, 1.0, 0.9)

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # Load RAG Engine once
    if not st.session_state.rag_engine:
        with st.spinner("Initializing Auditor Intelligence..."):
            from src.utils import process_pdfs
            from src.engine import TeslaRAGEngine

            chunks = process_pdfs("./data")
            st.session_state.rag_engine = TeslaRAGEngine(chunks)
            st.sidebar.success("✅ Documents Indexed")

    # --- TABS FOR BENCHMARKING ---
    tab1, tab2 = st.tabs(["💬 Supply Chain Auditor", "📊 Performance Benchmark"])

    with tab1:
        st.title("🔋 Tesla Intelligence")

        # Display persistent chat bubbles
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message:
                    for i, doc in enumerate(message["sources"]):
                        with st.expander(f"📍 Evidence Segment {i + 1}"):
                            st.code(doc["page_content"], language="markdown")

        # Chat Input logic
        query = st.chat_input("Query Tesla's internal supply chain data...")
        if query:
            if check_auth():
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)

                # Generate Assistant Response
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing Logistics..."):
                        response, sources = st.session_state.rag_engine.get_response(
                            query, temp=temp_val, top_p=top_p_val
                        )
                        st.markdown(response)

                        # Store in history for Tab 2 to use
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": response,
                                "sources": sources,
                            }
                        )

                # Instant Evaluation for Tab 2
                evaluator = RAGEvaluator()
                context_text = " ".join([d["page_content"] for d in sources])
                st.session_state.last_evaluation = evaluator.grade_response(
                    query, context_text, response
                )
                st.rerun()

    with tab2:
        st.header("📈 Real-Time RAG Metrics")
        if st.session_state.last_evaluation:
            scores = st.session_state.last_evaluation

            # KPI Metrics
            c1, c2 = st.columns(2)
            c1.metric("Faithfulness (No Hallucination)", f"{scores['faithfulness']}/10")
            c2.metric("Answer Relevancy", f"{scores['relevancy']}/10")

            st.subheader("Judge's Logic")
            st.info(scores["reasoning"])

            # Screenshot help: Explains the parameters used
            st.write(
                f"**Current Benchmark State:** Temp={temp_val} | Top-P={top_p_val}"
            )
        else:
            st.write("Run a query in the Auditor tab to generate performance data.")


# --- 4. EXECUTION FLOW ---
if not check_auth():
    login_screen()
else:
    main_interface()
