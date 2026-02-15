import os
from langchain_community.vectorstores import FAISS
from config.settings import FAISS_INDEX_PATH

def create_vector_store(chunks, embeddings):
    """
    Creates a FAISS vector store from chunks and embeddings, and saves it locally.
    """
    print("Creating vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"Vector store saved to {FAISS_INDEX_PATH}")
    return vector_store

def load_vector_store(embeddings):
    """
    Loads the FAISS vector store from the local path.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        print("Vector store not found. Please run the ingestion process.")
        return None
    
    print(f"Loading vector store from {FAISS_INDEX_PATH}...")
    vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return vector_store

if __name__ == "__main__":
    # Test pipeline
    from rag.loader import load_documents
    from rag.chunking import split_documents
    from rag.embeddings import get_embedding_model
    
    # Ingest
    docs = load_documents()
    chunks = split_documents(docs)
    embed_model = get_embedding_model()
    create_vector_store(chunks, embed_model)
