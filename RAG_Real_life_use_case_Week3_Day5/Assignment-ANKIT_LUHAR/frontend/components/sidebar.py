"""
DP World RAG Chatbot — Sidebar Component.

Renders the sidebar with session controls, generation parameter tuning,
user info, and API status.
"""

from __future__ import annotations

import requests
import streamlit as st

try:
    from src.generation.prompt_templates import GENERATION_PRESETS
except ImportError:
    # Fallback if import path not resolved
    GENERATION_PRESETS = {
        "factual": {
            "temperature": 0.0, "top_p": 0.5,
            "label": "🎯 Factual (Temp=0.0, Top-P=0.5)",
            "description": "Most deterministic. Best for factual Q&A. Lowest hallucination risk.",
        },
        "balanced": {
            "temperature": 0.3, "top_p": 0.7,
            "label": "⚖️ Balanced (Temp=0.3, Top-P=0.7)",
            "description": "Default. Good balance of accuracy and natural language flow.",
        },
        "creative": {
            "temperature": 0.8, "top_p": 0.9,
            "label": "🎨 Creative (Temp=0.8, Top-P=0.9)",
            "description": "More varied language. Higher hallucination risk.",
        },
    }


def render_sidebar() -> None:
    """Render the sidebar with controls and information."""
    with st.sidebar:
        # ── Logo / Brand ────────────────────────────────────
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #333;">
            <h2 style="color: #0066CC; margin: 0;">🚢 DP World</h2>
            <p style="color: #888; font-size: 0.85rem; margin-top: 4px;">
                AI Senior Logistics Consultant
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Logged-in User ──────────────────────────────────
        if st.session_state.get("username"):
            st.markdown(f"👤 Logged in as: **{st.session_state.username}**")

        st.markdown("---")

        # ── Session Info ────────────────────────────────────
        st.markdown("### 💬 Session")
        if st.session_state.session_id:
            st.caption(f"ID: `{st.session_state.session_id[:8]}...`")
            st.caption(f"Messages: {len(st.session_state.messages)}")

        # ── Controls ────────────────────────────────────────
        st.markdown("### ⚙️ Controls")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        st.markdown("---")

        # ── Generation Parameters ───────────────────────────
        st.markdown("### 🎛️ Generation Parameters")
        st.caption("Experiment with these to see how they affect response quality and hallucination.")

        # Preset selector
        preset = st.selectbox(
            "Preset",
            options=list(GENERATION_PRESETS.keys()),
            format_func=lambda k: GENERATION_PRESETS[k]["label"],
            index=1,  # balanced default
            key="preset_selector",
        )

        selected = GENERATION_PRESETS[preset]
        st.caption(selected["description"])

        # Manual temperature slider
        st.session_state.temperature = st.slider(
            "🌡️ Temperature",
            min_value=0.0,
            max_value=1.0,
            value=selected["temperature"],
            step=0.1,
            help="0.0 = deterministic/factual, 1.0 = creative/varied. Lower values reduce hallucination.",
        )

        # Manual top-p slider
        st.session_state.top_p = st.slider(
            "🎯 Top-P (Nucleus Sampling)",
            min_value=0.0,
            max_value=1.0,
            value=selected["top_p"],
            step=0.1,
            help="Controls diversity. 0.5 = focused, 1.0 = full vocabulary. Lower values reduce hallucination.",
        )

        # Show retrieved chunks toggle
        st.session_state.show_chunks = st.checkbox(
            "🔎 Show Retrieved Chunks",
            value=st.session_state.get("show_chunks", True),
            help="Display the raw retrieved text chunks so you can verify the source.",
        )

        # Parameter info box
        st.markdown(f"""
        <div style="
            background: rgba(0, 102, 204, 0.1);
            border: 1px solid rgba(0, 102, 204, 0.2);
            border-radius: 8px;
            padding: 0.75rem;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #8B95A5;
        ">
            <strong style="color: #00AAFF;">Current Settings:</strong><br>
            Temperature: <code>{st.session_state.temperature}</code><br>
            Top-P: <code>{st.session_state.top_p}</code><br>
            Preset: <code>{preset}</code>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── API Status ──────────────────────────────────────
        st.markdown("### 📡 API Status")
        try:
            resp = requests.get(
                f"{st.session_state.api_base_url}/api/v1/health/",
                timeout=3,
            )
            if resp.status_code == 200:
                health = resp.json()
                st.success(f"✅ {health.get('status', 'connected').title()}")
            else:
                st.warning("⚠️ API returned an error")
        except requests.RequestException:
            st.error("❌ API Offline")

        # ── Quick Questions ─────────────────────────────────
        st.markdown("### 💡 Try asking:")
        quick_questions = [
            "How do I book a shipment?",
            "How can I track my container?",
            "Tell me about DP World ports",
            "What are the shipping tariffs?",
            "DP World trade solutions",
        ]
        for q in quick_questions:
            if st.button(q, key=f"quick_{q[:20]}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

        # ── Footer ──────────────────────────────────────────
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 0.75rem;'>"
            "Powered by Groq (LLM) + Cohere (Embeddings) + Pinecone (VectorDB)<br>"
            "Chain-of-Thought Reasoning | RAG Pipeline<br>"
            "© 2026 DP World AI Team"
            "</p>",
            unsafe_allow_html=True,
        )
