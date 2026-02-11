import os
import requests
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuration ---
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize only the embedding model
embed_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection("medical_notes_domain")

def query_rag(question: str):
    # 1. Direct Retrieval: Fetch top 3 results based on similarity
    query_embedding = embed_model.embed_query(question)
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=3 
    )
    top_chunks = results["documents"][0]
    
    context = "\n\n".join(top_chunks) if top_chunks else "No relevant medical records found."

    # 2. LLM Generation: Augment the prompt with retrieved context
    prompt = f"""
    You are a medical assistant. Strictly use the following context to answer the clinical query.
    If the context doesn't contain the answer, say 'I don't know based on the records.'
    
    Medical Context: {context}
    
    Clinical Query: {question}
    
    Answer:"""
    
    payload = {"model": "mistral", "prompt": prompt, "stream": False}
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        return response.json().get("response")
    except Exception as e:
        return f"Error: {str(e)}"