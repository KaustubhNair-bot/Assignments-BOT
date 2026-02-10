"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# ============== Authentication Models ==============

class UserCreate(BaseModel):
    """Model for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)
    
class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str

class Token(BaseModel):
    """JWT Token response model"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data encoded in JWT token"""
    username: Optional[str] = None

class UserResponse(BaseModel):
    """User information response (excludes password)"""
    username: str
    full_name: str
    specialty: Optional[str] = None
    created_at: datetime

# ============== Search Models ==============

class SearchQuery(BaseModel):
    """Model for RAG search queries"""
    query: str = Field(..., min_length=3, max_length=500, description="Search query for similar medical cases")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    specialty_filter: Optional[str] = Field(None, description="Filter by medical specialty")

class SearchResult(BaseModel):
    """Individual search result"""
    case_id: str
    specialty: str
    sample_name: str
    transcription: str
    similarity_score: float
    keywords: Optional[str] = None

class SearchResponse(BaseModel):
    """Response containing search results"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float

# ============== LLM Answer Models ==============

class AskQuery(BaseModel):
    """Model for RAG + LLM queries"""
    query: str = Field(..., min_length=3, max_length=500, description="Medical question to answer")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of cases to retrieve for context")
    specialty_filter: Optional[str] = Field(None, description="Filter by medical specialty")

class LLMResponse(BaseModel):
    """Response from LLM (with or without RAG context)"""
    query: str
    answer: str
    model: str
    mode: str  # "rag" or "base_llm"
    llm_time_ms: float
    tokens_used: Dict[str, int]
    num_contexts: int
    retrieved_cases: Optional[List[SearchResult]] = None
    retrieval_time_ms: Optional[float] = None
