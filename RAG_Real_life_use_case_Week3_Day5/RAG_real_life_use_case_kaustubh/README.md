# 📡 Airtel RAG Customer Support Chatbot

A **Retrieval-Augmented Generation (RAG)** based customer support chatbot built for **Bharti Airtel** — India's leading telecom company. This project demonstrates an end-to-end RAG pipeline with evaluation, brand-voice prompting, and a Streamlit-based chat interface.

## 🎯 Project Overview

**Use Case:** Customer Support Assistant for Airtel  
**Company:** Bharti Airtel Limited (Telecom)  
**Goal:** Build a RAG-based chatbot that answers customer queries about Airtel's plans, policies, billing, and services using only verified company documentation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI                                │
│   ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌────────────┐   │
│   │Mock Login│→ │Chat Interface│→│Chunk View│  │Eval Dashboard│  │
│   └──────────┘  └─────┬──────┘  └──────────┘  └────────────┘   │
│                       │                                          │
│                       ▼                                          │
│            ┌──────────────────┐                                  │
│            │   User Query     │                                  │
│            └────────┬─────────┘                                  │
│                     │                                            │
│         ┌───────────┼───────────┐                                │
│         ▼                       ▼                                │
│  ┌──────────────┐    ┌──────────────────┐                       │
│  │  RAG Engine   │    │   LLM Engine      │                     │
│  │              │    │                    │                      │
│  │ • PDF Loader │    │ • Groq (LLaMA 3.3)│                     │
│  │ • Chunker    │───▶│ • Brand Persona    │                     │
│  │ • Embedder   │    │ • CoT Reasoning    │                     │
│  │ • FAISS DB   │    │ • Temp/TopP Ctrl   │                     │
│  └──────────────┘    └──────────────────┘                       │
│         │                       │                                │
│         ▼                       ▼                                │
│  ┌──────────────┐    ┌──────────────────┐                       │
│  │ sentence-    │    │  Response with    │                       │
│  │ transformers │    │  CoT Reasoning    │                       │
│  │ (MiniLM-L6)  │    │  + Brand Voice    │                       │
│  └──────────────┘    └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **LLM** | Groq (LLaMA 3.3 70B Versatile) | Ultra-fast inference via Groq's LPU, excellent instruction-following. Cloud-based LLM chosen over SLM for superior reasoning and brand-voice adherence |
| **Embeddings** | `all-MiniLM-L6-v2` (SLM) | Lightweight (80MB), fast, 384-dim. Ideal for semantic search without GPU |
| **Vector DB** | FAISS (Facebook AI) | Fast similarity search, no server needed, persistent storage |
| **Chunking** | LangChain `RecursiveCharacterTextSplitter` | 500-char chunks with 100-char overlap for optimal retrieval |
| **UI** | Streamlit | Rapid prototyping, built-in chat components |
| **Auth** | Custom mock login (SHA-256) | Simple security gate as required |

## 🧠 Model Selection: LLM vs SLM

### Decision: **Hybrid Approach (LLM for generation + SLM for embeddings)**

| Aspect | LLM (LLaMA 3.3 70B via Groq) | SLM (MiniLM-L6-v2) |
|--------|------------------------|---------------------|
| **Used For** | Response generation | Document embeddings |
| **Why** | Superior brand-voice adherence, CoT reasoning, complex query handling | Fast, lightweight, no GPU needed, excellent for semantic similarity |
| **Size** | Cloud API (no local resources) | 80MB local model |
| **Latency** | ~0.5-2 seconds (Groq LPU) | ~50ms per embedding |
| **Cost** | Free tier available on Groq | Free (local) |

**Justification:** A pure SLM approach (e.g., Phi-2, TinyLlama) would struggle with:
- Maintaining consistent Airtel brand voice across varied queries
- Complex Chain-of-Thought reasoning
- Handling multi-turn conversations with context
- Generating detailed, structured responses

The hybrid approach gives us the best of both worlds: SLM efficiency for embeddings + LLM quality for generation.

## 📋 Features

- ✅ **RAG Pipeline**: PDF loading → Chunking → Embedding → FAISS → Retrieval → Generation
- ✅ **Brand Voice Persona**: Strict "Airtel Assist" persona that only uses provided context
- ✅ **Chain-of-Thought (CoT)**: Model explains retrieval logic before answering
- ✅ **Temperature/Top-P Controls**: Live sliders to experiment with generation parameters
- ✅ **Retrieved Chunks Display**: Dedicated tab showing source chunks with relevance scores
- ✅ **Mock Login**: Username/password authentication gate
- ✅ **Evaluation Suite**: 10-question benchmark with keyword matching & hallucination detection
- ✅ **Temperature Comparison**: Side-by-side comparison of factual vs. creative settings
- ✅ **Multi-turn Chat**: Conversation history maintained for context

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/KaustubhNair-bot/AI_Tr_BOT.git
cd AI_training_BOT/RAG_real_life_use_case_kaustubh
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API key
```bash
cp .env.example .env
# Edit .env and add your Groq API key
# Get one at: https://console.groq.com/keys
```

### 5. Run the app
```bash
streamlit run streamlit_app.py
```

### 6. Login
Use any of these demo credentials:
| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator |
| `agent` | `agent123` | Customer Support |
| `demo` | `demo123` | Viewer |

## 📁 Project Structure

```
RAG_real_life_use_case_kaustubh/
├── app/
│   ├── __init__.py          # Package init
│   ├── auth.py              # Mock authentication module
│   ├── rag_engine.py        # RAG pipeline (load, chunk, embed, FAISS, retrieve)
│   ├── llm_engine.py        # Gemini LLM with brand persona & CoT
│   └── evaluation.py        # Benchmarking & hallucination detection
├── data/
│   ├── airtel_plans_and_policies.md   # Source document (Markdown)
│   └── airtel_plans_and_policies.pdf  # Source document (PDF)
├── faiss_index/             # Persisted FAISS index (auto-generated)
├── evaluation_results/      # Benchmark results (auto-generated)
├── streamlit_app.py         # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 📊 Evaluation

The evaluation module (`app/evaluation.py`) tests the chatbot across 10 categories:

1. Prepaid Plans
2. Postpaid Plans
3. Porting / MNP
4. International Roaming
5. Refund Policy
6. Broadband
7. Customer Support
8. Rewards Program
9. Fair Usage Policy
10. Cancellation

### Metrics:
- **Keyword Match Score**: Percentage of expected keywords found in the response
- **Hallucination Rate**: Percentage of numeric claims not supported by retrieved chunks
- **Temperature Comparison**: Factual (T=0.0) vs Balanced (T=0.3) vs Creative (T=0.8)

## 🌡️ Generation Parameters Findings

| Setting | Temperature | Top-P | Hallucination Risk | Best For |
|---------|-------------|-------|-------------------|----------|
| Factual | 0.0 | 0.5 | ✅ Lowest | Plan details, pricing, policies |
| Balanced | 0.3 | 0.85 | ✅ Low | General queries, recommendations |
| Creative | 0.8 | 0.95 | ⚠️ Higher | Marketing copy, engagement |

**Conclusion:** Temperature 0.0–0.3 with Top-P 0.5–0.85 provides the best balance of factual accuracy and brand-voice adherence for customer support.

## 🔒 Security

- Mock login with SHA-256 hashed passwords
- Session-based authentication via Streamlit session state
- API key stored in `.env` (not committed to Git)
- Model constrained to only use provided context (reduces information leakage)

---

**Built by Kaustubh Nair** | AI Training Program — Week 3, Day 5 Assignment
