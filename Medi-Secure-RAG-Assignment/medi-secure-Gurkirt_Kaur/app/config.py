# Simple config for Medi-Secure
import os
from datetime import timedelta

class Settings:
    # Basic settings
    APP_NAME = "Medi-Secure"
    VERSION = "1.0.0"
    
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Data paths
    DATA_DIR = "./data"
    EMBEDDINGS_DIR = "./embeddings"
    
    # Model settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50

settings = Settings()
