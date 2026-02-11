# Deployment Guide

## DP World RAG Chatbot — Deployment

### Prerequisites

- Python 3.11+
- API keys for: Groq, Cohere, Pinecone
- Redis (recommended for production)

---

### 1. Manual Deployment

#### Step 1: Clone & Setup

```bash
# Clone the repository
git clone <repo-url>
cd dp-world-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your API keys
# Ensure you set APP_ENV=production for live deployments
nano .env
```

#### Step 3: Data Pipeline

Before starting the app, ensure your data is fresh:

```bash
# Scrape data from DP World site
python scripts/scrape_dpworld.py --max-pages 100

# Create Pinecone index & ingest data
python scripts/seed_pinecone.py
python scripts/ingest_data.py
```

#### Step 4: Run Services

We use `make` commands for convenience, but here are the underlying commands for production:

**Backend (API):**
```bash
# Run with 4 workers for production load handling
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend (Streamlit):**
```bash
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

---

### 2. Production Security Checklist

- [ ] Set `APP_ENV=production`
- [ ] Set `APP_DEBUG=false`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` to allow only your frontend domain
- [ ] Enable HTTPS (e.g., using Nginx or Cloudflare)
- [ ] Set a password for Redis if used publicly

### 3. Recommended Production Stack

For a robust deployment on a VPS (AWS EC2, DigitalOcean, etc.), we recommend:

```
[ Internet ]
      │
[ Nginx / Load Balancer (SSL + Rate Limiting) ]
      │
      ├── /api/*  →  Uvicorn (FastAPI Backend)
      │
      └── /*      →  Streamlit (Frontend App)
```

**Nginx Configuration Snippet:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. Monitoring & Logging

- **Logs**: The application uses structured logging. Ensure stdout/stderr are captured by systemd or a logging agent.
- **Health Check**: Monitor `GET /api/v1/health` for uptime status.
