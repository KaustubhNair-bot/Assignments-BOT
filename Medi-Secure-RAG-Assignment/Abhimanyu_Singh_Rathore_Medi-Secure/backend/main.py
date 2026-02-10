from fastapi import FastAPI, Depends, HTTPException, Form
from backend.auth import create_access_token, get_current_user
from backend.users import fake_doctors_db, verify_password
from backend.rag import query_rag

app = FastAPI(title="MediSecure RAG API")

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username not in fake_doctors_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, fake_doctors_db[username]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/ask")
def ask(
    question: str = Form(...),
    doctor: str = Depends(get_current_user)
):
    return {
        "doctor": doctor,
        "answer": query_rag(question)
    }
