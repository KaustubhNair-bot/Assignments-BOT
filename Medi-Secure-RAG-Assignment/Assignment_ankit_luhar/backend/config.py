import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_ENV: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "medical-rag"
    COHERE_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./medical_rag.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
