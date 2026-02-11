"""
DP World RAG Chatbot — Feedback Routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from config.logging_config import get_logger
from src.api.dependencies import get_feedback_handler
from src.api.schemas.common_schemas import APIResponse
from src.api.schemas.feedback_schemas import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackStatsResponse,
)
from src.chat.feedback_handler import FeedbackHandler

logger = get_logger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=APIResponse[FeedbackResponse])
async def submit_feedback(
    request: FeedbackRequest,
    handler: FeedbackHandler = Depends(get_feedback_handler),
) -> APIResponse[FeedbackResponse]:
    """Submit feedback on a chatbot response."""
    try:
        fb = handler.submit_feedback(
            session_id=request.session_id,
            rating=request.rating,
            comment=request.comment or "",
            message_id=request.message_id or "",
        )
        return APIResponse(
            success=True,
            data=FeedbackResponse(feedback_id=fb.feedback_id),
        )
    except Exception as exc:
        logger.error("feedback_error", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/stats", response_model=APIResponse[FeedbackStatsResponse])
async def get_feedback_stats(
    handler: FeedbackHandler = Depends(get_feedback_handler),
) -> APIResponse[FeedbackStatsResponse]:
    """Get aggregate feedback statistics."""
    stats = handler.get_feedback_stats()
    return APIResponse(
        success=True,
        data=FeedbackStatsResponse(**stats),
    )
