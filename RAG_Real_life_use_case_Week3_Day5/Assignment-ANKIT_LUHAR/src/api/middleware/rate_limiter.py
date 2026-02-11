"""
DP World RAG Chatbot — Rate Limiter Middleware.

Uses slowapi for request rate limiting.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config.settings import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{settings.rate_limit_requests}/{settings.rate_limit_window_seconds}seconds"
    ],
)
