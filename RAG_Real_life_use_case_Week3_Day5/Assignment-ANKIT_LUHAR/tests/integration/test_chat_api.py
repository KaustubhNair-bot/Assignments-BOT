"""
Tests — Chat API (Integration).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.mark.integration
class TestChatAPI:
    """Integration tests for the chat API endpoints."""

    def setup_method(self):
        self.client = TestClient(app)

    def test_root(self):
        """Root endpoint should return app info."""
        resp = self.client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "version" in data

    def test_health(self):
        """Health endpoint should return healthy."""
        resp = self.client.get("/api/v1/health/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "degraded")

    def test_health_metrics(self):
        """Metrics endpoint should return stats."""
        resp = self.client.get("/api/v1/health/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "counters" in data
        assert "timers" in data

    @patch("src.api.dependencies.get_chat_manager")
    def test_create_session(self, mock_get_cm):
        """Session creation should return session_id."""
        mock_cm = AsyncMock()
        mock_cm.start_session.return_value = {
            "session_id": "test-session-id",
            "message": "Welcome!",
        }
        mock_get_cm.return_value = mock_cm

        resp = self.client.post("/api/v1/chat/session")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "session_id" in data["data"]

    @patch("src.api.dependencies.get_feedback_handler")
    def test_feedback_stats(self, mock_get_fh):
        """Feedback stats endpoint should return stats."""
        mock_fh = MagicMock()
        mock_fh.get_feedback_stats.return_value = {
            "total": 10,
            "average_rating": 4.2,
            "positive": 8,
            "negative": 2,
        }
        mock_get_fh.return_value = mock_fh

        resp = self.client.get("/api/v1/feedback/stats")
        assert resp.status_code == 200
