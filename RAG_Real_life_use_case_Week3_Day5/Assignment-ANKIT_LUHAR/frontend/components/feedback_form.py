"""
DP World RAG Chatbot — Feedback Form Component.

Inline feedback form for rating chatbot responses.
"""

from __future__ import annotations

import requests
import streamlit as st


def render_feedback_form(message_id: str = "") -> None:
    """Render a feedback form for a specific message."""
    with st.expander("📝 Rate this response", expanded=False):
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("👍 Helpful", key=f"thumbs_up_{message_id}"):
                _submit_feedback(1, message_id)
                st.success("Thanks for the feedback!")

        with col2:
            if st.button("👎 Not Helpful", key=f"thumbs_down_{message_id}"):
                _submit_feedback(-1, message_id)
                st.info("Thanks — we'll work on improving!")

        comment = st.text_area(
            "Additional comments (optional)",
            key=f"comment_{message_id}",
            max_chars=500,
        )
        if st.button("Submit Comment", key=f"submit_{message_id}"):
            _submit_feedback(0, message_id, comment)
            st.success("Comment submitted!")


def _submit_feedback(rating: int, message_id: str, comment: str = "") -> None:
    """Submit feedback to the API."""
    try:
        requests.post(
            f"{st.session_state.api_base_url}/api/v1/feedback/",
            json={
                "session_id": st.session_state.get("session_id", ""),
                "rating": rating,
                "comment": comment,
                "message_id": message_id,
            },
            timeout=5,
        )
    except requests.RequestException:
        pass
