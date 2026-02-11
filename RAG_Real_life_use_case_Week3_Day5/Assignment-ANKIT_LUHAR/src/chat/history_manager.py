"""
DP World RAG Chatbot — History Manager.

Manages per-session conversation history with a sliding window.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

from config.constants import ASSISTANT_ROLE, MAX_HISTORY_TURNS, USER_ROLE
from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ChatMessage:
    """A single message in the conversation."""

    role: str  # "user" | "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = field(default_factory=dict)


class HistoryManager:
    """Manage conversation history for a session."""

    def __init__(
        self,
        max_turns: int = MAX_HISTORY_TURNS,
        redis_client: Optional[object] = None,
    ) -> None:
        self.max_turns = max_turns
        self._redis = redis_client
        self._local_store: dict[str, list[ChatMessage]] = {}

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[dict] = None) -> None:
        """Add a message to the session history."""
        msg = ChatMessage(role=role, content=content, metadata=metadata or {})
        history = self._get_history(session_id)
        history.append(msg)

        # Enforce sliding window
        if len(history) > self.max_turns * 2:
            history = history[-(self.max_turns * 2) :]

        self._set_history(session_id, history)

    def get_history(self, session_id: str) -> list[ChatMessage]:
        """Get the full history for a session."""
        return self._get_history(session_id)

    def get_formatted_history(self, session_id: str, last_n: Optional[int] = None) -> str:
        """Get history formatted as a string for prompt injection."""
        history = self._get_history(session_id)
        if last_n:
            history = history[-last_n * 2 :]

        if not history:
            return ""

        parts = []
        for msg in history:
            role_label = "User" if msg.role == USER_ROLE else "Assistant"
            parts.append(f"{role_label}: {msg.content}")

        return "\n".join(parts)

    def get_messages_for_llm(self, session_id: str) -> list[dict[str, str]]:
        """Get history as OpenAI-style message dicts for LLM input."""
        history = self._get_history(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in history]

    def clear_history(self, session_id: str) -> None:
        """Clear all history for a session."""
        self._set_history(session_id, [])
        logger.info("history_cleared", session_id=session_id)

    def get_last_user_query(self, session_id: str) -> Optional[str]:
        """Get the last user message from history."""
        history = self._get_history(session_id)
        for msg in reversed(history):
            if msg.role == USER_ROLE:
                return msg.content
        return None

    # ── Storage ─────────────────────────────────────────────
    def _get_history(self, session_id: str) -> list[ChatMessage]:
        if self._redis:
            return self._load_redis(session_id)
        return self._local_store.get(session_id, [])

    def _set_history(self, session_id: str, history: list[ChatMessage]) -> None:
        if self._redis:
            self._save_redis(session_id, history)
        else:
            self._local_store[session_id] = history

    def _load_redis(self, session_id: str) -> list[ChatMessage]:
        key = f"dpw:history:{session_id}"
        try:
            data = self._redis.get(key)  # type: ignore[union-attr]
            if data:
                return [ChatMessage(**m) for m in json.loads(data)]
        except Exception:
            pass
        return []

    def _save_redis(self, session_id: str, history: list[ChatMessage]) -> None:
        key = f"dpw:history:{session_id}"
        try:
            data = json.dumps([asdict(m) for m in history])
            self._redis.setex(key, 86400, data)  # type: ignore[union-attr]
        except Exception as exc:
            logger.error("history_save_error", error=str(exc))
