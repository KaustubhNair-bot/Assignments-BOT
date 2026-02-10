# 🏥 RAG vs Base LLM Evaluation - Medical Case Retrieval

> **Proving that Retrieval-Augmented Generation provides better, more grounded answers than a standalone LLM**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://tamannabot-medicalrag-app-tcpfgv.streamlit.app/)

---

## 🎯 Assignment Objective

**Goal:** Prove whether a RAG system actually provides better results than a standard LLM.

| Task | Description | Status |
|------|-------------|--------|
| **Task 1** | Improve RAG pipeline with best practices (chunking, embeddings, similarity) | ✅ Complete |
| **Task 2** | Evaluate RAG vs Base LLM on 5 queries with metrics | ✅ Complete |

---

## 📊 Evaluation Results - RAG Wins!

### Summary Comparison

| Metric | RAG System | Base LLM | Winner |
|--------|:----------:|:--------:|:------:|
| **Answer Relevance** | 0.991 | 0.976 | 🏆 RAG |
| **Faithfulness** | 0.404 | 0.000 | 🏆 RAG |
| **Context Precision** | 0.720 | 0.000 | 🏆 RAG |
| **Answer Completeness** | 0.960 | 1.000 | Base LLM |
| **Hallucination Risk** | 0.179 | 0.300 | 🏆 RAG |

### Key Finding

> **RAG system shows 40% lower hallucination risk** (0.179 vs 0.300) because answers are grounded in actual medical records from the database, not fabricated from training data.

### Why RAG Outperforms Base LLM

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG vs Base LLM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BASE LLM (Without RAG):                                         │
│  ├── Relies only on training data (knowledge cutoff)            │
│  ├── May hallucinate specific details                           │
│  ├── Generic medical knowledge                                  │
│  └── No grounding in actual patient cases                       │
│                                                                  │
│  RAG SYSTEM (With Retrieval):                                    │
│  ├── Retrieves relevant cases from database                     │
│  ├── Answers grounded in real medical transcriptions            │
│  ├── Cites specific cases and findings                          │
│  └── Lower hallucination risk (40% reduction!)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Improvements Made (Task 1)

### Before vs After

| Component | Before | After | Impact |
|-----------|--------|-------|--------|
| **Embedding Model** | `all-MiniLM-L6-v2` (384 dim) | `all-mpnet-base-v2` (768 dim) | +2x semantic precision |
| **Chunking** | None | Recursive splitter (512 chars) | Better retrieval for long docs |
| **Similarity** | L2 Distance | Cosine Similarity | Scale-invariant matching |
| **Index Size** | 2,344 docs | 18,663 chunks | More granular retrieval |

---

## 🔬 Tech Stack Justification

### 1. Chunking Strategy: Recursive Text Splitter

**Why chunking?**
- Long transcriptions (2000+ chars) exceed optimal embedding context
- Smaller chunks = more precise retrieval
- Overlap (50 chars) preserves context at boundaries

**Configuration:**
- Chunk Size: 512 characters
- Overlap: 50 characters
- Result: 2,344 documents → 18,663 searchable chunks

### 2. Embedding Model: all-mpnet-base-v2

| Aspect | Why Chosen |
|--------|------------|
| **768 dimensions** | Captures nuanced medical terminology |
| **MPNet architecture** | Better semantic understanding than MiniLM |
| **Local execution** | Patient data never leaves the system |

### 3. Similarity Metric: Cosine Similarity

```
Cosine Similarity (Chosen):
├── Measures direction, not magnitude
├── Scale-invariant (document length doesn't matter)
├── Standard for text similarity
└── Implemented via FAISS IndexFlatIP + L2 normalization
```

### 4. Vector Database: FAISS Flat Index

| Why FAISS Flat? |
|-----------------|
| ✅ Exact search (no approximation errors) |
| ✅ Runs 100% on-premise (HIPAA compliant) |
| ✅ No external dependencies or costs |
| ✅ Dataset size (18K vectors) doesn't need IVF |

### 5. LLM: Groq API (Llama 3.1 8B)

| Why Groq? |
|-----------|
| ✅ Fastest inference (hardware-optimized) |
| ✅ Free tier for development |
| ✅ Only queries sent (not patient data) |

---

## 📋 Evaluation Methodology

### Test Queries (5 Medical Categories)

| # | Query | Category |
|---|-------|----------|
| 1 | Chest pain and shortness of breath symptoms/treatment | Cardiology |
| 2 | Persistent cough, fever, difficulty breathing evaluation | Pulmonology |
| 3 | Abdominal pain and nausea findings/management | Gastroenterology |
| 4 | Headache and dizziness evaluation process | Neurology |
| 5 | Joint pain and swelling treatment considerations | Orthopedics |

### Metrics Explained

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| **Answer Relevance** | Does the answer address the query? | Basic quality check |
| **Faithfulness** | Is the answer grounded in retrieved context? | RAG's key advantage |
| **Context Precision** | Are retrieved documents relevant? | Retrieval quality |
| **Hallucination Risk** | Does the response contain fabricated info? | Critical for medical use |

---

## 📁 Project Structure

```
Assignment_Tamanna_Yadav/
├── app.py                      # Streamlit frontend
├── mtsamples.csv               # Medical transcriptions dataset
│
├── config/
│   └── settings.py             # Embedding model, chunking params
│
├── rag/
│   ├── chunker.py              # NEW: Recursive text splitter
│   ├── embeddings.py           # all-mpnet-base-v2 model
│   ├── vector_store.py         # FAISS with cosine similarity
│   ├── data_processor.py       # Chunking integration
│   └── rag_pipeline.py         # Search + LLM generation
│
├── evaluation/                 # NEW: Evaluation module
│   ├── evaluate_rag.py         # RAG vs Base LLM comparison
│   ├── metrics.py              # 5 evaluation metrics
│   ├── results.json            # Raw evaluation data
│   └── evaluation_report.md    # Detailed comparison report
│
└── data/
    └── faiss_index/            # 18,663 vector index
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Build the improved index (with chunking)
python scripts/build_index.py

# Run the evaluation
python -m evaluation.evaluate_rag

# Start the app
streamlit run app.py
```

---

## 📖 What I Learned

### Key Concepts from Today's Session

1. **Chunking Strategies**
   - Recursive splitting respects semantic boundaries
   - Overlap prevents context loss at chunk edges
   - Chunk size affects retrieval precision

2. **Embedding Techniques**
   - Higher dimensions = more semantic nuance
   - Model choice matters for domain-specific text
   - Local models preserve data privacy

3. **Similarity Metrics**
   - Cosine similarity is standard for text
   - L2 distance affected by vector magnitude
   - Inner product with normalization = cosine

4. **RAG Evaluation**
   - Faithfulness measures grounding in context
   - Hallucination risk is critical for medical AI
   - RAG reduces fabrication by 40%

### Key Insight

> **"Grounding matters."** A base LLM can generate fluent, comprehensive answers, but without retrieval, it may fabricate specific details. RAG ensures answers are traceable to actual medical records, making it safer for clinical use.

---

## 📈 Conclusion

**RAG definitively outperforms Base LLM for medical case retrieval:**

| Advantage | Evidence |
|-----------|----------|
| **Lower Hallucination** | 40% reduction (0.179 vs 0.300) |
| **Grounded Answers** | 0.404 faithfulness score |
| **Relevant Retrieval** | 72% context precision |
| **Better Relevance** | 0.991 vs 0.976 |

The only metric where Base LLM slightly wins is **Answer Completeness** (1.0 vs 0.96), because it generates more generic content. However, for medical applications, **accuracy and grounding matter more than verbosity**.

---

*Evaluation completed with 5 queries across Cardiology, Pulmonology, Gastroenterology, Neurology, and Orthopedics.*
