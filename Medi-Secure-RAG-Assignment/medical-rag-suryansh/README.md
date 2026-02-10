# Clinical Case Retrieval System (C²RS)

## Table of Contents

1.  Introduction
2.  Problem Statement
3.  Objectives
4.  Dataset Description
5.  Folder Structure
6.  System Architecture
7.  Technology Stack
8.  Implementation Workflow
9.  Security Design
10. RAG Pipeline Details
11. Summarization Module
12. Results & Screens
13. Limitations
14. Future Enhancements
15. Conclusion

------------------------------------------------------------------------

## 1. Introduction

Clinical notes in hospitals are mostly unstructured and difficult to
search.
This project builds a secure AI system that allows doctors to search
previous cases using semantic similarity (RAG) and optionally summarize
them using a local SLM.

------------------------------------------------------------------------

## 2. Problem Statement

-   Thousands of patient notes exist as free text\
-   Keyword search is ineffective\
-   Data cannot leave hospital premises\
-   Only authorized doctors must access records

------------------------------------------------------------------------

## 3. Objectives

-   Build offline semantic search over transcriptions
-   Protect access using JWT authentication
-   Provide doctor-friendly relevance display
-   Optional medical summary generation

------------------------------------------------------------------------

## 4. Dataset Description

| Attribute   | Value                          |
|------------|--------------------------------|
| Source     | Kaggle Medical Transcriptions  |
| Column Used| transcription                  |
| Size       | ~5k records                    |
| Type       | Unstructured clinical notes    |

------------------------------------------------------------------------

## 5. Folder Structure

    medical-rag/
    │
    ├── app.py                     # Landing & login page
    ├── pages/
    │   └── search.py              # Protected search dashboard
    │
    ├── backend/
    │   ├── main.py                # FastAPI endpoints
    │   ├── auth.py                # JWT authentication
    │   ├── rag.py                 # FAISS retrieval
    │   └── summarizer.py          # Local T5 summarizer
    │
    ├── embeddings/
    │   ├── build_index.py         # Create vector index
    │   ├── medical.index          # FAISS store
    │   └── texts.txt              # Raw knowledge base
    │
    ├── data/
    │   └── medical.csv            # Dataset
    │
    └── requirements.txt

------------------------------------------------------------------------

## 6. System Architecture

    +--------------------+
    | Doctor Login UI    |
    +---------+----------+
              |
              v
    +--------------------+
    | JWT Authentication |
    +---------+----------+
              |
              v
    +--------------------+
    | MPNet Embedding    |
    +---------+----------+
              |
              v
    +--------------------+
    | FAISS Vector Store |
    +---------+----------+
              |
              v
    +--------------------+
    | Retrieved Cases    |
    +---------+----------+
              |
              v
    +--------------------+
    | Optional T5 SLM    |
    +--------------------+

------------------------------------------------------------------------

## 7. Technology Stack

| Layer     | Tool       | Reason             |
|-----------|------------|--------------------|
| Backend   | FastAPI    | Lightweight API    |
| Security  | JWT        | Token auth         |
| Retrieval | FAISS      | Fast similarity    |
| Embedding | MPNet      | Semantic search    |
| Frontend  | Streamlit | Rapid UI           |
| SLM       | T5 Small   | Offline summary    |

------------------------------------------------------------------------

## 8. Implementation Workflow

1.  Load transcription column
2.  Generate MPNet embeddings
3.  Build FAISS index
4.  Doctor logs in
5.  Query encoded
6.  Similar cases retrieved
7.  Optional summarization

------------------------------------------------------------------------

## 9. Security Design

-   No external API usage
-   JWT based sessions
-   Local model inference
-   Protected pages

------------------------------------------------------------------------

## 10. RAG Pipeline Details

-   Dense vector search
-   Top-5 retrieval
-   Relevance labels
-   Evidence display

------------------------------------------------------------------------

## 11. Summarization Module

-   On-demand only
-   T5 text-to-text
-   No diagnosis generation

------------------------------------------------------------------------

## 12. Results

-   Accurate semantic matches
-   Fast response
-   Secure workflow

------------------------------------------------------------------------

## 13. Limitations

-   Lightweight SLM grammar noise
-   No entity extraction

------------------------------------------------------------------------

## 14. Future Enhancements

-   Structured summaries
-   Highlight terms
-   Role based access

------------------------------------------------------------------------

## 15. Conclusion

C²RS demonstrates privacy-preserving retrieval of medical notes with
assistive summarization.
