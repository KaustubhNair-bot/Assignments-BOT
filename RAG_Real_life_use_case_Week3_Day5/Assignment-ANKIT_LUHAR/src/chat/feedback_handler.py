

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Feedback:
    """User feedback on a chatbot response."""

    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    message_id: str = ""
    rating: int = 0  
    comment: str = ""
    query: str = ""
    response: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FeedbackHandler:
    """Collect and persist user feedback."""

    def __init__(
        self,
        storage_path: str = "data/feedback",
        redis_client: Optional[object] = None,
    ) -> None:
        self._storage_path = Path(storage_path)
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._redis = redis_client
        self._feedback_file = self._storage_path / "feedback.jsonl"

    def submit_feedback(
        self,
        session_id: str,
        rating: int,
        comment: str = "",
        query: str = "",
        response: str = "",
        message_id: str = "",
    ) -> Feedback:
        """Submit user feedback."""
        fb = Feedback(
            session_id=session_id,
            message_id=message_id,
            rating=rating,
            comment=comment,
            query=query,
            response=response,
        )

        self._persist(fb)
        logger.info(
            "feedback_submitted",
            feedback_id=fb.feedback_id,
            session_id=session_id,
            rating=rating,
        )
        return fb

    def get_feedback_stats(self) -> dict:
        """Get aggregate feedback statistics."""
        all_fb = self._load_all()
        if not all_fb:
            return {"total": 0, "average_rating": 0, "positive": 0, "negative": 0}

        ratings = [f.rating for f in all_fb if f.rating != 0]
        return {
            "total": len(all_fb),
            "average_rating": round(sum(ratings) / max(len(ratings), 1), 2),
            "positive": sum(1 for r in ratings if r > 0),
            "negative": sum(1 for r in ratings if r < 0),
        }

    def _persist(self, feedback: Feedback) -> None:
        """Append feedback to JSONL file."""
        try:
            with open(self._feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(feedback)) + "\n")
        except Exception as exc:
            logger.error("feedback_persist_error", error=str(exc))

    def _load_all(self) -> list[Feedback]:
        """Load all feedback from disk."""
        if not self._feedback_file.exists():
            return []
        feedbacks = []
        try:
            with open(self._feedback_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        feedbacks.append(Feedback(**json.loads(line)))
        except Exception as exc:
            logger.error("feedback_load_error", error=str(exc))
        return feedbacks
