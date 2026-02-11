"""Pydantic data models for request/response validation."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Auth models
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class UserSignup(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ---------------------------------------------------------------------------
# Search / RAG models
# ---------------------------------------------------------------------------
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    transcription: str
    metadata: dict
    score: float


class GenerateResponse(BaseModel):
    """Response from /generate and /base-generate endpoints."""
    answer: str
    sources: List[str] = []
    num_sources: int = 0


# ---------------------------------------------------------------------------
# Upload model
# ---------------------------------------------------------------------------
class CaseUpload(BaseModel):
    transcription: str
    specialty: str = "General"
    keywords: str = ""
