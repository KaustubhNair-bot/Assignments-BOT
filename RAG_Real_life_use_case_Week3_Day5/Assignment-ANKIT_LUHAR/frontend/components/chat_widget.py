"""
DP World RAG Chatbot — Chat Widget Component.

Renders the main chat interface with message history, retrieved chunks,
and generation parameter display for full RAG transparency.
"""

from __future__ import annotations

import requests
import streamlit as st


def render_chat() -> None:
    """Render the chat interface."""
    # ── Header ──────────────────────────────────────────────
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="
            background: linear-gradient(135deg, #0066CC 0%, #00AAFF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        ">🚢 DP World Assistant</h1>
        <p style="color: #888; font-size: 1.05rem;">
            Your AI-powered Senior Logistics Consultant &mdash; with Chain-of-Thought reasoning
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Initialize session if needed ────────────────────────
    if st.session_state.session_id is None:
        _start_session()

    # ── Display Chat Messages ───────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            _render_message(msg["role"], msg["content"])
            # Show retrieved chunks inline if stored with the message
            if msg["role"] == "assistant" and st.session_state.get("show_chunks", True):
                chunks = msg.get("retrieved_chunks", [])
                gen_params = msg.get("generation_params", {})
                if chunks:
                    _render_retrieved_chunks(chunks, gen_params)

    # ── Handle pending question from sidebar quick buttons ─
    prompt = None
    if st.session_state.get("pending_question"):
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None

    # ── Chat Input ──────────────────────────────────────────
    if typed := st.chat_input("Ask about DP World services, shipping, ports..."):
        prompt = typed

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        _render_message("user", prompt)

        # Get response with loading animation
        with st.spinner("🔍 Searching knowledge base & applying Chain-of-Thought reasoning..."):
            response_data = _send_message(prompt)

        _process_response(response_data)


def _render_message(role: str, content: str) -> None:
    """Render a single chat message."""
    with st.chat_message(role, avatar="🧑" if role == "user" else "🚢"):
        st.markdown(content)


def _process_response(response_data: dict | None) -> None:
    """Process and display the API response."""
    if response_data:
        assistant_msg = response_data.get("response", "Sorry, I couldn't process your request.")
        sources = response_data.get("sources", [])
        retrieved_chunks = response_data.get("retrieved_chunks", [])
        gen_params = response_data.get("generation_params", {})

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_msg,
            "retrieved_chunks": retrieved_chunks,
            "generation_params": gen_params,
        })
        _render_message("assistant", assistant_msg)

        # Show retrieved chunks for verification
        if st.session_state.get("show_chunks", True) and retrieved_chunks:
            _render_retrieved_chunks(retrieved_chunks, gen_params)

        # Show sources
        if sources:
            with st.expander("📚 Sources", expanded=False):
                for i, src in enumerate(sources, 1):
                    st.markdown(f"{i}. [{src}]({src})")
    else:
        error_msg = "⚠️ Unable to reach the API. Please ensure the backend is running."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        _render_message("assistant", error_msg)


def _render_retrieved_chunks(chunks: list[dict], gen_params: dict) -> None:
    """Render retrieved chunks for source verification + generation parameters."""
    with st.expander(f"🔎 Retrieved Chunks ({len(chunks)} found) — Click to verify sources", expanded=False):
        # Generation parameters used
        if gen_params:
            st.markdown("**⚙️ Generation Parameters Used:**")
            param_cols = st.columns(3)
            with param_cols[0]:
                temp = gen_params.get("temperature", "N/A")
                st.metric("Temperature", f"{temp}")
            with param_cols[1]:
                tp = gen_params.get("top_p", "N/A")
                st.metric("Top-P", f"{tp}")
            with param_cols[2]:
                model = gen_params.get("model", "N/A")
                st.metric("Model", model.split("/")[-1] if model else "N/A")
            st.markdown("---")

        # Retrieved chunks
        for i, chunk in enumerate(chunks, 1):
            score = chunk.get("score", 0)
            title = chunk.get("title", "Untitled")
            source = chunk.get("source", "")
            text = chunk.get("text", "")

            # Score colour
            if score >= 0.8:
                score_color = "#10B981"  # green
                score_label = "🟢 High"
            elif score >= 0.5:
                score_color = "#F59E0B"  # amber
                score_label = "🟡 Medium"
            else:
                score_color = "#EF4444"  # red
                score_label = "🔴 Low"

            st.markdown(f"""
            <div style="
                background: #1a1d23;
                border: 1px solid #2a2e37;
                border-left: 4px solid {score_color};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.5rem;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong style="color: #E6E9EF;">Chunk #{i}: {title}</strong>
                    <span style="
                        background: {score_color}22;
                        color: {score_color};
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: 0.8rem;
                    ">{score_label} ({score:.4f})</span>
                </div>
                <p style="color: #8B95A5; font-size: 0.85rem; margin: 0.5rem 0;">{text[:300]}{'...' if len(text) > 300 else ''}</p>
                <p style="color: #0066CC; font-size: 0.75rem; margin: 0;">{source}</p>
            </div>
            """, unsafe_allow_html=True)


def _start_session() -> None:
    """Create a new chat session via the API."""
    try:
        resp = requests.post(
            f"{st.session_state.api_base_url}/api/v1/chat/session",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            st.session_state.session_id = data.get("session_id")
            welcome = data.get("message", "")
            if welcome:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": welcome,
                })
    except requests.RequestException:
        st.session_state.session_id = "local-fallback"
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "👋 Welcome to **DP World Assistant**!\n\n"
                "⚠️ *Running in offline mode — API is not available.*\n\n"
                "Please start the FastAPI backend with `make api` to enable full functionality."
            ),
        })


def _send_message(message: str) -> dict | None:
    """Send a message to the chat API with current generation parameters."""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id,
        }

        # Pass generation parameters if set
        if hasattr(st.session_state, "temperature"):
            payload["temperature"] = st.session_state.temperature
        if hasattr(st.session_state, "top_p"):
            payload["top_p"] = st.session_state.top_p

        resp = requests.post(
            f"{st.session_state.api_base_url}/api/v1/chat/",
            json=payload,
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json().get("data", {})
    except requests.RequestException:
        pass
    return None
