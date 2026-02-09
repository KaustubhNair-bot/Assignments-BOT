# 🏥 MediSecure – Secure Medical RAG System
## Demo Link 
[Demo Link](https://drive.google.com/file/d/14pkaLRE6KtPpzHbV7VHBEpmOly5e2qYN/view?usp=sharing)

## 📌 Overview

This project implements a secure Retrieval-Augmented Generation (RAG) system for a private hospital.

The hospital has thousands of unstructured medical transcription notes and requires a system that:

-  Allows doctors to search past cases with similar symptoms
-  Ensures no patient data leaves the hospital infrastructure
- Restricts access to authorized doctors only

The transcription column from the Kaggle Medical Transcriptions dataset is used as the knowledge base.

## System Architecture

The system follows a fully local, secure architecture:

Doctor (Streamlit UI)
- JWT Authentication
- FastAPI Backend
- FAISS Vector Search
- Local Embedding Model
- Local LLM (Ollama - Mistral)
- Structured Clinical Response

All components run locally.
No external APIs are used.
No data is transmitted outside the system.

## Project Structure 
```bash
Medisecure_Assignment/
│
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── rag.py               # RAG pipeline (retrieval + generation)
│   ├── auth.py              # JWT authentication logic
│   ├── db.py                # SQLite database setup
│   ├── build_index.py       # One-time FAISS index creation script
│   │
│   ├── data/
│   │   └── mtsamples.csv    # Medical transcription dataset
│   │
│   └── vectorstore/
│       ├── faiss_index      # Stored FAISS index
│       └── chunks.pkl       # Stored text chunks
│
├── frontend/
│   └── app.py               # Streamlit UI
│
├── local_models/
│   └── all-MiniLM-L6-v2/    # Local embedding model
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Security Design

Security was treated as a first-class concern in this project.

1. Authentication

- OAuth2 password flow with JWT tokens
- Passwords hashed using Argon2 (modern OWASP-recommended hashing algorithm)
- Protected /rag endpoint requiring valid Bearer token

2. Data Privacy

- No calls to OpenAI or external LLM providers
- Embeddings loaded from local model files
- LLM served locally using Ollama
- Vector database stored on disk using FAISS

## RAG Implementation Details

The RAG pipeline works as follows:

- Medical notes are chunked into smaller segments.
- Each chunk is converted into embeddings using all-MiniLM-L6-v2.
- Embeddings are stored in a FAISS index (cosine similarity using normalized vectors).
- On query:
    - Query is embedded
    - Top-k similar chunks retrieved
    - Retrieved context injected into prompt
- Local LLM generates structured clinical insight
- The vector index is built offline using build_index.py to ensure:
    - Fast API startup
    - No runtime embedding delays

## New Registration Design

A public registration option is intentionally not provided in the Streamlit interface. In a real hospital deployment, doctor accounts would be created and managed by an administrator rather than allowing open self-registration.

For this assignment, account creation is handled internally through the backend (via the Swagger UI or direct database provisioning). This approach better reflects real-world healthcare systems where access control is centrally managed for security reasons.

## Tech Stack & Justification
### 🔹 FastAPI
Chosen for:
- High performance
- Native OAuth2 + JWT integration
- Clean API documentation

### 🔹 Streamlit
Used to quickly build:
- Secure doctor login UI
- Query interface
- Response display

It allows rapid prototyping while keeping backend separate.

### 🔹 FAISS
Selected because:
- Fully local vector database
- Extremely fast similarity search
- No external dependency
- Industry-standard for embedding retrieval

### 🔹 Sentence Transformers (MiniLM)
Chosen for:
- Lightweight and efficient embeddings
- Strong semantic similarity performance
- Can be downloaded and used fully offline

### 🔹 Ollama (Mistral 7B)
Selected because:
- Fully local LLM execution
- No external API calls
- Strong reasoning capability for a 7B model
- Lightweight enough for development environments

### 🔹 SQLite
Used for:
- Storing doctor credentials
- Simple local persistence
- Lightweight and sufficient for internal hospital deployment

## 🚀 Setup Instructions
1. Build Vector Store (One-Time Step)
```bash
python backend/build_index.py
```
This generates the FAISS index locally.

2. Start Backend
```bash
uvicorn main:app --reload
```

3. Start Streamlit Frontend
```bash
streamlit run app.py
```

## What I Learned During This Assignment

This assignment helped me learned how to design and implement a fully local RAG pipeline. Instead of relying on external APIs, an end-to-end system where embeddings, vector search, and LLM inference all run locally.Key technical learnings include:

- Building a fully local RAG system — from chunking raw medical notes, generating embeddings, creating a FAISS vector index, and integrating it with a local LLM for contextual generation.

- Working with vector databases (FAISS) and understanding how similarity search works using normalized embeddings and cosine similarity.

- Designing secure authentication using JWT tokens — implementing OAuth2 password flow, token creation, token validation, and protected API endpoints.

- Password security best practices, including hashing with Argon2 instead of storing plain credentials.

- Separating offline preprocessing from runtime APIs, by building the vector index once and loading it during API startup for fast and reliable service.

- Architectural thinking — structuring backend, frontend, authentication, and AI components in a clean and modular way.