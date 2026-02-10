import os
import pickle
from urllib import response
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import requests
from rank_bm25 import BM25Okapi
from sklearn.preprocessing import minmax_scale

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "faiss_index")
CHUNKS_PATH = os.path.join(VECTORSTORE_DIR, "chunks.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "mtsamples.csv")
BM25_PATH = os.path.join(VECTORSTORE_DIR, "bm25.pkl")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME_OLLAMA = "mistral:latest"

MODEL_NAME_EMBEDDING = "sentence-transformers/all-mpnet-base-v2"
embedding_model = SentenceTransformer(MODEL_NAME_EMBEDDING)

def recursive_chunk(text, chunk_size=250, overlap=50):
    words = text.split()

    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break

        start += chunk_size - overlap

    return chunks

def build_vector_store():
    print("Building upgraded vector store...")

    df = pd.read_csv(DATA_PATH)

    # Remove missing values
    df = df.dropna(subset=["transcription"])

    # Remove duplicate medical notes
    df = df.drop_duplicates(subset=["transcription"])

    df = df.reset_index(drop=True)

    all_chunks = []
    metadata = []

    for doc_id, text in enumerate(df["transcription"]):
        chunks = recursive_chunk(text)

        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({
                "doc_id": doc_id,
                "text": chunk
            })

    print(f"Total chunks: {len(all_chunks)}")

    # Dense embeddings
    embeddings = embedding_model.encode(
        all_chunks,
        batch_size=16,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    dimension = embeddings.shape[1]

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(metadata, f)

    # BM25 (Lexical)
    tokenized_corpus = [chunk.split() for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    with open(BM25_PATH, "wb") as f:
        pickle.dump(bm25, f)

    print("New vector store created successfully.")

def load_vector_store():
    if not os.path.exists(INDEX_PATH):
        raise RuntimeError("Vector store not found. Run build_index.py first.")

    index = faiss.read_index(INDEX_PATH)

    with open(CHUNKS_PATH, "rb") as f:
        metadata = pickle.load(f)

    with open(BM25_PATH, "rb") as f:
        bm25 = pickle.load(f)

    return index, metadata, bm25

def hybrid_retrieve(query, index, metadata, bm25, k=5, alpha=0.6):

    # Dense retrieval
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    dense_scores, dense_indices = index.search(query_embedding, k * 3)

    dense_scores = dense_scores[0]
    dense_indices = dense_indices[0]

    # BM25 retrieval
    bm25_scores = bm25.get_scores(query.split())
    bm25_scores = minmax_scale(bm25_scores)

    # Combine scores
    combined_scores = []

    for idx in range(len(metadata)):
        dense_score = 0
        if idx in dense_indices:
            dense_score = dense_scores[list(dense_indices).index(idx)]

        lexical_score = bm25_scores[idx]

        score = alpha * dense_score + (1 - alpha) * lexical_score
        combined_scores.append((idx, score))

    combined_scores.sort(key=lambda x: x[1], reverse=True)

    top_k = combined_scores[:k]

    results = [metadata[idx]["text"] for idx, _ in top_k]

    return results


def build_prompt(query, retrieved_chunks):
    # Format cases as bullet points
    cases_formatted = ""
    for i, chunk in enumerate(retrieved_chunks, 1):
        cases_formatted += f"• Case {i}:\n{chunk}\n\n"

   
    prompt = f"""
You are a clinical AI assistant helping doctors review past similar cases.

Use ONLY the provided past medical case excerpts to answer.
Multiple excerpts may belong to the same patient — identify and group them correctly.
Determine the actual number of unique patient cases based on content, NOT the number of excerpts.

Past Similar Case Excerpts:
{cases_formatted}

Doctor Query:
{query}

Instructions:

1. Identify unique patient cases from the excerpts.
2. Group excerpts that belong to the same patient.
3. Determine the correct total number of distinct cases.
4. Present output in a clear, structured, bullet-point format.

Structure your response exactly as follows:

Summary of Similar Cases:
- Case 1: [Brief structured summary]
- Case 2: [Brief structured summary]
- Case N: [Brief structured summary]

(Only list as many cases as truly exist.)

Likely Diagnoses (based strictly on the cases above):
- [Diagnosis 1] — observed in Case(s) X
- [Diagnosis 2] — observed in Case(s) X, Y

Medical Reasoning:
- Common symptom patterns across cases
- Key clinical findings
- Clinical patterns relevant to the doctor's query
- Suggested next steps based only on past cases

Important Rules:
- Do NOT hallucinate medical facts.
- Do NOT invent new diagnoses.
- Do NOT assume number of cases equals number of excerpts.
- Only use information explicitly present in the provided cases.
- If cases are insufficient to answer confidently, state: 
  "Insufficient similar cases available."

Keep the response concise, structured, and clinically professional.
"""

    return prompt

def generate_response(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME_OLLAMA,
            "prompt": prompt,
            "temperature": 0.0,  
            "max_tokens": 300,
            "stream": False
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["response"]

def rag_pipeline(query, index, metadata, bm25):

    retrieved_chunks = hybrid_retrieve(
        query,
        index,
        metadata,
        bm25,
        k=5
    )
 
    prompt = build_prompt(query, retrieved_chunks)

    answer = generate_response(prompt)
    
    return {
        "retrieved_cases": retrieved_chunks,
        "generated_response": answer
    }
