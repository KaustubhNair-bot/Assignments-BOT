# Troubleshooting Guide

## Common Issues & Fixes

### 1. "Pinecone index not found" or "Dimension Mismatch"

If you see errors about dimension mismatch (e.g. 1024 vs 2048), you need to recreate the index.

**Fix:**
```bash
# This script deletes and recreates the index with correct dimensions
python scripts/seed_pinecone.py
```

### 2. "No documents found" or Empty Responses

If the chatbot says "I don't have information about that", the vector database might be empty.

**Fix:**
```bash
# Run the full ingestion pipeline
python scripts/ingest_data.py --chunk-size 512
```

### 3. Rate Limit Errors (429)

If you see `trial token rate limit exceeded` during ingestion:
- The script now has auto-retry logic. Just let it run.
- If it fails completely, wait 60 seconds and try again.

### 4. Search returning irrelevant results

- Increase `top_k` in `config/constants.py` (default is 5).
- Adjust `SIMILARITY_THRESHOLD` (default is 0.35).

## Deployment & Production

### API Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Resetting the Environment
To completely reset and start fresh:

```bash
# 1. Delete vector index
python -c "from src.ingestion.pinecone_indexer import PineconeIndexer; PineconeIndexer().pc.delete_index('dpworld-knowledge-base')"

# 2. Re-seed index
python scripts/seed_pinecone.py

# 3. Re-ingest data
python scripts/ingest_data.py
```
