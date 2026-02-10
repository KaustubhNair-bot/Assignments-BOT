# MediCure RAG System

A secure Retrieval Augmented Generation (RAG) system designed for healthcare professionals to search through medical transcriptions using semantic search, integrated with an LLM for natural language answer generation.

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Solution Architecture](#solution-architecture)
4. [Tech Stack Justification](#tech-stack-justification)
5. [Features](#features)
6. [Project Structure](#project-structure)
7. [Setup and Installation](#setup-and-installation)
8. [Running the Application](#running-the-application)
9. [Running the Evaluation](#running-the-evaluation)
10. [Usage Guide](#usage-guide)
11. [API Documentation](#api-documentation)
12. [Security Considerations](#security-considerations)
13. [RAG vs Base LLM Evaluation](#rag-vs-base-llm-evaluation)
14. [Author](#author)

---

## Overview

MediCure RAG is an AI-powered medical case search system that enables doctors to find similar patient cases based on symptoms, conditions, or medical procedures. The system combines:

1. **FAISS-based vector search** for efficient retrieval of similar medical transcriptions
2. **Groq LLM integration** (Llama 3.3 70B) for generating natural language answers grounded in retrieved cases
3. **JWT authentication** for secure access control
4. **Local file-based storage** for user data and document caching
5. **Streamlit** for a modern, interactive web interface

---

## Problem Statement

A private hospital with thousands of unstructured patient notes required a secure AI system that allows doctors to:

1. Search for past cases with similar symptoms using RAG for intelligent semantic search
2. Get AI-generated natural language answers grounded in actual patient records
3. Protect patient data with local processing and access control through JWT authentication
4. Compare the effectiveness of RAG against a standalone LLM

---

## Solution Architecture

```
+-------------------+     +-------------------+     +-------------------+
|   Streamlit UI    |---->|   FastAPI Backend |---->|   Data Layer      |
|   (Port 8501)     |     |   (Port 8000)     |     |                   |
+-------------------+     +-------------------+     +-------------------+
                                   |
                    +--------------+--------------+
                    |              |              |
              +----------+  +----------+  +----------+
              |   JWT    |  |   RAG    |  |   LLM    |
              |   Auth   |  |  Engine  |  |  Engine  |
              +----------+  +----------+  +----------+
                                 |              |
                    +------------+         +----+----+
                    |            |         |         |
              +----------+  +----------+  |  Groq   |
              |  FAISS   |  | Sentence |  |  API    |
              |  Index   |  | Transf.  |  +---------+
              +----------+  +----------+
                (Local)       (Local)      (External)
```

### Pipeline Flow

**RAG Pipeline (Full):**
```
User Query -> Embed Query (local) -> FAISS Search -> Retrieve Top-K Cases
           -> Pass Cases as Context to LLM (Groq) -> Generate Grounded Answer
```

**Base LLM Pipeline (Comparison):**
```
User Query -> Send directly to LLM (Groq) -> Generate Answer (no context)
```

---

## Tech Stack Justification

### Why FAISS over ChromaDB?

| Criteria | FAISS | ChromaDB |
|----------|-------|----------|
| Python 3.14 Compatibility | Full support | Broken (pydantic v1 incompatibility) |
| Performance | Excellent - Optimized C++ with Python bindings | Good - Pure Python |
| Index Size Efficiency | Compact binary format | Larger SQLite-based storage |
| Maturity | Production-proven (Meta/Facebook) | Relatively newer |
| Memory Overhead | Minimal | Higher due to embedded server |
| Dependencies | Lightweight | Heavy (pydantic v1, grpcio, etc.) |

**Decision:** ChromaDB failed to initialize on Python 3.14 due to its dependency on pydantic v1's `BaseSettings`, which is incompatible. FAISS provides better performance with fewer dependencies and full compatibility.

### Why File-Based Storage (No External Database)?

| Criteria | File-Based (JSON + Pickle) | MongoDB | SQLite |
|----------|---------------------------|---------|--------|
| Deployment Complexity | Zero - just files | Requires server or Atlas | Requires driver |
| Streamlit Cloud Compatibility | Works out of the box | Needs remote instance | Works |
| Setup Required | None | Install & configure | pip install |
| Dependencies | None (built-in Python) | pymongo | sqlite3 (built-in) |
| Performance for our use case | Excellent (in-memory) | Good | Good |
| Scalability | Moderate | Excellent | Moderate |

**Decision:** For this project's scale (~5,000 records), file-based storage is the simplest and most portable approach. Document metadata is cached in a pickle file and loaded into memory at startup. User data is stored in a simple JSON file. This eliminates the need for any database server, making deployment to Streamlit Cloud trivial.

### Why Groq API for LLM?

| Criteria | Groq | OpenAI | Local LLM (Ollama) |
|----------|------|--------|---------------------|
| Speed | Fastest inference (custom LPU) | Standard | Slow (hardware-dependent) |
| Cost | Generous free tier | Paid from start | Free but resource-heavy |
| Model Quality | Llama 3.3 70B (state-of-art open model) | GPT-4 | Limited by local hardware |
| Setup Complexity | API key only | API key only | Requires GPU, model download |
| Privacy Consideration | Queries sent to API | Queries sent to API | Fully local |

**Decision:** Groq provides the fastest inference speed for large language models using their custom LPU (Language Processing Unit) hardware. The Llama 3.3 70B model available through Groq offers excellent medical knowledge while being an open-source model. For a production healthcare deployment, a local LLM would be preferred for full data privacy.

### Why Sentence-Transformers (all-MiniLM-L6-v2)?

| Criteria | all-MiniLM-L6-v2 | OpenAI Embeddings | BiomedBERT |
|----------|-------------------|-------------------|------------|
| Data Privacy | Fully local | Cloud API | Fully local |
| Model Size | ~80MB | N/A (API) | ~400MB |
| Speed | Fast | Network-dependent | Moderate |
| Embedding Dimension | 384 | 1536 | 768 |
| Quality for Medical Text | Good | Excellent | Best for medical |
| Setup | pip install only | API key required | Specialized setup |

**Decision:** all-MiniLM-L6-v2 runs entirely locally, ensuring no patient data leaves the system during the embedding process. It provides a good balance of speed, accuracy, and size. All embeddings are generated on-premises.

### Why Streamlit?

| Criteria | Streamlit | HTML/CSS/JS | Gradio | Flask+Templates |
|----------|-----------|-------------|--------|-----------------|
| Development Speed | Very fast | Slow | Fast | Moderate |
| Python-native | Yes | No | Yes | Partial |
| Interactive Widgets | Built-in | Manual JS | Built-in | Manual |
| Session Management | Built-in | Manual | Limited | Manual |
| Deployment | Simple (Streamlit Cloud) | Requires server | Simple | Moderate |

**Decision:** Streamlit allows rapid development of interactive data applications in pure Python. Its built-in session state, widgets, and layout system make it ideal for building a medical search interface without frontend development overhead.

### Why FastAPI?

| Criteria | FastAPI | Flask | Django |
|----------|---------|-------|--------|
| Performance | Async, high performance | Sync, moderate | Sync, moderate |
| API Documentation | Auto-generated (Swagger) | Manual | Manual |
| Type Validation | Pydantic (automatic) | Manual | Forms/Serializers |
| Modern Python | async/await native | Sync | Sync |
| JWT Support | Easy integration | Manual | django-rest-framework |

**Decision:** FastAPI provides automatic API documentation, request validation through Pydantic models, and native async support. Its automatic Swagger UI at `/docs` makes API testing straightforward.

---

## Features

### Semantic Search (Retrieval)
- FAISS-based vector similarity search
- sentence-transformers for local embedding generation
- Filter results by medical specialty
- Ranked results with similarity scores

### RAG + LLM Answer Generation
- Retrieved cases passed as context to Groq LLM
- Natural language answers grounded in actual patient records
- Case references and citations in generated answers
- Reduced hallucination through context grounding

### RAG vs Base LLM Comparison
- Side-by-side comparison in the UI
- Automated evaluation script with multiple metrics
- LLM-as-Judge evaluation for answer quality
- Detailed markdown report generation

### Secure Authentication
- JWT-based authentication with bcrypt password hashing
- Protected API endpoints
- Configurable token expiration

---

## Project Structure

```
Medi-Cure-RAG-Kaustubh/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application (endpoints)
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models
│   ├── auth.py              # JWT authentication (bcrypt + JSON storage)
│   ├── rag_engine.py        # FAISS + sentence-transformers RAG
│   └── llm_engine.py        # Groq LLM integration
├── data/
│   └── mtsamples.csv        # Medical transcriptions dataset
├── faiss_index/             # FAISS index + document cache (auto-generated)
├── users.json               # User accounts (auto-generated)
├── streamlit_app.py         # Streamlit UI (3 tabs)
├── evaluation.py            # RAG vs Base LLM evaluation script
├── EVALUATION_REPORT.md     # Generated evaluation report
├── evaluation_results.json  # Raw evaluation data
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Groq API key (free at https://console.groq.com)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Medi-Cure-RAG-Kaustubh
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Edit `.env` and set your Groq API key:

```env
GROQ_API_KEY=your-actual-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### Step 5: Ensure Dataset Exists

Verify `data/mtsamples.csv` is present. This dataset contains ~5,000 medical transcriptions.

---

## Running the Application

Two terminals are required:

### Terminal 1: Start the API Server

```bash
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

First run will build the FAISS index (approximately 2-5 minutes). Subsequent runs load from disk.

### Terminal 2: Start Streamlit UI

```bash
source venv/bin/activate
streamlit run streamlit_app.py --server.port 8501
```

### Access Points

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| API Health Check | http://localhost:8000/health |

---

## Running the Evaluation

To run the RAG vs Base LLM comparison:

```bash
source venv/bin/activate
python evaluation.py
```

This will:
1. Run 5 medical queries through both RAG and base LLM pipelines
2. Evaluate using keyword overlap and LLM-as-Judge metrics
3. Generate `EVALUATION_REPORT.md` with detailed results
4. Save raw data to `evaluation_results.json`

---

## Usage Guide

### Demo Accounts

| Username | Password | Specialty |
|----------|----------|-----------|
| dr.smith | doctor123 | Cardiology |
| dr.jones | doctor123 | General Surgery |
| dr.patel | doctor123 | Internal Medicine |

### Three UI Tabs

1. **Retrieval Search**: Find similar cases using semantic search (FAISS only)
2. **RAG + LLM Answer**: Get AI-generated answers grounded in retrieved cases
3. **RAG vs Base LLM Comparison**: Side-by-side comparison of both approaches

---

## API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new doctor |
| POST | `/auth/login` | Login, receive JWT token |
| GET | `/auth/me` | Get current user info |

### Search and RAG

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search` | Semantic search (retrieval only) |
| POST | `/ask` | RAG + LLM (retrieval + generation) |
| POST | `/ask-base` | Base LLM only (for comparison) |
| GET | `/specialties` | List medical specialties |
| GET | `/stats` | System statistics |

---

## Security Considerations

### Data Privacy

1. **Local Embeddings**: All text vectorization uses sentence-transformers running locally. No patient data is sent externally for embedding.

2. **LLM Queries**: When using the LLM features, query text and retrieved transcriptions are sent to the Groq API. For production healthcare use, consider a locally hosted LLM (e.g., Ollama with Llama 3).

3. **Local Storage**: FAISS index, document cache, and user data are all stored as local files.

### Authentication

1. **bcrypt Password Hashing**: Passwords are never stored in plaintext.
2. **JWT Token Expiration**: Tokens expire after 30 minutes (configurable).
3. **Protected Endpoints**: All search and LLM endpoints require valid JWT.

---

## RAG vs Base LLM Evaluation

### Evaluation Approach

The evaluation uses two established techniques:

1. **Automated Metrics**: Keyword overlap to measure topic coverage
2. **LLM-as-Judge**: Using the LLM itself to evaluate answer quality, a technique from evaluation frameworks like RAGAS, DeepEval, and TruLens

### Metrics Used

| Metric | Description | Applied To |
|--------|-------------|-----------|
| Context Relevance | Relevance of retrieved cases to query | RAG only |
| Groundedness | Is the answer grounded in retrieved context? | RAG only |
| Completeness | Thoroughness of the answer | Both |
| Specificity | Presence of specific medical details | Both |
| Keyword Overlap | Coverage of expected medical topics | Both |
| Hallucination Risk | Risk of fabricated information | Base LLM |
| Response Time | End-to-end latency | Both |

### Expected Findings

RAG is expected to outperform the base LLM in:
- **Specificity**: RAG answers reference real patient cases with actual details
- **Groundedness**: Answers are traceable to source documents
- **Hallucination Risk**: Lower risk since answers are grounded in real data
- **Domain Relevance**: Answers tailored to the hospital's actual patient records

The base LLM may perform comparably in:
- **General Medical Knowledge**: Broad questions not requiring case-specific data
- **Response Speed**: No retrieval overhead

The full evaluation report is generated at `EVALUATION_REPORT.md` after running `evaluation.py`.

---

## Dataset

- **Source**: Medical Transcriptions Dataset (Kaggle)
- **Records**: ~5,000 medical transcriptions
- **Specialties**: 40+ categories
- **Content**: Patient notes, procedures, diagnoses, treatment plans

---

## Author

**Kaustubh Nair**

---

## License

This project is licensed under the MIT License.
