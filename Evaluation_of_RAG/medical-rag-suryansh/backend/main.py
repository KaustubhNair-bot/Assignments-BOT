from fastapi import FastAPI, Header
from backend.auth import authenticate, create_token, verify_token
from backend.rag import get_retrieved_texts, rag_with_llm, compare_models

app = FastAPI()


#login
@app.post("/login")
def login(data: dict):

    user  = data.get("username")
    pwd = data.get("password")

    if not authenticate(user, pwd):
        return {"error": "Invalid credentials"}
    
    return {"token": create_token(user)}



# simple retrival
@app.get("/search")
def rag(query:str, token: str = Header()):

    try:
        verify_token(token)
    except Exception as e:
        return {"error": "Unauthorized access"}

    results = get_retrieved_texts(query)

    return {"results": results}

# full RAG + LLM
@app.get("/ask")
def ask(query:str, token: str = Header()):

    try:
        verify_token(token)
    except Exception:
        return {"error": "Unauthorized access"}

    return rag_with_llm(query)

# comparison API
@app.get("/compare")
def compare(query:str, token: str = Header()):

    try:
        verify_token(token)
    except Exception:
        return {"error": "Unauthorized access"}

    return compare_models(query)
