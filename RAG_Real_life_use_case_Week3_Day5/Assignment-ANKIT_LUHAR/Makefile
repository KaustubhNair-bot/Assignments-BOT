# ============================================================
# DP World RAG Chatbot — Makefile
# ============================================================

.PHONY: help install dev run api frontend scrape ingest test lint format \
        docker-build docker-up docker-down clean health

# ── Defaults ────────────────────────────────────────────────
PYTHON   ?= python3
PIP      ?= pip
UVICORN  ?= uvicorn
STREAMLIT?= streamlit

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ───────────────────────────────────────────────────
install: ## Install production dependencies
	$(PIP) install -r requirements.txt

dev: ## Install dev dependencies
	$(PIP) install -e ".[dev]"

# ── Run Services ────────────────────────────────────────────
run: api ## Alias for api

api: ## Start FastAPI server
	$(UVICORN) src.api.main:app --host 0.0.0.0 --port 8000 --reload

frontend: ## Start Streamlit frontend
	$(STREAMLIT) run frontend/app.py --server.port 8501

# ── Data Pipeline ───────────────────────────────────────────
scrape: ## Run DP World web scraper
	$(PYTHON) scripts/scrape_dpworld.py

ingest: ## Run data ingestion pipeline
	$(PYTHON) scripts/ingest_data.py

seed: ## Initialize Pinecone index
	$(PYTHON) scripts/seed_pinecone.py

# ── Quality ─────────────────────────────────────────────────
test: ## Run all tests
	pytest tests/ -v --tb=short

test-unit: ## Run unit tests only
	pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests
	pytest tests/integration/ -v --tb=short

test-e2e: ## Run end-to-end tests
	pytest tests/e2e/ -v --tb=short

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint: ## Lint with ruff
	ruff check src/ tests/

format: ## Format with black
	black src/ tests/ config/ scripts/

typecheck: ## Run mypy type checker
	mypy src/



# ── Utilities ───────────────────────────────────────────────
health: ## Run health check
	$(PYTHON) scripts/health_check.py

clean: ## Clean cache and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov .coverage dist build
