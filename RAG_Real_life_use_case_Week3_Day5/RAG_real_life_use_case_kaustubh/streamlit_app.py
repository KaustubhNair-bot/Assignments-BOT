"""
Airtel RAG Customer Support Chatbot — Streamlit Application.

Features:
- Mock login authentication
- Chat interface with conversation history
- Retrieved chunks display for source verification
- Sidebar controls for temperature, top-p, CoT toggle
- Evaluation runner
- RAG statistics dashboard
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Ensure app package is importable
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.auth import render_login_page, render_logout_button
from app.rag_engine import RAGEngine
from app.llm_engine import LLMEngine
from app.evaluation import run_full_evaluation, TEST_CASES

# ================================================================== #
#  PAGE CONFIG                                                        #
# ================================================================== #
st.set_page_config(
    page_title="Airtel Customer Support | RAG Chatbot",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================== #
#  CUSTOM CSS                                                         #
# ================================================================== #
st.markdown(
    """
    <style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #E40000 0%, #B30000 50%, #8B0000 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 4px 20px rgba(228, 0, 0, 0.3);
    }
    .main-header h1 {
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 0.9rem;
        margin: 0;
    }

    /* Chat messages */
    .user-msg {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #e0e0e0;
    }
    .bot-msg {
        background: linear-gradient(135deg, #0f3460, #1a1a2e);
        border: 1px solid rgba(228, 0, 0, 0.2);
        border-left: 3px solid #E40000;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #e0e0e0;
    }

    /* Chunk cards */
    .chunk-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .chunk-header {
        color: #E40000;
        font-weight: 600;
        font-size: 0.78rem;
        margin-bottom: 0.4rem;
    }

    /* Sidebar styling */
    .sidebar-section {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* Stats cards */
    .stat-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid rgba(228,0,0,0.15);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-value {
        color: #E40000;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .stat-label {
        color: #999;
        font-size: 0.8rem;
        margin-top: 0.2rem;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ================================================================== #
#  INITIALIZATION (cached)                                            #
# ================================================================== #
@st.cache_resource(show_spinner="🔧 Loading RAG engine & embedding model...")
def init_rag_engine():
    """Initialize the RAG engine (load/build FAISS index)."""
    engine = RAGEngine()
    engine.initialize()
    return engine


@st.cache_resource(show_spinner="🤖 Loading LLM engine...")
def init_llm_engine(temperature=0.3, top_p=0.85, enable_cot=True):
    """Initialize the LLM engine with Gemini."""
    return LLMEngine(temperature=temperature, top_p=top_p, enable_cot=enable_cot)


# ================================================================== #
#  AUTHENTICATION GATE                                                #
# ================================================================== #
if not render_login_page():
    st.stop()

# ================================================================== #
#  MAIN APPLICATION (after login)                                     #
# ================================================================== #

# Initialize engines
rag_engine = init_rag_engine()
llm_engine = init_llm_engine()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_chunks" not in st.session_state:
    st.session_state.last_chunks = []

# ------------------------------------------------------------------ #
#  SIDEBAR                                                            #
# ------------------------------------------------------------------ #
with st.sidebar:
    render_logout_button()
    st.markdown("---")

    st.markdown("### ⚙️ Generation Parameters")

    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="0.0 = factual/deterministic, 1.0 = creative/diverse",
    )

    top_p = st.slider(
        "🎯 Top-P (Nucleus Sampling)",
        min_value=0.1,
        max_value=1.0,
        value=0.85,
        step=0.05,
        help="Controls diversity of token selection. Lower = more focused.",
    )

    enable_cot = st.toggle(
        "🧠 Chain-of-Thought",
        value=True,
        help="Enable CoT reasoning: model explains retrieval logic before answering.",
    )

    top_k = st.slider(
        "📄 Retrieved Chunks (top-k)",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of document chunks retrieved for context.",
    )

    # Update LLM params
    llm_engine.update_params(temperature=temperature, top_p=top_p, enable_cot=enable_cot)

    st.markdown("---")

    # RAG Stats
    st.markdown("### 📊 RAG Statistics")
    stats = rag_engine.get_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chunks", stats["total_chunks"])
        st.metric("Chunk Size", stats["chunk_size"])
    with col2:
        st.metric("Vectors", stats["index_vectors"])
        st.metric("Overlap", stats["chunk_overlap"])
    st.caption(f"Model: `{stats['embedding_model']}`")
    st.caption(f"Dimension: `{stats['embedding_dim']}`")

    st.markdown("---")

    # LLM Config display
    st.markdown("### 🤖 LLM Configuration")
    llm_config = llm_engine.get_config()
    st.json(llm_config)

    st.markdown("---")

    # Evaluation
    st.markdown("### 🧪 Evaluation")
    if st.button("🚀 Run Benchmark", use_container_width=True):
        with st.spinner("Running evaluation across 10 test cases..."):
            eval_results = run_full_evaluation(rag_engine, llm_engine)
            st.session_state["eval_results"] = eval_results
        st.success("✅ Evaluation complete!")

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_chunks = []
        st.rerun()


# ------------------------------------------------------------------ #
#  MAIN CONTENT AREA                                                  #
# ------------------------------------------------------------------ #

# Header
st.markdown(
    """
    <div class="main-header">
        <div>
            <h1>📡 Airtel Customer Support</h1>
            <p>RAG-Powered AI Assistant — Ask about plans, policies, billing & more</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tab layout
tab_chat, tab_chunks, tab_eval, tab_compare = st.tabs(
    ["💬 Chat", "📄 Retrieved Chunks", "📊 Evaluation", "🔬 Temperature Comparison"]
)

# ---- CHAT TAB ----
with tab_chat:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🙋" if msg["role"] == "user" else "📡"):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about Airtel plans, billing, policies..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(prompt)

        # Retrieve relevant chunks
        with st.spinner("🔍 Searching knowledge base..."):
            retrieved = rag_engine.retrieve(prompt, top_k=top_k)
            st.session_state.last_chunks = retrieved

        # Generate response
        with st.chat_message("assistant", avatar="📡"):
            with st.spinner("🤖 Generating response..."):
                response = llm_engine.generate(
                    prompt,
                    retrieved,
                    chat_history=st.session_state.messages[:-1],
                )
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# ---- RETRIEVED CHUNKS TAB ----
with tab_chunks:
    st.markdown("### 📄 Retrieved Document Chunks")
    st.caption("These are the source chunks retrieved from Airtel's knowledge base for your last query.")

    if st.session_state.last_chunks:
        for i, (chunk_text, score, chunk_idx) in enumerate(st.session_state.last_chunks, 1):
            with st.expander(f"📌 Chunk {i} — Index #{chunk_idx} | Distance: {score:.4f}", expanded=(i <= 2)):
                st.markdown(
                    f"""
                    <div class="chunk-card">
                        <div class="chunk-header">Chunk #{chunk_idx} | Relevance Score: {score:.4f} | Length: {len(chunk_text)} chars</div>
                        {chunk_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("💡 Ask a question in the Chat tab to see retrieved chunks here.")


# ---- EVALUATION TAB ----
with tab_eval:
    st.markdown("### 📊 RAG Evaluation Results")

    eval_results = st.session_state.get("eval_results")

    if eval_results:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{eval_results['summary']['avg_keyword_score']:.0%}</div>
                    <div class="stat-label">Avg Keyword Match</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{eval_results['summary']['avg_hallucination_rate']:.0%}</div>
                    <div class="stat-label">Avg Hallucination Rate</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{len(eval_results['test_results'])}</div>
                    <div class="stat-label">Test Cases</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{eval_results['model']}</div>
                    <div class="stat-label">Model Used</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Per-question results table
        st.markdown("#### Per-Question Results")
        import pandas as pd
        rows = []
        for tr in eval_results["test_results"]:
            rows.append({
                "ID": tr["test_id"],
                "Category": tr["category"],
                "Keyword Score": f"{tr['keyword_evaluation']['score']:.0%}",
                "Keywords Matched": f"{tr['keyword_evaluation']['total_matched']}/{tr['keyword_evaluation']['total_expected']}",
                "Hallucination Rate": f"{tr['hallucination_evaluation']['hallucination_rate']:.0%}",
                "Response Length": tr["response_length"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Missed keywords details
        st.markdown("#### ❌ Missed Keywords by Question")
        for tr in eval_results["test_results"]:
            missed = tr["keyword_evaluation"]["missed"]
            if missed:
                st.warning(f"Q{tr['test_id']} ({tr['category']}): Missing → {', '.join(missed)}")

    else:
        st.info("💡 Click **Run Benchmark** in the sidebar to start evaluation.")
        st.markdown("#### 📋 Test Cases")
        for tc in TEST_CASES:
            st.markdown(f"**Q{tc['id']}** ({tc['category']}): {tc['question']}")


# ---- TEMPERATURE COMPARISON TAB ----
with tab_compare:
    st.markdown("### 🔬 Temperature & Top-P Comparison")
    st.caption("Compare how different generation settings affect response quality and hallucination.")

    compare_query = st.text_input(
        "Enter a question to compare across settings:",
        value="What is the cheapest prepaid plan available on Airtel?",
    )

    if st.button("🔄 Run Comparison", use_container_width=True):
        retrieved = rag_engine.retrieve(compare_query, top_k=top_k)
        chunk_texts = [r[0] for r in retrieved]

        with st.spinner("Generating responses at 3 different settings..."):
            comparison = llm_engine.generate_with_comparison(compare_query, retrieved)

        for setting, response in comparison.items():
            with st.expander(f"⚙️ {setting}", expanded=True):
                st.markdown(response)
                st.markdown("---")
                # Quick hallucination check
                from app.evaluation import evaluate_hallucination_risk, evaluate_keyword_match
                hall = evaluate_hallucination_risk(response, chunk_texts)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Response Length", f"{len(response)} chars")
                with col2:
                    st.metric("Hallucination Rate", f"{hall['hallucination_rate']:.0%}")
                with col3:
                    st.metric("Unsupported Claims", hall["unsupported_claims"])

    # Evaluation results comparison
    eval_results = st.session_state.get("eval_results")
    if eval_results and eval_results.get("temperature_comparison"):
        st.markdown("---")
        st.markdown("#### 📊 Benchmark Temperature Comparison")
        import pandas as pd
        comp_rows = []
        for tc in eval_results["temperature_comparison"]:
            comp_rows.append({
                "Setting": tc["setting"],
                "Keyword Score": f"{tc['keyword_score']:.0%}",
                "Hallucination Rate": f"{tc['hallucination_rate']:.0%}",
                "Response Length": tc["response_length"],
            })
        df_comp = pd.DataFrame(comp_rows)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
