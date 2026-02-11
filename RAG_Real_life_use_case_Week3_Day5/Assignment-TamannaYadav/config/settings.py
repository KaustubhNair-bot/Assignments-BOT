"""
Configuration settings for Tesla RAG system.
Centralized parameters for easy experimentation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db" / "faiss_index"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Chunking parameters
CHUNK_SIZE = 600  # tokens (500-800 range)
CHUNK_OVERLAP = 120  # tokens (100-150 range)
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

# Embedding parameters
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Retrieval parameters
TOP_K = 5
SIMILARITY_THRESHOLD = 0.3

# LLM parameters (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.1
TOP_P = 0.9
MAX_TOKENS = 1024

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
