from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import pandas as pd
import hashlib
import secrets
from typing import List, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import config
from app.config import settings

app = FastAPI(title="Hospital RAG API", description="Simple medical search API")

# JWT Authentication
security = HTTPBearer()

# Simple user database (with hashed passwords)
USERS = {
    "doctor": {
        "password_hash": hashlib.sha256("doctor123".encode()).hexdigest(),
        "name": "Dr. Smith"
    },
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "Administrator"
    }
}

# Load medical data on startup
MEDICAL_DATA = None

def load_medical_data():
    """Load medical transcriptions from CSV"""
    global MEDICAL_DATA
    try:
        df = pd.read_csv(Path(__file__).parent.parent / "data" / "mtsamples.csv")
        MEDICAL_DATA = df
        print(f"✅ Loaded {len(df)} medical transcriptions")
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    text: str
    similarity: float
    medical_specialty: str
    description: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if username not in USERS:
        raise credentials_exception
    
    return username

def simple_search(query: str, limit: int = 5):
    """Simple keyword search (fallback when embeddings not ready)"""
    if MEDICAL_DATA is None:
        return []
    
    results = []
    query_lower = query.lower()
    
    for idx, row in MEDICAL_DATA.iterrows():
        if pd.notna(row['transcription']):
            transcription = str(row['transcription']).lower()
            
            # Simple keyword matching
            if query_lower in transcription:
                # Calculate simple similarity based on keyword frequency
                word_count = transcription.count(query_lower)
                similarity = min(word_count * 0.1, 1.0)
                
                results.append({
                    'text': str(row['transcription']),
                    'similarity': similarity,
                    'medical_specialty': row.get('medical_specialty', 'Unknown'),
                    'description': row.get('description', 'No description')
                })
                
                if len(results) >= limit:
                    break
    
    return results

@app.on_event("startup")
async def startup_event():
    """Setup on startup"""
    load_medical_data()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hospital RAG API", "status": "ready", "data_loaded": MEDICAL_DATA is not None}

@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """JWT login endpoint"""
    username = login_data.username
    password = login_data.password
    
    if username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, USERS[username]["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": username
    }

@app.post("/test_search")
async def test_search(query: str = "chest pain", limit: int = 3):
    """Test search endpoint"""
    return simple_search(query, limit)

@app.post("/search")
async def search_medical(request: SearchRequest, current_user: str = Depends(get_current_user)):
    """Search medical transcriptions with JWT auth"""
    if MEDICAL_DATA is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Use simple search for now (can be upgraded to embeddings later)
    results = simple_search(request.query, request.limit)
    
    if not results:
        # If no exact matches, try partial matches
        results = []
        query_words = request.query.lower().split()
        
        for idx, row in MEDICAL_DATA.iterrows():
            if pd.notna(row['transcription']):
                transcription = str(row['transcription']).lower()
                
                # Check if any query words are in the transcription
                matches = sum(1 for word in query_words if word in transcription)
                if matches > 0:
                    similarity = matches / len(query_words)
                    
                    results.append({
                        'text': str(row['transcription']),
                        'similarity': similarity,
                        'medical_specialty': row.get('medical_specialty', 'Unknown'),
                        'description': row.get('description', 'No description')
                    })
                    
                    if len(results) >= request.limit:
                        break
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:request.limit]
    
    return results

@app.get("/stats")
async def get_stats(current_user: str = Depends(get_current_user)):
    """Get system statistics with JWT auth"""
    if MEDICAL_DATA is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {
        "total_transcriptions": len(MEDICAL_DATA),
        "medical_specialties": MEDICAL_DATA['medical_specialty'].value_counts().to_dict(),
        "user": current_user,
        "search_type": "keyword_search"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
