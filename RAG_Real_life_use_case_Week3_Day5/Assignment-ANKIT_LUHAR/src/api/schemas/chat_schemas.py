"""
DP World RAG Chatbot — Chat API Schemas.

Request/response models for chat endpoints.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    message: str = Field(
        ..., min_length=1, max_length=2000,
        description="User message",
        examples=["What services does DP World offer?"],
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Existing session ID; omit to start a new session",
    )
    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Generation temperature (0.0=factual, 0.8=creative)",
    )
    top_p: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Nucleus sampling parameter",
    )


class RetrievedChunk(BaseModel):
    """A single retrieved chunk shown to the user for verification."""

    text: str = ""
    score: float = 0.0
    source: str = ""
    title: str = ""


class GenerationParams(BaseModel):
    """Generation parameters used for this response."""

    temperature: Optional[float] = None
    top_p: Optional[float] = None
    model: str = ""
    blocked: bool = False


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    message_id: str
    response: str
    sources: list[str] = []
    session_id: str
    retrieved_chunks: list[RetrievedChunk] = []
    generation_params: Optional[GenerationParams] = None


class SessionResponse(BaseModel):
    """Response for session creation."""

    session_id: str
    message: str


class HistoryItem(BaseModel):
    """Single message in the history."""

    role: str
    content: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    """Response with full chat history."""

    session_id: str
    messages: list[HistoryItem] = []
    total: int = 0
