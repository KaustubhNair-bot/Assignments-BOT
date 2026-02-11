# Architecture Overview

## DP World RAG Chatbot — System Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit UI   │────▶│   FastAPI Backend  │────▶│   Groq LLM      │
│   (Frontend)     │◀────│   (API Layer)      │◀────│   (Generation)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │                          ▲
                                │                          │
                                ▼                          │
                        ┌──────────────────┐     ┌─────────────────┐
                        │   Redis Cache     │     │  Context Builder │
                        │   (Caching)       │     │  (RAG Pipeline)  │
                        └──────────────────┘     └─────────────────┘
                                                          ▲
                                                          │
                        ┌──────────────────┐     ┌─────────────────┐
                        │   Cohere API      │────▶│   Pinecone      │
                        │   (Embeddings)    │     │   (Vector DB)   │
                        └──────────────────┘     └─────────────────┘
```

### Data Flow

#### 1. Ingestion Pipeline
```
dpworld.com → Scraper → Content Cleaner → Document Loader → Text Splitter 
→ Cohere Embeddings → Pinecone Upsert
```

#### 2. Query Pipeline
```
User Query → Input Guardrails → Cohere Embed (query) → Pinecone Search 
→ Cohere Rerank → Context Builder → Groq LLM → Output Guardrails 
→ Response Formatter → User
```

### Module Breakdown

| Module         | Purpose                                        |
|----------------|------------------------------------------------|
| `config/`      | Settings, constants, logging                   |
| `src/scraper/`  | Web scraping DP World website                 |
| `src/ingestion/`| Document loading, chunking, embedding, indexing|
| `src/retrieval/` | Vector search, reranking, context building    |
| `src/generation/`| Groq LLM client, prompts, guardrails         |
| `src/chat/`     | Chat orchestration, sessions, history          |
| `src/api/`      | FastAPI routes, middleware, schemas            |
| `src/utils/`    | Shared utilities                               |
| `frontend/`     | Streamlit chat UI                              |

### Key Design Decisions

1. **Cohere for Embeddings + Reranking**: High-quality English embeddings with optional reranking for improved precision.
2. **Groq for LLM**: Ultra-fast inference with Llama models.
3. **Pinecone Serverless**: Zero-ops vector database with auto-scaling.
4. **Redis Caching**: Query and embedding caching to reduce API costs.
5. **Guardrails**: Input validation, prompt injection detection, output sanitization.
6. **Async FastAPI**: High-performance async API with proper middleware stack.
