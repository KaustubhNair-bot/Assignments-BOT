"""Application settings and configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration for the MediSecure RAG application."""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Data files
    RAW_DATA_PATH = BASE_DIR / "mtsamples.csv"
    FAISS_INDEX_PATH = DATA_DIR / "faiss_index"
    METADATA_PATH = DATA_DIR / "metadata.pkl"
    
    # Embedding model (runs locally - no data leaves the system)
    # Upgraded to all-mpnet-base-v2 for better semantic understanding
    # Why: Higher quality embeddings (768 dim vs 384), better for medical text
    EMBEDDING_MODEL = "all-mpnet-base-v2"
    EMBEDDING_DIMENSION = 768
    
    # Chunking settings
    # Why: Long transcriptions split into smaller chunks for better retrieval precision
    CHUNK_SIZE = 512  # Characters per chunk
    CHUNK_OVERLAP = 50  # Overlap to preserve context at boundaries
    MIN_CHUNK_SIZE = 100  # Minimum chunk size to keep
    
    # FAISS settings
    # Using IndexFlatIP (Inner Product) with normalized vectors = Cosine Similarity
    # Why: Cosine similarity is scale-invariant, standard for text similarity
    TOP_K_RESULTS = 5
    SIMILARITY_METRIC = "cosine"  # Options: cosine, l2
    
    # Groq API settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "llama-3.1-8b-instant"
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "medi-secure-default-secret-key-change-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Application settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Demo users (in production, use a proper database)
    DEMO_USERS = {
        "dr.smith": {
            "password_hash": "$2b$12$6vTauzonw1QN6p3P.SYcmOlOOqW2SwP8YvK10vLFD3fmYcmMzUezi",  # password: doctor123
            "name": "Dr. John Smith",
            "specialty": "Internal Medicine",
            "license_id": "MD-12345"
        },
        "dr.jones": {
            "password_hash": "$2b$12$6vTauzonw1QN6p3P.SYcmOlOOqW2SwP8YvK10vLFD3fmYcmMzUezi",  # password: doctor123
            "name": "Dr. Sarah Jones",
            "specialty": "Cardiology",
            "license_id": "MD-67890"
        }
    }
