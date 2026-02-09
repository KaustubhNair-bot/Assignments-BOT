"""
MediCure RAG System - FastAPI Backend
A secure API for medical transcription search with JWT authentication
All data processing happens locally - no patient data leaves the system
"""
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    UserCreate, Token, UserResponse,
    SearchQuery, SearchResponse
)
from app.auth import (
    create_access_token, authenticate_user, create_user,
    get_current_user, create_demo_users
)
from app.rag_engine import rag_engine
from app.database import mongodb

# Initialize FastAPI app
app = FastAPI(
    title="MediCure RAG API",
    description="""
    Secure RAG API for medical transcription search.
    
    ## Features
    - **Semantic Search**: Find similar medical cases using AI
    - **JWT Authentication**: Secure access for authorized doctors
    - **Local Processing**: All data stays on-premises
    """,
    version="1.0.0"
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
    
    # Connect to MongoDB
    mongodb.connect()
    
    # Create demo users
    create_demo_users()
    
    # Initialize RAG engine
    rag_engine.initialize()
    
    print("MediCure RAG API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    mongodb.close()


# ============== Health Check ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = rag_engine.get_stats()
    return {
        "status": "healthy",
        "rag_engine": stats
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


# ============== RAG Search ==============

@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_cases(
    query: SearchQuery,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Search for similar medical cases using RAG.
    
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


@app.get("/specialties", response_model=list[str], tags=["Search"])
async def get_specialties(current_user: UserResponse = Depends(get_current_user)):
    """Get list of available medical specialties"""
    return rag_engine.get_specialties()


@app.get("/stats", tags=["System"])
async def get_system_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get system statistics"""
    return rag_engine.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
