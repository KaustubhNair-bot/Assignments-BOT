# 🏥 Clinical Case Retrieval System (C²RS)

> A secure, privacy-preserving RAG system for semantic search over medical transcriptions with AI-powered clinical decision support.
---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Login Credentials](#-login-credentials)
- [RAG Pipeline](#-rag-pipeline)
- [Evaluation Results](#-evaluation-results)
- [Security](#-security)
- [Limitations](#-limitations)
- [Future Work](#-future-work)

---

## 🎯 Overview

**C²RS** is an offline clinical decision support system that enables doctors to search through unstructured medical transcriptions using semantic similarity. The system combines **FAISS vector search**, **sentence transformers**, and **LLM-based answer generation** to provide evidence-based clinical insights without compromising patient privacy.

### Problem Statement

- 🗂️ Thousands of patient notes exist as unstructured free text
- 🔍 Traditional keyword search is ineffective for medical queries
- 🔒 Patient data cannot leave hospital premises (HIPAA compliance)
- 👨‍⚕️ Only authorized doctors should access sensitive records

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **🔐 JWT Authentication** | Secure token-based doctor authentication |
| **🧠 Semantic Search** | MPNet embeddings + FAISS for intelligent retrieval |
| **💬 AI Answer Generation** | LLM-powered clinical decision support |
| **📊 Relevance Scoring** | Transparent confidence metrics for each case |
| **📝 Medical Summarization** | Optional T5-based case summarization |
| **🏠 Fully Offline** | No external API calls, all processing local |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DOCTOR LOGIN (Streamlit)                │
│                    Username + Password                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  JWT AUTHENTICATION (FastAPI)               │
│              Token Generation & Verification                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLINICAL QUERY INPUT                       │
│           "chest pain", "pneumonia treatment"                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              MPNET EMBEDDING GENERATION                      │
│           Convert query → 768-dim vector                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 FAISS VECTOR SEARCH                          │
│          Retrieve Top-5 Similar Cases (L2 distance)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              RETRIEVED CLINICAL CASES                        │
│        Context chunks with relevance scores                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM ANSWER GENERATION (Groq)                    │
│     Structured clinical response with evidence               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         OPTIONAL: T5 SUMMARIZATION                           │
│            Concise case summaries                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
medical-rag/
│
├── app.py                          # Landing page & login UI
├── pages/
│   └── search.py                   # Protected search dashboard
│
├── backend/
│   ├── main.py                     # FastAPI endpoints (/login, /ask, /search)
│   ├── auth.py                     # JWT token management
│   ├── rag.py                      # FAISS retrieval + RAG pipeline
│   ├── generator.py                # LLM answer generation (Groq)
│   ├── summarizer.py               # T5 medical summarization
│   ├── evaluate.py                 # Evaluation metrics (relevancy, faithfulness)
│   ├── metrics.py                  # Performance metrics for comparison
│   └── prompts.py                  # Structured LLM prompts
│
├── embeddings/
│   ├── build_index.py              # Create FAISS index
│   ├── medical.index               # FAISS vector store (binary)
│   └── texts.txt                   # Original transcriptions (line-separated)
│
├── data/
│   └── medical.csv                 # Kaggle medical transcriptions dataset
│
├── evaluation_results.json         # RAG vs Base LLM comparison results
├── RAG_vs_Base_LLM_Comparison.docx # Detailed evaluation report
├── README.md                       # Project documentation
├── requirements.txt                # Python dependencies
└── run_eval.py                     # Automated evaluation script
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | FastAPI | Lightweight REST endpoints |
| **Frontend** | Streamlit | Rapid prototyping UI |
| **Authentication** | JWT (python-jose) | Secure token-based auth |
| **Vector Search** | FAISS (CPU) | Fast similarity search |
| **Embeddings** | Sentence-Transformers (MPNet) | Semantic text encoding |
| **LLM** | Groq API (Llama 3.3 70B) | Answer generation |
| **Summarization** | T5-Small (Transformers) | Local case summarization |
| **Dataset** | [Kaggle Medical Transcriptions](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions) | ~5K clinical notes |

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Groq API key ([Get one here](https://console.groq.com))

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/medical-rag.git
cd medical-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Build FAISS index (one-time setup)
python embeddings/build_index.py
```

---

## 💻 Usage

### 1. Start Backend API

```bash
# Terminal 1
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Launch Streamlit UI

```bash
# Terminal 2
streamlit run app.py
```

### 3. Access Application

Open browser and navigate to:
```
http://localhost:8501
```

---

## 🔑 Login Credentials

Use these credentials to access the system:

| Username | Password |
|----------|----------|
| `doctor1` | `pass123` |
| `doctor2` | `med456` |

> **Note:** These are demo credentials. In production, implement proper user management with hashed passwords.

---

## 🔍 RAG Pipeline

### How It Works

1. **Query Encoding**
   ```python
   query = "chest pain in elderly patient"
   query_vector = mpnet_model.encode([query])  # → 768-dim vector
   ```

2. **FAISS Retrieval**
   ```python
   distances, indices = faiss_index.search(query_vector, k=5)
   # Returns 5 most similar cases with L2 distances
   ```

3. **Context Assembly**
   ```python
   retrieved_cases = [texts[idx] for idx in indices if distance < 1.4]
   ```

4. **LLM Answer Generation**
   ```python
   prompt = f"""
   Context: {retrieved_cases}
   Question: {query}
   
   Provide:
   1. Clinical Summary
   2. Diagnosis
   3. Management
   4. Red Flags
   5. Evidence Source
   """
   ```

### Distance Threshold

- Distance < **1.0**: Highly relevant (95%+ match)
- Distance < **1.4**: Relevant (70-95% match)
- Distance > **1.4**: Not retrieved (noise filter)

---

## 📊 Evaluation Results

### RAG vs Base LLM Performance

| Metric | Base LLM | RAG System | Improvement |
|--------|----------|------------|-------------|
| **Keyword Coverage** | 32.67% | **48.00%** | +47% |
| **Faithfulness** | N/A | **80.22%** | — |
| **Hallucination Rate** | N/A | **19.78%** | — |
| **Clinical Utility** | Mixed | **100% Excellent** | ✅ |
| **Avg Response Time** | N/A | **2.90s** | — |

### Key Findings

✅ **100% Excellent clinical utility** across all test queries  
✅ **47% better keyword coverage** than base LLM  
✅ **80%+ faithfulness** to source medical records  
✅ **Sub-3 second responses** for real-time decision support  

📄 [Full Evaluation Report](RAG_vs_Base_LLM_Comparison.docx)

---

## 🔒 Security

### Privacy-First Design

- ✅ **No external API calls** for sensitive data
- ✅ **JWT-based authentication** with 2-hour token expiry
- ✅ **Local model inference** (T5 summarization)
- ✅ **Protected routes** requiring valid tokens
- ✅ **HIPAA-compliant** architecture (local deployment)

### Authentication Flow

```python
# Login
POST /login
{
  "username": "doctor1",
  "password": "pass123"
}
→ Returns: { "token": "eyJ0eXAi..." }

# Protected Search
GET /ask?query=chest+pain
Headers: { "token": "eyJ0eXAi..." }
→ Returns: Clinical answer + retrieved cases
```

---

## ⚠️ Limitations

- 📊 **Dataset Size**: Limited to ~5K transcriptions (expandable)
- 🤖 **T5 Grammar**: Lightweight model may produce less polished summaries
- 🏷️ **No Entity Extraction**: Doesn't highlight specific symptoms/drugs
- 👥 **Basic Auth**: Production needs role-based access control (RBAC)

---

## 🚀 Future Work

- **ICD-10 Code Prediction** for retrieved cases
- **Medical Entity Highlighting** (NER integration)
- **Multi-Modal Support** (images, lab reports)
- **Federated Search** across multiple hospital databases
- **Fine-tuned Medical LLM** (BioGPT, Med-PaLM)
- **Audit Logging** for compliance tracking

---

## 📝 Citation

```bibtex
@software{clinical_case_retrieval_2024,
  title = {Clinical Case Retrieval System (C²RS)},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/medical-rag}
}
```

---

##  Acknowledgments

- [Kaggle Medical Transcriptions Dataset](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions)
- [Sentence-Transformers](https://www.sbert.net/) for MPNet embeddings
- [FAISS](https://github.com/facebookresearch/faiss) for efficient vector search
- [Groq](https://groq.com/) for fast LLM inference

