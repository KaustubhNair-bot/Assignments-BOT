"""
DP World RAG Chatbot — Input Validators.

Validation helpers for API inputs and user messages.
"""

from __future__ import annotations

import re
from typing import Optional

from config.constants import MAX_MESSAGE_LENGTH


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str = "") -> None:
        self.field = field
        super().__init__(message)


def validate_message(message: str) -> str:
    """Validate a user chat message."""
    if not message or not message.strip():
        raise ValidationError("Message cannot be empty", field="message")

    message = message.strip()

    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters",
            field="message",
        )

    if len(message) < 2:
        raise ValidationError("Message is too short", field="message")

    return message


def validate_session_id(session_id: str) -> str:
    """Validate a session ID format (UUID v4)."""
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    if not uuid_pattern.match(session_id):
        raise ValidationError("Invalid session ID format", field="session_id")
    return session_id


def validate_rating(rating: int) -> int:
    """Validate a feedback rating."""
    if rating not in (-1, 1, 2, 3, 4, 5):
        raise ValidationError(
            "Rating must be -1, 1, 2, 3, 4, or 5",
            field="rating",
        )
    return rating


def validate_top_k(top_k: int) -> int:
    """Validate the top_k parameter."""
    if top_k < 1 or top_k > 20:
        raise ValidationError("top_k must be between 1 and 20", field="top_k")
    return top_k


def sanitize_input(text: str) -> str:
    """Basic input sanitisation — remove control characters."""
    # Remove non-printable characters except newlines and tabs
    return re.sub(r"[^\x20-\x7E\n\t\u00A0-\uFFFF]", "", text)
