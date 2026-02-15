import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

# RAG Settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RETRIEVER_K = 3

# Model Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"
