from fastapi import FastAPI,Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from db import init_db
from auth import hash_password, verify_password, create_access_token,get_current_user
from rag import rag_pipeline,load_vector_store
from contextlib import asynccontextmanager
import sqlite3

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    print("Database initialized")
    app.state.index, app.state.metadata, app.state.bm25 = load_vector_store()
    yield

    # Shutdown logic (optional)
    print("Application shutting down")


app = FastAPI(
    title="MediSecure RAG API",
    lifespan=lifespan
)
@app.get("/")
def root():
    return {"message": "MediSecure API Running"}

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("medisecure.db")
    cursor = conn.cursor()

    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO doctors (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
    except:
        raise HTTPException(status_code=400, detail="User already exists")

    finally:
        conn.close()

    return {"message": "Doctor registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = sqlite3.connect("medisecure.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM doctors WHERE username = ?",
        (form_data.username,)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, user[0]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": form_data.username})

    return {"access_token": token, "token_type": "bearer"}

@app.post("/rag")
def secure_rag(
    query: str = Form(...),
    current_user: str = Depends(get_current_user)
):
    return rag_pipeline(
    query,
    app.state.index,
    app.state.metadata,
    app.state.bm25
)