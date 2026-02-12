
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware."""
    settings = get_settings()

    origins = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
    ]

    if settings.is_production:
        origins = [
            "https://dpworld-chatbot.example.com",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
