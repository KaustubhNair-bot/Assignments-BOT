"""
DP World RAG Chatbot — Feedback API Schemas.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Request body for submitting feedback."""

    session_id: str = Field(..., description="Session the feedback belongs to")
    rating: int = Field(..., ge=-1, le=5, description="Rating: -1/+1 thumbs, or 1-5 stars")
    comment: Optional[str] = Field(default="", max_length=1000, description="Optional comment")
    message_id: Optional[str] = Field(default="", description="ID of the message being rated")


class FeedbackResponse(BaseModel):
    """Response after feedback submission."""

    feedback_id: str
    message: str = "Thank you for your feedback!"


class FeedbackStatsResponse(BaseModel):
    """Aggregate feedback statistics."""

    total: int = 0
    average_rating: float = 0
    positive: int = 0
    negative: int = 0
