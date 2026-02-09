from fastapi import FastAPI, Header
from backend.auth import authenticate, create_token, verify_token
from backend.rag import search

app = FastAPI()

@app.post("/login")
def login(data: dict):
    user  = data.get("username")
    pwd = data.get("password")

    if not authenticate(user, pwd):
        return {"error": "Invalid credentials"}
    
    return {"token": create_token(user)}

@app.get("/search")
def rag(query:str,token: str = Header()):
    try:
        verify_token(token) # Verify the provided token; Raises error if token is invalid or expired
    except Exception as e:
        return {"error": "Unauthorized access"}

    results = search(query) # Perform RAG search using the provided query and return results
    return {"results": results}