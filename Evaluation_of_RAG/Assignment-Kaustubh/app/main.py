"""
MediCure RAG System - FastAPI Backend
A secure API for medical transcription search with JWT authentication
Integrates FAISS-based RAG with Groq LLM for natural language answers
"""
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    UserCreate, Token, UserResponse,
    SearchQuery, SearchResponse, AskQuery, LLMResponse
)
from app.auth import (
    create_access_token, authenticate_user, create_user,
    get_current_user, create_demo_users
)
from app.rag_engine import rag_engine
from app.llm_engine import llm_engine

# Initialize FastAPI app
app = FastAPI(
    title="MediCure RAG API",
    description="""
    Secure RAG API for medical transcription search with LLM-powered answers.
    
    ## Features
    - **Semantic Search**: Find similar medical cases using FAISS
    - **RAG + LLM**: Get natural language answers grounded in retrieved cases
    - **Base LLM**: Compare with answers without retrieval context
    - **JWT Authentication**: Secure access for authorized doctors
    - **Local Embeddings**: All vectorization stays on-premises
    """,
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Starting MediCure RAG API...")
    
    # Create demo users
    create_demo_users()
    
    # Initialize RAG engine
    rag_engine.initialize()
    
    # Initialize LLM engine
    llm_engine.initialize()
    
    print("MediCure RAG API ready!")


# ============== Health Check ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = rag_engine.get_stats()
    return {
        "status": "healthy",
        "rag_engine": stats,
        "llm_available": llm_engine.is_available(),
        "llm_model": settings.GROQ_MODEL if llm_engine.is_available() else None
    }


# ============== Authentication ==============

@app.post("/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(user_data: UserCreate):
    """Register a new doctor account"""
    return create_user(user_data)


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get JWT access token.
    
    Demo accounts: dr.smith/doctor123, dr.jones/doctor123, dr.patel/doctor123
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.get("username", form_data.username)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


# ============== RAG Search (Retrieval Only) ==============

@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_cases(
    query: SearchQuery,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Search for similar medical cases using semantic search (retrieval only).
    
    **Requires authentication.**
    """
    try:
        return rag_engine.search(
            query=query.query,
            top_k=query.top_k,
            specialty_filter=query.specialty_filter
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


# ============== RAG + LLM (Full Pipeline) ==============

@app.post("/ask", response_model=LLMResponse, tags=["RAG + LLM"])
async def ask_rag(
    query: AskQuery,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Ask a medical question and get an LLM-generated answer grounded in retrieved cases.
    
    This is the full RAG pipeline:
    1. Retrieve similar cases from FAISS
    2. Pass retrieved cases as context to the LLM
    3. LLM generates a natural language answer based on the context
    
    **Requires authentication.**
    """
    if not llm_engine.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Set GROQ_API_KEY in .env"
        )
    
    try:
        # Step 1: Retrieve relevant cases
        search_response = rag_engine.search(
            query=query.query,
            top_k=query.top_k,
            specialty_filter=query.specialty_filter
        )
        
        # Step 2: Prepare contexts for LLM
        contexts = []
        for result in search_response.results:
            contexts.append({
                "case_id": result.case_id,
                "specialty": result.specialty,
                "sample_name": result.sample_name,
                "transcription": result.transcription,
                "similarity_score": result.similarity_score
            })
        
        # Step 3: Generate answer with LLM
        llm_result = llm_engine.generate_rag_answer(
            query=query.query,
            retrieved_contexts=contexts
        )
        
        if "error" in llm_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=llm_result["error"]
            )
        
        return LLMResponse(
            query=query.query,
            answer=llm_result["answer"],
            model=llm_result["model"],
            mode="rag",
            llm_time_ms=llm_result["llm_time_ms"],
            tokens_used=llm_result["tokens_used"],
            num_contexts=llm_result["num_contexts"],
            retrieved_cases=search_response.results,
            retrieval_time_ms=search_response.search_time_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG+LLM error: {str(e)}"
        )


# ============== Base LLM (No Context - For Comparison) ==============

@app.post("/ask-base", response_model=LLMResponse, tags=["RAG + LLM"])
async def ask_base_llm(
    query: AskQuery,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Ask a medical question and get an answer from the base LLM WITHOUT any retrieved context.
    
    This endpoint is for comparison purposes to demonstrate the value of RAG.
    The LLM answers purely from its training data.
    
    **Requires authentication.**
    """
    if not llm_engine.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Set GROQ_API_KEY in .env"
        )
    
    try:
        llm_result = llm_engine.generate_base_answer(query=query.query)
        
        if "error" in llm_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=llm_result["error"]
            )
        
        return LLMResponse(
            query=query.query,
            answer=llm_result["answer"],
            model=llm_result["model"],
            mode="base_llm",
            llm_time_ms=llm_result["llm_time_ms"],
            tokens_used=llm_result["tokens_used"],
            num_contexts=0,
            retrieved_cases=None,
            retrieval_time_ms=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Base LLM error: {str(e)}"
        )


@app.get("/specialties", response_model=list[str], tags=["Search"])
async def get_specialties(current_user: UserResponse = Depends(get_current_user)):
    """Get list of available medical specialties"""
    return rag_engine.get_specialties()


@app.get("/stats", tags=["System"])
async def get_system_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get system statistics"""
    stats = rag_engine.get_stats()
    stats["llm_available"] = llm_engine.is_available()
    stats["llm_model"] = settings.GROQ_MODEL if llm_engine.is_available() else None
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
