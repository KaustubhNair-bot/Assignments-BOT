"""
Configuration settings for the Secure Medical RAG System
Contains all environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # Groq Configuration (for text generation)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "llama-3.1-8b-instant"
    
    # Data Configuration
    DATA_PATH = "data/mtsamples.csv"
    VECTOR_STORE_PATH = "data/vector_store.faiss"
    CHUNK_SIZE = 500  # Characters per chunk
    CHUNK_OVERLAP = 50  # Characters overlap between chunks
    
    # RAG Configuration
    EMBEDDING_MODEL = "dmis-lab/biobert-base-cased-v1.1"
    TOP_K_RETRIEVAL = 3  # Number of similar documents to retrieve
    
    # UI Configuration
    APP_TITLE = "MEdi-Secure"
    APP_DESCRIPTION = "AI-powered medical case search with patient data protection"

# Demo users (hardcoded for simplicity)
DEMO_USERS = {
    "dr_smith": {
        "password": "password123",
        "name": "Dr. Smith",
        "specialization": "Cardiology"
    },
    "dr_johnson": {
        "password": "password123", 
        "name": "Dr. Johnson",
        "specialization": "Neurology"
    },
    "dr_wilson": {
        "password": "password123",
        "name": "Dr. Wilson", 
        "specialization": "General Medicine"
    }
}
