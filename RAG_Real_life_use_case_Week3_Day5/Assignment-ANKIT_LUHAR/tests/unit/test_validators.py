"""
Tests — Validators.
"""

from __future__ import annotations

import pytest

from src.utils.validators import (
    ValidationError,
    validate_message,
    validate_rating,
    validate_session_id,
    validate_top_k,
    sanitize_input,
)


class TestValidators:
    """Tests for input validators."""

    def test_valid_message(self):
        assert validate_message("Hello, DP World!") == "Hello, DP World!"

    def test_empty_message(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_message("")

    def test_whitespace_message(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_message("   ")

    def test_long_message(self):
        with pytest.raises(ValidationError, match="maximum length"):
            validate_message("a" * 3000)

    def test_short_message(self):
        with pytest.raises(ValidationError, match="too short"):
            validate_message("a")

    def test_message_trimmed(self):
        assert validate_message("  hello  ") == "hello"

    def test_valid_session_id(self):
        sid = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
        assert validate_session_id(sid) == sid

    def test_invalid_session_id(self):
        with pytest.raises(ValidationError, match="Invalid session"):
            validate_session_id("not-a-uuid")

    def test_valid_rating(self):
        assert validate_rating(1) == 1
        assert validate_rating(-1) == -1
        assert validate_rating(5) == 5

    def test_invalid_rating(self):
        with pytest.raises(ValidationError, match="Rating"):
            validate_rating(10)

    def test_valid_top_k(self):
        assert validate_top_k(5) == 5

    def test_invalid_top_k(self):
        with pytest.raises(ValidationError):
            validate_top_k(0)
        with pytest.raises(ValidationError):
            validate_top_k(25)

    def test_sanitize_input(self):
        result = sanitize_input("Hello\x00World")
        assert "\x00" not in result
        assert "Hello" in result
