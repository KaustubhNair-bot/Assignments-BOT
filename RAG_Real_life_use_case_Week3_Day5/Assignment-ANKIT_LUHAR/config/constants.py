"""
DP World RAG Chatbot — Application Constants.

Centralised, immutable values used across the application.
"""

from __future__ import annotations

# ── Embedding dimensions ────────────────────────────────────
COHERE_EMBED_DIMENSION = 1024  # embed-english-v3.0

# ── Chunking defaults ───────────────────────────────────────
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64
MAX_CHUNK_SIZE = 2048
MIN_CHUNK_SIZE = 100

# ── Retrieval ───────────────────────────────────────────────
DEFAULT_TOP_K = 5
MAX_TOP_K = 20
SIMILARITY_THRESHOLD = 0.35

# ── LLM ─────────────────────────────────────────────────────
MAX_CONTEXT_TOKENS = 6000
MAX_HISTORY_TURNS = 10
SYSTEM_ROLE = "system"
USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"

# ── Chat ────────────────────────────────────────────────────
MAX_MESSAGE_LENGTH = 2000
SESSION_EXPIRY_HOURS = 24
MAX_SESSIONS_PER_USER = 5

# ── Scraper ─────────────────────────────────────────────────
ALLOWED_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}
SKIP_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".mp4", ".zip", ".exe"}
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2

# ── API ─────────────────────────────────────────────────────
API_V1_PREFIX = "/api/v1"
API_TITLE = "DP World RAG Chatbot API"
API_DESCRIPTION = "Production-ready RAG chatbot for DP World logistics services"
API_VERSION = "1.0.0"

# ── Redis cache key prefixes ────────────────────────────────
CACHE_PREFIX_QUERY = "dpw:query:"
CACHE_PREFIX_SESSION = "dpw:session:"
CACHE_PREFIX_EMBEDDING = "dpw:embed:"

# ── Metadata keys ───────────────────────────────────────────
META_SOURCE_URL = "source_url"
META_TITLE = "title"
META_SECTION = "section"
META_SCRAPED_AT = "scraped_at"
META_CHUNK_INDEX = "chunk_index"
