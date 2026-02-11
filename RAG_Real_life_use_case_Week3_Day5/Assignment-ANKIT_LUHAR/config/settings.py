"""
DP World RAG Chatbot — Application Settings.

All configuration is loaded from environment variables / .env file using
Pydantic BaseSettings.  Access the singleton via ``get_settings()``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised, validated application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────
    app_name: str = Field(default="dp-world-chatbot", description="Application name")
    app_env: str = Field(default="development", description="Environment (development|staging|production)")
    app_debug: bool = Field(default=False, description="Debug mode")
    app_host: str = Field(default="0.0.0.0", description="Server host")
    app_port: int = Field(default=8000, description="Server port")
    app_log_level: str = Field(default="INFO", description="Logging level")
    secret_key: str = Field(default="change-me", description="Secret key for sessions")

    # ── Groq LLM ────────────────────────────────────────────
    groq_api_key: str = Field(default="", description="Groq API key")
    groq_model_name: str = Field(default="llama-3.3-70b-versatile", description="Groq model")
    groq_max_tokens: int = Field(default=2048, description="Max generation tokens")
    groq_temperature: float = Field(default=0.3, description="Sampling temperature")

    # ── Cohere ──────────────────────────────────────────────
    cohere_api_key: str = Field(default="", description="Cohere API key")
    cohere_embed_model: str = Field(default="embed-english-v3.0", description="Embedding model")

    # ── Pinecone ────────────────────────────────────────────
    pinecone_api_key: str = Field(default="", description="Pinecone API key")
    pinecone_environment: str = Field(default="us-east-1", description="Pinecone environment")
    pinecone_index_name: str = Field(default="dpworld-knowledge-base", description="Index name")
    pinecone_cloud: str = Field(default="aws", description="Cloud provider")
    pinecone_region: str = Field(default="us-east-1", description="Region")

    # ── Redis ───────────────────────────────────────────────
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ttl: int = Field(default=3600, description="Default TTL in seconds")

    # ── Scraper ─────────────────────────────────────────────
    scraper_base_url: str = Field(default="https://www.dpworld.com", description="Base URL to scrape")
    scraper_max_pages: int = Field(default=500, description="Max pages to scrape")
    scraper_delay_seconds: float = Field(default=2.0, description="Delay between requests")
    scraper_user_agent: str = Field(default="DPWorldBot/1.0", description="User-Agent header")

    # ── Rate Limiting ───────────────────────────────────────
    rate_limit_requests: int = Field(default=30, description="Requests per window")
    rate_limit_window_seconds: int = Field(default=60, description="Window duration in seconds")

    # ── Frontend ────────────────────────────────────────────
    streamlit_port: int = Field(default=8501, description="Streamlit port")
    api_base_url: str = Field(default="http://localhost:8000", description="API base URL")

    # ── Validators ──────────────────────────────────────────
    @field_validator("app_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return upper

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def redis_url(self) -> str:
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()
