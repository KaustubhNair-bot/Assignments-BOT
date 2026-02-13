import chromadb
from pathlib import Path
from .config import VECTOR_DB_DIR, COLLECTION_NAME
from .embeddings import generate_embeddings
import os

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

_collection = None


def get_collection():
    """
    Get existing collection if available,
    otherwise create a new one.
    """
    global _collection

    if _collection is not None:
        return _collection

    Path(VECTOR_DB_DIR).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

    existing_collections = [col.name for col in client.list_collections()]

    if COLLECTION_NAME in existing_collections:
        print("✅ Existing vector collection found.")
        _collection = client.get_collection(COLLECTION_NAME)
    else:
        print("🚀 Creating new vector collection.")
        _collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "McDonald's Marketing RAG Collection"}
        )

    return _collection


def collection_has_data():
    """
    Check if collection already contains embeddings.
    """
    collection = get_collection()
    return collection.count() > 0


def add_chunks(chunks):
    """
    Add chunks only if collection is empty.
    Prevents duplicate embedding errors.
    """
    collection = get_collection()

    if collection.count() > 0:
        print("⚠️ Collection already populated. Skipping ingestion.")
        return

    print(f"📦 Adding {len(chunks)} chunks to vector store...")

    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embeddings = generate_embeddings(texts)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print("✅ Ingestion complete.")
