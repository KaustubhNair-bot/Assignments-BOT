

# MediSecure – Secure Medical RAG System

## Objective

This project implements a secure, fully local **Retrieval-Augmented Generation (RAG)** system designed for healthcare environments. It enables medical professionals to query unstructured patient transcriptions while ensuring strict data privacy through on-premises processing.

The system aims to:

- Minimize medical hallucinations by grounding answers in the Kaggle Medical Transcriptions dataset  
- Provide high-precision search using a **Two-Stage Retrieval pipeline** (Semantic Search + Reranking)  
- Secure sensitive access using **JWT-based authentication**

![alt text](image.png)

![alt text](image-1.png)
---

## System Architecture

The system is built on a completely local infrastructure to ensure that no patient data leaves the hospital premises.

### Pipeline Flow

1. **User Interface (Streamlit)**  
   Authenticated interface for doctors to submit clinical queries.

2. **FastAPI Backend**  
   Handles authentication, authorization, and request orchestration.

3. **Retrieval Stage**  
   Semantic search using **ChromaDB** with `all-MiniLM-L6-v2` embeddings.

4. **Reranking Stage**  
   Re-scoring the top retrieved results using the **BGE-Reranker-v2-m3 Cross-Encoder**.

5. **Generation Stage**  
   Context-grounded response generation using **Mistral-7B via Ollama**.

---

## RAG System Improvements

This version incorporates multiple **Advanced RAG techniques** to improve clinical accuracy, faithfulness, and reliability.

| Component | Choice | Justification |
|---------|------|--------------|
| Vector Store | ChromaDB | Chosen for native persistent storage and metadata handling, enabling structured organization of clinical content. |
| Chunking Strategy | Recursive Character Splitting | Uses a 600-character chunk size with 120-character overlap to preserve semantic continuity across symptoms and findings. |
| Embeddings | all-MiniLM-L6-v2 | A lightweight, 384-dimensional embedding model optimized for local CPU execution with strong semantic performance. |
| Reranker | BGE-Reranker-v2-m3 | A Cross-Encoder used as a second-stage filter to significantly improve retrieval precision. |
| LLM Engine | Ollama (Mistral-7B) | Selected for strong reasoning capabilities while ensuring complete offline inference for healthcare privacy compliance. |

---

## Evaluation – eval.py

### Purpose

The `eval.py` script benchmarks the performance of the **MediSecure RAG pipeline** against a **Base LLM** (standalone Mistral without retrieval) using five complex clinical queries.

### Evaluation Methodology: LLM-as-a-Judge

A Mistral-7B Judge model was used to score responses on a scale of **1–10** across the following dimensions:

- **Groundedness**  
  Whether the answer is factually supported by retrieved database records.

- **Specificity**  
  Presence of concrete clinical details such as medications, dosages, procedures, or findings.

- **Completeness**  
  Whether the response addresses all aspects of the clinical query.

---

## Benchmark Results Summary

| Metric | Base LLM (Mistral) | MediSecure RAG |
|------|------------------|---------------|
| Avg Groundedness | 4.2 / 10 | 9.1 / 10 |
| Avg Specificity | 6.8 / 10 | 8.8 / 10 |
| Avg Completeness | 8.0 / 10 | 7.5 / 10 |
| Avg Latency | ~1,200 ms | ~14,000 ms |

**Verdict:**  
While the RAG system introduces additional latency due to retrieval and reranking, it dramatically reduces hallucinations and produces highly specific, patient-grounded answers (e.g., identifying exact antibiotic counts such as “12 rounds”) that a base model cannot infer.

---

## Project Structure

```plaintext
MediSecure-RAG/
├── backend/
│   ├── auth.py           # JWT generation and validation
│   ├── ingest.py         # Document chunking and ChromaDB indexing
│   ├── main.py           # FastAPI server with secured endpoints
│   ├── rag.py            # RAG pipeline (Retrieval + Rerank + Generation)
│   └── users.py          # Local user database with Argon2 hashing
├── data/
│   └── medical_transcriptions.csv  # Knowledge base (~5,000 records)
├── chroma_db/            # Persistent vector database
├── app.py                # Streamlit frontend (comparison UI)
├── eval.py               # Task 2 benchmarking script
└── requirements.txt      # Project dependencies

## Setup and Installation
Prerequisites

Python 3.9 or higher

Ollama installed and running locally

Download the generator model using:
  -> ollama pull mistral
  
1. Install Dependencies
pip install -r requirements.txt

2. Initialize Vector Database
python backend/ingest.py

3. Run the Application

Terminal 1 (Backend):

uvicorn backend.main:app --reload


Terminal 2 (Frontend):

streamlit run app.py

4. Run Benchmarks

To compare RAG against the Base LLM:

python eval.py

Author

Abhimanyu Singh Rathore