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
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    
    # FAISS settings
    TOP_K_RESULTS = 5
    
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
