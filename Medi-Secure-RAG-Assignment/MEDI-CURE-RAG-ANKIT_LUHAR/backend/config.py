"""Application configuration — loads .env automatically."""
import os
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_env_path = os.path.join(os.path.dirname(__file__), os.pardir, ".env")
load_dotenv(dotenv_path=os.path.abspath(_env_path))


class Settings:
    """Simple settings container populated from environment variables."""

    def __init__(self):
        self.PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
        self.PINECONE_ENV: str = os.getenv("PINECONE_ENV", "us-east-1-aws")
        self.PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "medical-rag")
        self.COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "sqlite:///./medical_rag.db"
        )

    def __repr__(self):
        return (
            f"Settings(PINECONE_INDEX={self.PINECONE_INDEX_NAME}, "
            f"GROQ={'SET' if self.GROQ_API_KEY else 'UNSET'}, "
            f"COHERE={'SET' if self.COHERE_API_KEY else 'UNSET'})"
        )


_settings_instance = None


def get_settings() -> Settings:
    """Singleton accessor for application settings."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
