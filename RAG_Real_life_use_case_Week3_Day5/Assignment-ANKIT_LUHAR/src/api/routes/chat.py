"""
DP World RAG Chatbot — Chat API Routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from config.logging_config import get_logger
from src.api.dependencies import get_chat_manager
from src.api.schemas.chat_schemas import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    GenerationParams,
    HistoryItem,
    RetrievedChunk,
    SessionResponse,
)
from src.api.schemas.common_schemas import APIResponse
from src.chat.chat_manager import ChatManager
from src.utils.metrics import MetricsCollector

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])
metrics = MetricsCollector()


@router.post("/", response_model=APIResponse[ChatResponse])
async def send_message(
    request: ChatRequest,
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> APIResponse[ChatResponse]:
    """Send a message and receive a RAG-powered response."""
    metrics.increment("chat_requests")

    with metrics.timer("chat_latency"):
        try:
            # Start new session if none provided
            session_id = request.session_id
            if not session_id:
                session_data = await chat_manager.start_session()
                session_id = session_data["session_id"]

            result = await chat_manager.chat(
                session_id=session_id,
                user_message=request.message,
                temperature=request.temperature,
                top_p=request.top_p,
            )

            # Build retrieved chunks for UI display
            chunks = [
                RetrievedChunk(**c) for c in result.get("retrieved_chunks", [])
            ]
            gen_params = GenerationParams(
                **result.get("generation_params", {})
            )

            return APIResponse(
                success=True,
                data=ChatResponse(
                    message_id=result["message_id"],
                    response=result["response"],
                    sources=result["sources"],
                    session_id=result["session_id"],
                    retrieved_chunks=chunks,
                    generation_params=gen_params,
                ),
                message="Response generated successfully",
            )

        except Exception as exc:
            logger.error("chat_endpoint_error", error=str(exc))
            metrics.increment("chat_errors")
            raise HTTPException(status_code=500, detail=str(exc))


@router.post("/session", response_model=APIResponse[SessionResponse])
async def create_session(
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> APIResponse[SessionResponse]:
    """Create a new chat session."""
    result = await chat_manager.start_session()
    return APIResponse(
        success=True,
        data=SessionResponse(
            session_id=result["session_id"],
            message=result["message"],
        ),
    )


@router.get("/history/{session_id}", response_model=APIResponse[ChatHistoryResponse])
async def get_history(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> APIResponse[ChatHistoryResponse]:
    """Get chat history for a session."""
    history = await chat_manager.get_history(session_id)
    return APIResponse(
        success=True,
        data=ChatHistoryResponse(
            session_id=session_id,
            messages=[HistoryItem(**m) for m in history],
            total=len(history),
        ),
    )


@router.delete("/session/{session_id}", response_model=APIResponse)
async def delete_session(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> APIResponse:
    """Delete a chat session and its history."""
    success = await chat_manager.clear_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return APIResponse(success=True, message="Session deleted")
