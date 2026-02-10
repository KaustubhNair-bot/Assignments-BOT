# 🏥 MediSecure – Secure Medical RAG System

## 🎯 Objective

This project implements a secure Retrieval-Augmented Generation (RAG) system for a private hospital.It improves the earlier implemented RAG with enhanced techniques.

The system enables doctors to:

- Search past medical cases using symptom-based queries  
- Receive structured clinical summaries  
- Ensure no patient data leaves the hospital infrastructure  
- Restrict access to authorized users using JWT authentication  

The `transcription` column from the Kaggle Medical Transcriptions dataset is used as the knowledge base.

---

## 🧱 System Architecture

The system follows a fully local, secure architecture:

Doctor (Streamlit UI)  
→ JWT Authentication  
→ FastAPI Backend  
→ Hybrid Retrieval (FAISS + BM25)  
→ Local Embedding Model  
→ Local LLM (Ollama – Mistral)  
→ Structured Clinical Response  

All components run locally.  
No external APIs are used.  
No medical data is transmitted outside the system.

---

# 🚀 RAG System Improvements

## 📌 Overview

The RAG pipeline was upgraded to improve retrieval quality, contextual grounding, and response reliability. Improvements were made across chunking, embedding strength, and retrieval architecture.

---

## 🔧 Core Improvements

| Component | Previous Approach | Improved Approach | Justification |
|------------|------------------|------------------|----------------|
| **Chunking Strategy** | Fixed-size chunking | Recursive chunking with overlap | Preserves semantic continuity and prevents important clinical details from being split across chunk boundaries. |
| **Embedding Model** | Lightweight general-purpose embeddings | `all-mpnet-base-v2` | Provides stronger semantic representations for nuanced medical terminology and symptom relationships. |
| **RAG Architecture** | Dense retrieval only (FAISS) | Hybrid retrieval (Dense + BM25) with deduplication | Combines semantic similarity with keyword matching, improving robustness across conceptual and exact clinical queries. |

---

## 🛠 Additional Enhancements

- Removed duplicate medical records before indexing  
- Applied post-retrieval deduplication to prevent repeated case excerpts  
- Improved prompt structure to:
  - Dynamically group unique patient cases  
  - Prevent hallucinated diagnoses  
  - Enforce structured clinical summaries  
- Set generation temperature to `0.0` for deterministic benchmarking  

---

# 🧪 Evaluation – `eval.py`

## 📌 Purpose

The `eval.py` script was designed to benchmark the improved RAG system against a base LLM under identical generation settings.

---

## ⚙️ How It Works

The evaluation script:

1. Loads the FAISS index and BM25 retriever  
2. Runs five predefined clinical queries  
3. Generates responses from:
   - Base LLM (no retrieval)  
   - RAG pipeline (hybrid retrieval + generation)  
4. Measures:
   - Latency  
   - Semantic similarity (BERTScore)  
5. Exports results to `evaluation_results.csv`

---

## 📊 Evaluation Metrics

The following metrics were used:

- **Relevance (1–5)** – Measures how directly the response addresses the clinical query  
- **Grounding (0–2)** – Measures whether the response is supported by retrieved cases  
- **Hallucination (Yes/No)** – Detects unsupported medical claims  
- **Semantic Similarity (BERTScore)** – Measures conceptual alignment with retrieved context  

Detailed responses and scoring for each query are available in `evaluation_results.csv`.

---

# ✅ Conclusion

The improved RAG architecture enhances contextual grounding and clinical relevance compared to a standalone LLM.  

While the base model tends to provide conservative responses, the RAG system delivers structured, evidence-aligned summaries grounded in historical medical cases.

This makes the system better suited for domain-sensitive applications such as healthcare decision support.
