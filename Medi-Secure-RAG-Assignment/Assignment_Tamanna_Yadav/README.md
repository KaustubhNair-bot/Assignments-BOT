# 🏥 MediSecure RAG System

> **A Secure AI-Powered Medical Case Retrieval System for Healthcare Professionals**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://tamannabot-medicalrag-app-tcpfgv.streamlit.app/)



## 🎯 Introduction

**MediSecure RAG** is a production-ready AI system that helps doctors find clinically similar past cases from thousands of medical transcriptions. Built with privacy as the core principle, it ensures **zero patient data leaves the hospital's infrastructure** while leveraging modern AI for intelligent search.

This project was developed as part of a learning assignment to understand:
- How **Retrieval-Augmented Generation (RAG)** works in practice
- Building **secure AI systems** for sensitive healthcare data
- Implementing **JWT authentication** for access control
- Working with **vector databases** for semantic search

---

## 🚀 Live Demo

**Try the application here:** [https://tamannabot-medicalrag-app-tcpfgv.streamlit.app/](https://tamannabot-medicalrag-app-tcpfgv.streamlit.app/)

**Demo Credentials:**
- **Username:** `dr.smith` or `dr.jones`
- **Password:** `doctor123`

---

## 🔍 The Problem

Hospitals generate thousands of medical transcriptions daily. When a doctor encounters a patient with specific symptoms, they often want to:

1. **Find similar past cases** to understand treatment patterns
2. **Learn from historical outcomes** to make better decisions
3. **Identify rare conditions** by matching symptom patterns

**Traditional challenges:**
- Manual searching through records is time-consuming
- Keyword search misses semantically similar cases
- Sending patient data to cloud AI services violates privacy regulations (HIPAA)
- No authentication means anyone could access sensitive records

---

## 💡 The Solution

MediSecure RAG addresses these challenges by:

| Challenge | Solution |
|-----------|----------|
| Time-consuming manual search | **Semantic search** finds similar cases in milliseconds |
| Keyword limitations | **Vector embeddings** understand meaning, not just words |
| Privacy concerns | **On-premise processing** - patient data never leaves the system |
| Unauthorized access | **JWT authentication** ensures only verified doctors can access |

---

## 📚 Key Concepts Explained

### What is RAG (Retrieval-Augmented Generation)?

RAG is a technique that combines **information retrieval** with **AI generation**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG Pipeline                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User Query ──▶ [Embed Query] ──▶ [Search Vector DB] ──▶       │
│                                           │                     │
│                                           ▼                     │
│                                    [Retrieved Docs]             │
│                                           │                     │
│                                           ▼                     │
│                              [LLM Generates Summary]            │
│                                           │                     │
│                                           ▼                     │
│                                    [Final Response]             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why RAG instead of just using an LLM?**
- LLMs have knowledge cutoffs and can hallucinate
- RAG grounds responses in your actual data
- You control what information the AI can access

### What are Vector Embeddings?

Embeddings convert text into numerical vectors that capture semantic meaning:

```
"Patient has chest pain"     →  [0.23, -0.45, 0.67, ...]
"Cardiac discomfort reported" →  [0.21, -0.43, 0.65, ...]  ← Similar vectors!
"Broken leg injury"          →  [0.89, 0.12, -0.34, ...]  ← Different vector
```

Similar meanings = Similar vectors = Found by similarity search

### What is FAISS?

**FAISS** (Facebook AI Similarity Search) is a library for efficient similarity search:
- Stores millions of vectors
- Finds nearest neighbors in milliseconds
- Runs entirely locally (no cloud needed)

### What is JWT Authentication?

**JWT** (JSON Web Token) is a secure way to verify user identity:

```
┌─────────────────────────────────────────────────────────────────┐
│                      JWT Authentication Flow                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Doctor enters username/password                             │
│                    │                                             │
│                    ▼                                             │
│   2. Server verifies credentials against stored hash             │
│                    │                                             │
│                    ▼                                             │
│   3. Server creates signed JWT token                             │
│      {user: "dr.smith", exp: "24h", signature: "xyz..."}        │
│                    │                                             │
│                    ▼                                             │
│   4. Token stored in session, sent with each request             │
│                    │                                             │
│                    ▼                                             │
│   5. Server validates token signature on each request            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MediSecure RAG System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Streamlit  │───▶│     JWT      │───▶│   RAG Pipeline   │  │
│  │   Frontend   │    │    Auth      │    │                  │  │
│  └──────────────┘    └──────────────┘    └────────┬─────────┘  │
│         │                                          │            │
│         │            ┌─────────────────────────────┼────────┐   │
│         │            │      ON-PREMISE ZONE        ▼        │   │
│         │            │  ┌──────────────────────────────┐    │   │
│         │            │  │   Sentence Transformers      │    │   │
│         │            │  │   (Local Embedding Model)    │    │   │
│         │            │  └────────────┬─────────────────┘    │   │
│         │            │               │                      │   │
│         │            │               ▼                      │   │
│         │            │  ┌──────────────────────────────┐    │   │
│         │            │  │      FAISS Vector DB         │    │   │
│         │            │  │   (2,344 Medical Cases)      │    │   │
│         │            │  └──────────────────────────────┘    │   │
│         │            │                                      │   │
│         │            │  🔒 Patient data NEVER leaves here   │   │
│         │            └──────────────────────────────────────┘   │
│         │                                                       │
│         │            ┌──────────────────────────────────────┐   │
│         └───────────▶│         Groq API (External)          │   │
│                      │  Only receives: Search query text     │   │
│                      │  Never receives: Patient records      │   │
│                      └──────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## �️ Tech Stack & Justification

### Why These Technologies?

| Technology | Purpose | Why I Chose It |
|------------|---------|----------------|
| **Python** | Core language | Industry standard for AI/ML, extensive libraries |
| **Streamlit** | Frontend UI | Rapid prototyping, built-in session management, easy deployment |
| **FAISS** | Vector database | Fast similarity search, runs locally, handles large datasets |
| **Sentence Transformers** | Text embeddings | Local execution (privacy), high-quality semantic understanding |
| **Groq API** | LLM inference | Fast response times, only receives queries (not patient data) |
| **JWT + bcrypt** | Authentication | Stateless auth, secure password hashing, industry standard |
| **Pandas** | Data processing | Efficient CSV handling, data manipulation |


---

## �📁 Project Structure

```
Assignment_Tamanna_Yadav/
│
├── 📄 app.py                    # Main Streamlit application
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment template
├── 📄 .gitignore                # Git ignore patterns
├── 📄 mtsamples.csv             # Medical transcriptions (5000 records)
├── 📄 README.md                 # This documentation
│
├── 📁 config/                   # Configuration Module
│   ├── __init__.py
│   └── settings.py              # Centralized settings, user credentials
│
├── 📁 auth/                     # Authentication Module
│   ├── __init__.py
│   ├── jwt_handler.py           # Token creation & validation
│   └── authenticator.py         # Login logic, password verification
│
├── 📁 rag/                      # RAG Pipeline Module
│   ├── __init__.py
│   ├── embeddings.py            # Sentence transformer wrapper
│   ├── vector_store.py          # FAISS index management
│   ├── data_processor.py        # Data cleaning, anonymization
│   └── rag_pipeline.py          # Main search & summarization
│
├── 📁 scripts/                  # Utility Scripts
│   ├── build_index.py           # Create FAISS index
│   └── generate_password_hash.py # Create bcrypt hashes
│
└── 📁 data/                     # Generated Data (gitignored)
    ├── faiss_index/             # Vector index files
    └── metadata.pkl             # Document metadata
```

---

## ⚙️ How It Works

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Journey                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣ AUTHENTICATION                                              │
│     Doctor enters credentials                                    │
│            │                                                     │
│            ▼                                                     │
│     bcrypt verifies password hash                                │
│            │                                                     │
│            ▼                                                     │
│     JWT token generated (valid 24h)                              │
│                                                                  │
│  2️⃣ SEARCH QUERY                                                 │
│     Doctor types: "patient with chest pain and fever"            │
│            │                                                     │
│            ▼                                                     │
│     Query converted to 384-dim vector (locally)                  │
│            │                                                     │
│            ▼                                                     │
│     FAISS finds top-5 similar cases                              │
│                                                                  │
│  3️⃣ RESULTS DISPLAY                                              │
│     Cases shown with:                                            │
│     • Similarity scores (e.g., 78.5%)                            │
│     • Medical specialty                                          │
│     • Case description                                           │
│     • Full transcription (expandable)                            │
│                                                                  │
│  4️⃣ AI SUMMARY (Optional)                                        │
│     Query sent to Groq API (NOT patient data)                    │
│            │                                                     │
│            ▼                                                     │
│     LLM generates clinical insights                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager


### Installation

```bash
# 1. Clone or navigate to project
cd Assignment_Tamanna_Yadav

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your Groq API key (optional, for AI summaries)

# 5. Build the vector index (one-time setup)
python scripts/build_index.py

# 6. Run the application
streamlit run app.py
```

### Demo Credentials

| Username | Password | Specialty |
|----------|----------|-----------|
| `dr.smith` | `doctor123` | Internal Medicine |
| `dr.jones` | `doctor123` | Cardiology |

---

## 🔐 Security Features

### Multi-Layer Security Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Layers                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: AUTHENTICATION                                         │
│  ├── bcrypt password hashing (salt + hash)                       │
│  ├── JWT tokens with 24-hour expiration                          │
│  └── Session validation on every request                         │
│                                                                  │
│  Layer 2: DATA PRIVACY                                           │
│  ├── All embeddings generated locally                            │
│  ├── FAISS index stored on-premise                               │
│  ├── PII anonymization (phone, SSN, email, dates)                │
│  └── Only search queries sent to external API                    │
│                                                                  │
│  Layer 3: ACCESS CONTROL                                         │
│  ├── No public endpoints without authentication                  │
│  ├── Token required for all data access                          │
│  └── Automatic session timeout                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## � What I Learned

### Technical Skills Gained

1. **RAG Architecture Design**
   - Understanding the retrieval-then-generate paradigm
   - Balancing retrieval quality vs. speed
   - Chunking strategies for long documents

2. **Vector Databases**
   - How embeddings capture semantic meaning
   - FAISS index types (Flat, IVF, HNSW)
   - Similarity metrics (L2, cosine, inner product)

3. **Security Implementation**
   - JWT token lifecycle management
   - bcrypt salting and hashing
   - Session state in stateless applications

4. **Production Considerations**
   - Data deduplication importance
   - Error handling for external APIs
   - Environment-based configuration

### Key Insights

> **"Privacy by Design"** - I learned that security shouldn't be an afterthought. By choosing local embeddings and on-premise storage from the start, privacy became inherent to the architecture.

> **"Semantic Search is Powerful"** - Traditional keyword search would miss "chest pain" when searching for "cardiac discomfort". Vector search understands they're related.

> **"Deduplication Matters"** - The original dataset had 2,655 duplicate transcriptions. Without deduplication, search results would show the same case multiple times.

---

## 🧩 Challenges & Solutions

### Challenge 1: Duplicate Search Results
**Problem:** Same cases appearing multiple times in results  
**Solution:** Implemented hash-based deduplication in data processor, reducing 4,999 records to 2,344 unique cases

### Challenge 2: Password Hash Corruption
**Problem:** bcrypt hashes getting truncated in terminal output  
**Solution:** Used Python script to directly write hashes to config file, avoiding terminal line-wrap issues

### Challenge 3: API Key Security
**Problem:** Needed to use Groq API without exposing key  
**Solution:** Environment variables with `.env` file (gitignored), clear separation of config

### Challenge 4: Large Model Loading Time
**Problem:** Sentence transformer model slow to load on first query  
**Solution:** Lazy loading pattern - model loads once and stays in memory


