"""FastAPI application — Medical RAG System backend.

Endpoints
---------
POST /token          – Obtain JWT access token
POST /signup         – Create a new user account
GET  /users/me/      – Get current user info
POST /search         – Semantic search through patient cases
POST /generate       – RAG-powered answer generation (search + LLM)
POST /base-generate  – Base LLM answer (no retrieval) — for comparison
POST /upload         – Add a new case to the knowledge base
POST /load-data      – Admin: bulk-load the CSV dataset
"""

from __future__ import annotations

from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import auth, database, models, rag_system
from .database import engine

# ---------------------------------------------------------------------------
# Initialise database tables
# ---------------------------------------------------------------------------
database.Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Medical RAG System",
    description="RAG-powered patient case search with JWT authentication",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
@app.post("/token", response_model=models.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(database.UserDB)
        .filter(database.UserDB.username == form_data.username)
        .first()
    )

    # Auto-create default admin on first login
    if not user:
        if form_data.username == "admin" and form_data.password == "admin":
            hashed = auth.get_password_hash("admin")
            user = database.UserDB(username="admin", hashed_password=hashed)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup", response_model=models.User)
async def create_user(user: models.UserSignup, db: Session = Depends(get_db)):
    existing = (
        db.query(database.UserDB)
        .filter(database.UserDB.username == user.username)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = auth.get_password_hash(user.password)
    db_user = database.UserDB(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------------------------------------------------------------------------
# User info
# ---------------------------------------------------------------------------
@app.get("/users/me/", response_model=models.User)
async def read_users_me(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = auth.jwt.decode(
            token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        user = (
            db.query(database.UserDB)
            .filter(database.UserDB.username == username)
            .first()
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# ---------------------------------------------------------------------------
# Search & Generate endpoints
# ---------------------------------------------------------------------------
@app.post("/search", response_model=List[models.SearchResult])
async def search_cases(
    query: models.SearchQuery,
    current_user: models.User = Depends(read_users_me),
):
    docs = rag_system.rag.search(query.query, k=query.top_k)
    results = []
    for doc in docs:
        results.append(
            models.SearchResult(
                transcription=doc.page_content,
                metadata=getattr(doc, "metadata", {}),
                score=0.9,
            )
        )
    return results


@app.post("/generate", response_model=models.GenerateResponse)
async def generate_rag_answer(
    query: models.SearchQuery,
    current_user: models.User = Depends(read_users_me),
):
    """RAG pipeline: retrieve context docs → generate grounded answer."""
    docs = rag_system.rag.search(query.query, k=query.top_k)
    answer = rag_system.rag.generate_answer(query.query, docs)
    sources = [doc.page_content[:200] + "…" for doc in docs]
    return models.GenerateResponse(
        answer=answer,
        sources=sources,
        num_sources=len(docs),
    )


@app.post("/base-generate", response_model=models.GenerateResponse)
async def generate_base_answer(
    query: models.SearchQuery,
    current_user: models.User = Depends(read_users_me),
):
    """Base LLM generation WITHOUT retrieval — for comparison."""
    answer = rag_system.rag.generate_base_answer(query.query)
    return models.GenerateResponse(
        answer=answer,
        sources=[],
        num_sources=0,
    )


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
@app.post("/upload")
async def upload_case(
    case: models.CaseUpload,
    current_user: models.User = Depends(read_users_me),
):
    metadata = {
        "medical_specialty": case.specialty,
        "keywords": case.keywords,
        "uploaded_by": current_user.username,
    }
    success = rag_system.rag.add_document(case.transcription, metadata)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to index document")
    return {"status": "Case uploaded and indexed successfully"}


# ---------------------------------------------------------------------------
# Admin: bulk data load
# ---------------------------------------------------------------------------
@app.post("/load-data")
async def trigger_load_data(
    current_user: models.User = Depends(read_users_me),
):
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    from .data_loader import load_data

    try:
        load_data()
        return {"status": "Data loaded successfully"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
