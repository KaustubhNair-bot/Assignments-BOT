import os
import requests
import json
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- Paths & Config ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# Ensure this URL is exactly as shown below
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_DIR)

try:
    collection = client.get_collection("medical_notes")
except Exception:
    collection = None

def query_rag(question: str):
    if collection is None:
        return "Database not initialized. Please run ingest.py first."

    # 1. Search for context
    q_emb = model.encode(question).tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    docs = results.get("documents", [[]])[0]
    
    context = "\n\n".join(docs) if docs else "No relevant cases found."

    # 2. Build the Prompt
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"

    # 3. Request to Ollama
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False  
    }

    try:
        # We send the POST request to the FULL URL (including /api/generate)
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        
        if response.status_code == 405:
            return "Error 405: Check if OLLAMA_URL in .env ends with /api/generate"
            
        response.raise_for_status()
        return response.json().get("response", "No response text found.")
        
    except requests.exceptions.RequestException as e:
        return f"Connection Error: Is Ollama running? {str(e)}"