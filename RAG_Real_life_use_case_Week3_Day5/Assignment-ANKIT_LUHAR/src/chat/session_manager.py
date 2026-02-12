
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

from config.constants import CACHE_PREFIX_SESSION, MAX_SESSIONS_PER_USER, SESSION_EXPIRY_HOURS
from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)


@dataclass
class Session:
    """Represents a chat session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_active: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message_count: int = 0
    metadata: dict = field(default_factory=dict)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_active = datetime.now(timezone.utc).isoformat()
        self.message_count += 1


class SessionManager:
    """Manage chat sessions with optional Redis persistence."""

    def __init__(self, redis_client: Optional[object] = None) -> None:
        self._redis = redis_client
        self._local_sessions: dict[str, Session] = {}
        settings = get_settings()
        self._ttl = SESSION_EXPIRY_HOURS * 3600

    def create_session(self, metadata: Optional[dict] = None) -> Session:
        """Create a new session."""
        session = Session(metadata=metadata or {})

        if self._redis:
            self._save_to_redis(session)
        else:
            self._local_sessions[session.session_id] = session

        logger.info("session_created", session_id=session.session_id)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        if self._redis:
            return self._load_from_redis(session_id)
        return self._local_sessions.get(session_id)

    def update_session(self, session: Session) -> None:
        """Persist updated session state."""
        session.touch()
        if self._redis:
            self._save_to_redis(session)
        else:
            self._local_sessions[session.session_id] = session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if self._redis:
            key = f"{CACHE_PREFIX_SESSION}{session_id}"
            try:
                self._redis.delete(key)  # type: ignore[union-attr]
                logger.info("session_deleted", session_id=session_id)
                return True
            except Exception:
                return False
        else:
            if session_id in self._local_sessions:
                del self._local_sessions[session_id]
                return True
            return False

    def list_sessions(self) -> list[Session]:
        """List all active sessions."""
        if self._redis:
            return self._list_redis_sessions()
        return list(self._local_sessions.values())


    def _save_to_redis(self, session: Session) -> None:
        key = f"{CACHE_PREFIX_SESSION}{session.session_id}"
        try:
            self._redis.setex(key, self._ttl, json.dumps(asdict(session)))  
        except Exception as exc:
            logger.error("session_save_error", error=str(exc))

    def _load_from_redis(self, session_id: str) -> Optional[Session]:
        key = f"{CACHE_PREFIX_SESSION}{session_id}"
        try:
            data = self._redis.get(key)  
            if data:
                return Session(**json.loads(data))
        except Exception as exc:
            logger.error("session_load_error", error=str(exc))
        return None

    def _list_redis_sessions(self) -> list[Session]:
        try:
            pattern = f"{CACHE_PREFIX_SESSION}*"
            keys = self._redis.keys(pattern)  
            sessions = []
            for key in keys:
                data = self._redis.get(key)  
                if data:
                    sessions.append(Session(**json.loads(data)))
            return sessions
        except Exception:
            return []
