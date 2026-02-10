import os
import pickle
from urllib import response
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "faiss_index")
CHUNKS_PATH = os.path.join(VECTORSTORE_DIR, "chunks.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "mtsamples.csv")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME_OLLAMA = "mistral:latest"

MODEL_NAME_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(MODEL_NAME_EMBEDDING)

def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]
    return chunks

def build_vector_store():
    print("Building vector store...")

    df = pd.read_csv(DATA_PATH)

    all_chunks = []
    for text in df["transcription"].dropna():
        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")

    embeddings = embedding_model.encode(
        all_chunks,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(all_chunks, f)

    print("Vector store created successfully.")

def load_vector_store():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        raise RuntimeError(
            "Vector store not found. Run build_index.py before starting API."
        )

    index = faiss.read_index(INDEX_PATH)

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def retrieve_similar_cases(query, k=5):
    index, chunks = load_vector_store()

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, k)

    results = [chunks[i] for i in indices[0]]

    return results

def build_prompt(query, retrieved_chunks):
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are a clinical AI assistant helping doctors review past similar cases.

Use ONLY the provided past medical cases to answer.

Past Cases:
{context}

Doctor Query:
{query}

Instructions:
- Identify similar symptom patterns.
- Summarize relevant findings.
- Give concise and pointwise insights based on past cases.
- Mention possible diagnoses seen in past cases.
- Do NOT hallucinate new medical information.
- If insufficient information, say so clearly.

Response:
"""
    return prompt

def generate_response(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME_OLLAMA,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:

        print(response.status_code)
        print(response.text)
        raise Exception("Error communicating with Ollama")

    return response.json()["response"]

def rag_pipeline(query, index, chunks, k=5):
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, k)

    retrieved_chunks = [chunks[i] for i in indices[0]]

    prompt = build_prompt(query, retrieved_chunks)

    answer = generate_response(prompt)

    return {
        "query": query,
        "retrieved_cases": retrieved_chunks,
        "generated_response": answer
    }

