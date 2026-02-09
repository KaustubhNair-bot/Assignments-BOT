from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from . import auth, models, database, rag_system
from .database import engine

# Create tables
database.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical RAG System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user (simplified logic for demo - user needs to be created first or use a hardcoded one)
    # For this demo, we'll create a user on the fly if it doesn't exist matching "admin"
    user = db.query(database.UserDB).filter(database.UserDB.username == form_data.username).first()
    
    if not user:
        if form_data.username == "admin" and form_data.password == "admin":
             # Create default admin
            hashed_pw = auth.get_password_hash("admin")
            user = database.UserDB(username="admin", hashed_password=hashed_pw)
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
        
    access_token_expires = timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=models.User)
async def read_users_me(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    # In a full app, we would validate token and fetch user
    # simplified:
    try:
        payload = auth.jwt.decode(token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM])
        username: str = payload.get("sub")
        user = db.query(database.UserDB).filter(database.UserDB.username == username).first()
        if user is None:
             raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
         raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/search", response_model=List[models.SearchResult])
async def search_cases(query: models.SearchQuery, current_user: models.User = Depends(read_users_me)):
    docs = rag_system.rag.search(query.query, k=query.top_k)
    results = []
    for doc in docs:
        results.append(models.SearchResult(
            transcription=doc.page_content,
            metadata=doc.metadata,
            score=0.9 # Placeholder as LangChain generic search might not return score directly in all methods
        ))
    return results

@app.post("/signup", response_model=models.User)
async def create_user(user: models.UserSignup, db: Session = Depends(get_db)):
    db_user = db.query(database.UserDB).filter(database.UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = database.UserDB(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/upload")
async def upload_case(case: models.CaseUpload, current_user: models.User = Depends(read_users_me)):
    metadata = {
        "medical_specialty": case.specialty,
        "keywords": case.keywords,
        "uploaded_by": current_user.username
    }
    success = rag_system.rag.add_document(case.transcription, metadata)
    if not success:
         raise HTTPException(status_code=500, detail="Failed to index document")
    return {"status": "Case uploaded and indexed successfully"}

# Optional: Endpoint to trigger data loading
@app.post("/load-data")
async def trigger_load_data(current_user: models.User = Depends(read_users_me)):
    if current_user.username != "admin": # Simple check
        raise HTTPException(status_code=403, detail="Not authorized")
    from .data_loader import load_data
    try:
        load_data()
        return {"status": "Data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
