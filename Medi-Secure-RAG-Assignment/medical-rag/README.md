# Clinical Case Retrieval System (C²RS)
# Clinical Case Retrieval System (C²RS)

## Overview
The Clinical Case Retrieval System (C²RS) is a secure, offline Retrieval-Augmented Generation (RAG) platform designed for hospitals to search unstructured medical transcriptions.  
Doctors can retrieve past cases with similar symptoms and optionally generate concise medical summaries using a local Small Language Model (SLM) — without any patient data leaving the system.

---

## Features

- **Semantic Search (RAG)**
  - Uses `all-mpnet-base-v2` embeddings and FAISS vector index  
  - Retrieves top-5 clinically relevant transcriptions

- **Security**
  - JWT based authentication  
  - Only authorized doctors can access records  
  - Fully offline – no external API calls

- **Doctor-Friendly Interface**
  - Relevance labels: High / Moderate / Low  
  - Clean clinical view of transcriptions  
  - Optional “Generate Medical Summary” button

- **Local SLM Summarization**
  - T5 model generates concise summaries  
  - On-demand only (doctor controlled)

---

## Dataset Used
- Kaggle: *Medical Transcriptions Dataset*  
- Column used as knowledge base: **transcription**

Duplicates were removed before indexing to avoid biased retrieval.

---

## Tech Stack Justification

### 1. Sentence Transformers + FAISS
- Efficient semantic similarity search  
- Works completely offline  
- Scales to thousands of records  
- Suitable for clinical text retrieval

### 2. FastAPI + JWT
- Lightweight secure backend  
- Token authentication prevents unauthorized access  
- No patient data exposure

### 3. Streamlit Frontend
- Rapid medical dashboard  
- Session-based protected pages  
- No sidebar to mimic real hospital UI

### 4. Local T5 SLM
- Generates assistive summaries  
- Does not invent new medical facts  
- Keeps computation inside hospital network

---

## System Architecture

User Query
↓
MPNet Embedding
↓
FAISS Vector Search
↓
Top Similar Transcriptions
↓
(Optional) Local T5 Summarizer

---

## What I Learned

1. **RAG Workflow**
   - Building embeddings from real clinical text  
   - Indexing and semantic retrieval  
   - Importance of deduplication

2. **Healthcare Constraints**
   - Data must remain local  
   - AI should assist, not diagnose  
   - Explainability is crucial

3. **Streamlit State Handling**
   - Managing reruns with session state  
   - Preventing UI resets  
   - Building protected navigation

4. **SLM Limitations**
   - Lightweight models trade quality for privacy  
   - Need human-centered wording

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Build Index (One Time)
```bash
python embeddings/build_index.py
```

### 3. Start Backend
```bash
uvicorn backend.main:app --reload
```

### 4. Start Frontend
```bash
streamlit run app.py
```

Login
Username: doctor1
Password: pass123

---

## Why This Tech Stack?

**MPNet + FAISS**  
Chosen for semantic similarity instead of keyword search, enabling retrieval based on meaning of symptoms rather than exact words.

**FastAPI + JWT**  
Provides secure, lightweight authentication so only verified doctors can access records.

**Streamlit**  
Allows rapid creation of clinician-friendly interface without exposing internal APIs.

**T5 Small (Local SLM)**  
Used instead of cloud LLMs to ensure:
- No data leakage  
- Offline operation  
- Assistive summarization only

## Unique Aspects of This Implementation

- Deduplication before indexing to avoid biased retrieval  
- Doctor-friendly relevance labels instead of raw vector scores  
- On-demand SLM summarization  
- Session-safe Streamlit navigation  
- Fully offline RAG pipeline

