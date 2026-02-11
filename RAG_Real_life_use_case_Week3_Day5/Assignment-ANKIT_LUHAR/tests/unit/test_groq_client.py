"""
Tests — Groq Client.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.generation.groq_client import GroqClient


class TestGroqClient:
    """Tests for the GroqClient class."""

    @patch("src.generation.groq_client.Groq")
    def test_chat_completion(self, mock_groq_cls):
        """chat_completion should return response text."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="DP World operates globally."))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_cls.return_value = mock_client

        client = GroqClient()
        result = client.chat_completion([
            {"role": "user", "content": "Tell me about DP World"}
        ])

        assert result == "DP World operates globally."
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.generation.groq_client.Groq")
    def test_chat_completion_error(self, mock_groq_cls):
        """Should raise on API error."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit")
        mock_groq_cls.return_value = mock_client

        client = GroqClient()
        with pytest.raises(Exception, match="Rate limit"):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("src.generation.groq_client.Groq")
    def test_custom_temperature(self, mock_groq_cls):
        """Custom temperature should be passed to API."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_cls.return_value = mock_client

        client = GroqClient()
        client.chat_completion(
            [{"role": "user", "content": "test"}],
            temperature=0.9,
        )

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.9
