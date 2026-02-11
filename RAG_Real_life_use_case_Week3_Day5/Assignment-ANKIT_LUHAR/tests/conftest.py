"""
DP World RAG Chatbot — Pytest Fixtures.

Shared fixtures for the entire test suite.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

# Set test environment variables before importing settings
os.environ["APP_ENV"] = "development"
os.environ["APP_DEBUG"] = "true"
os.environ["GROQ_API_KEY"] = "test-groq-key"
os.environ["COHERE_API_KEY"] = "test-cohere-key"
os.environ["PINECONE_API_KEY"] = "test-pinecone-key"


@pytest.fixture
def sample_text() -> str:
    """Return a sample text for testing."""
    return (
        "DP World is one of the world's largest port operators and logistics companies. "
        "Based in Dubai, UAE, the company operates marine and inland terminals, "
        "maritime services, logistics and ancillary services, and technology-driven "
        "trade solutions. DP World has a portfolio of over 80 operating marine and "
        "inland terminals across six continents. The company handles around 70 million "
        "containers per year and employs approximately 56,000 people worldwide. "
        "DP World's services include container handling, cargo logistics, maritime "
        "services, free trade zones, and digital trade platforms."
    )


@pytest.fixture
def sample_html() -> str:
    """Return sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DP World Services</title>
        <meta name="description" content="Explore DP World's global logistics services">
    </head>
    <body>
        <nav><a href="/">Home</a></nav>
        <main>
            <h1>Our Services</h1>
            <p>DP World provides end-to-end supply chain solutions that help
            businesses move their goods more efficiently across the globe.</p>
            <h2>Port Operations</h2>
            <p>We operate over 80 marine and inland terminals worldwide,
            handling containers, break-bulk, and Ro-Ro cargo.</p>
            <h2>Logistics</h2>
            <p>Our logistics services connect ports with hinterland markets,
            providing warehousing, transportation, and distribution solutions.</p>
        </main>
        <footer><p>© 2026 DP World</p></footer>
        <script>var x = 1;</script>
    </body>
    </html>
    """


@pytest.fixture
def sample_documents() -> list[dict]:
    """Return sample scraped document data."""
    return [
        {
            "url": "https://www.dpworld.com/about-us",
            "title": "About DP World",
            "text": (
                "DP World is a leading enabler of global trade. "
                "We operate marine and inland terminals across six continents."
            ) * 5,
            "meta_description": "Learn about DP World",
            "word_count": 100,
            "scraped_at": "2026-01-01T00:00:00Z",
        },
        {
            "url": "https://www.dpworld.com/services",
            "title": "Our Services",
            "text": (
                "DP World provides end-to-end supply chain solutions "
                "including port operations, logistics, and marine services."
            ) * 5,
            "meta_description": "DP World services",
            "word_count": 120,
            "scraped_at": "2026-01-01T00:00:00Z",
        },
    ]


@pytest.fixture
def mock_groq_client():
    """Return a mocked Groq client."""
    mock = MagicMock()
    mock.chat_completion.return_value = (
        "DP World offers a wide range of logistics services including "
        "port operations, container handling, and trade solutions."
    )
    return mock


@pytest.fixture
def mock_redis():
    """Return a mocked Redis client."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.ping.return_value = True
    return mock
