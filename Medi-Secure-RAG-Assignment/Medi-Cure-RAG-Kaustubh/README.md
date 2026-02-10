# MediCure RAG System

A secure Retrieval Augmented Generation (RAG) system designed for healthcare professionals to search through medical transcriptions using semantic search. The system ensures complete patient data privacy by processing all data locally.

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Solution Architecture](#solution-architecture)
4. [Features](#features)
5. [Technology Stack](#technology-stack)
6. [Project Structure](#project-structure)
7. [Setup and Installation](#setup-and-installation)
8. [Running the Application](#running-the-application)
9. [Usage Guide](#usage-guide)
10. [API Documentation](#api-documentation)
11. [Security Considerations](#security-considerations)
12. [Author](#author)

---

## Overview

MediCure RAG is an AI-powered medical case search system that enables doctors to find similar patient cases based on symptoms, conditions, or medical procedures. The system uses vector embeddings and semantic search to retrieve relevant medical transcriptions from a knowledge base of approximately 5,000 medical records.

---

## Problem Statement

A private hospital with thousands of unstructured patient notes required a secure AI system that allows doctors to:

1. **Search for past cases with similar symptoms** - Using RAG (Retrieval Augmented Generation) for intelligent semantic search
2. **Protect Patient Data** - Ensuring no data leaves the system, with access restricted to authorized doctors only through JWT authentication

---

## Solution Architecture

The system is built with a three-tier architecture:

```
+-------------------+     +-------------------+     +-------------------+
|   Streamlit UI    |---->|   FastAPI Backend |---->|   Data Layer      |
|   (Port 8501)     |     |   (Port 8000)     |     |                   |
+-------------------+     +-------------------+     +-------------------+
                                   |
                    +--------------+--------------+
                    |              |              |
              +----------+  +----------+  +----------+
              |   JWT    |  |   RAG    |  | MongoDB  |
              |   Auth   |  |  Engine  |  |  Store   |
              +----------+  +----------+  +----------+
                                 |
                    +------------+------------+
                    |            |            |
              +----------+  +----------+  +----------+
              |  FAISS   |  | Sentence |  |   CSV    |
              |  Index   |  | Transf.  |  |   Data   |
              +----------+  +----------+  +----------+
```

### Components

1. **Streamlit UI**: A modern web interface for doctors to login and search medical cases
2. **FastAPI Backend**: REST API with JWT authentication protecting all search endpoints
3. **RAG Engine**: Combines FAISS vector indexing with sentence-transformers for semantic search
4. **MongoDB**: Stores document metadata and user credentials (with file-based fallback)
5. **FAISS Index**: Efficient similarity search on vector embeddings

---

## Features

### Semantic Search (RAG)
- AI-powered search using sentence-transformers embeddings
- FAISS-based vector similarity search for fast retrieval
- Filter results by medical specialty
- Ranked results with similarity scores
- Support for natural language queries

### Secure Authentication
- JWT (JSON Web Token) based authentication
- Password hashing using bcrypt
- Protected API endpoints accessible only to authenticated users
- Configurable token expiration

### Local Data Processing
- All embedding generation happens locally using sentence-transformers
- FAISS index stored on local disk
- MongoDB runs locally (or falls back to file-based storage)
- No external API calls - all patient data remains on-premises

### User Interface
- Clean, professional Streamlit-based web interface
- Login system with session management
- Expandable result cards for detailed case viewing
- Real-time search statistics
- Specialty-based filtering

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend Framework | FastAPI | REST API with automatic documentation |
| Frontend | Streamlit | Interactive web interface |
| Authentication | JWT + bcrypt | Secure user authentication |
| Vector Database | FAISS | Efficient similarity search |
| Embeddings | sentence-transformers | Generate text embeddings locally |
| Document Storage | MongoDB | Store transcriptions and metadata |
| Data Processing | Pandas, NumPy | Data manipulation and processing |

---

## Project Structure

```
Medi-Cure-RAG-Kaustubh/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application and endpoints
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models
│   ├── auth.py              # JWT authentication logic
│   ├── database.py          # MongoDB connection and operations
│   └── rag_engine.py        # FAISS-based RAG implementation
├── data/
│   └── mtsamples.csv        # Medical transcriptions dataset
├── faiss_index/             # FAISS index files (auto-generated)
│   ├── index.faiss          # Vector index
│   ├── id_mapping.pkl       # ID to case mapping
│   └── docs_cache.pkl       # Document cache
├── streamlit_app.py         # Streamlit UI application
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
├── .env.example             # Example environment file
├── .gitignore               # Git ignore rules
├── users.json               # User storage (fallback if no MongoDB)
└── README.md                # This file
```

---

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- MongoDB (optional - system falls back to file-based storage)
- Git

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Medi-Cure-RAG-Kaustubh
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment file and modify as needed:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```env
# Security - Generate a new secret key for production
JWT_SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=medicure_rag

# Paths
FAISS_INDEX_PATH=./faiss_index
DATA_PATH=./data/mtsamples.csv

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Server Configuration
API_HOST=127.0.0.1
API_PORT=8000
STREAMLIT_PORT=8501
```

### Step 5: Setup MongoDB (Optional)

If you have MongoDB installed:

```bash
mongod --dbpath /path/to/data/directory
```

Or using Docker:

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

Note: If MongoDB is not available, the system will automatically use file-based storage.

### Step 6: Prepare the Dataset

Ensure the medical transcriptions dataset is placed at `data/mtsamples.csv`. The dataset should contain the following columns:
- `transcription`: The medical transcription text
- `medical_specialty`: The medical specialty category
- `sample_name`: Name/title of the case
- `keywords`: Associated keywords
- `description`: Brief description

---

## Running the Application

The application requires two services to run simultaneously:

### Terminal 1: Start the API Server

```bash
cd Medi-Cure-RAG-Kaustubh
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

On first startup, the system will:
1. Connect to MongoDB (or initialize file-based storage)
2. Create demo user accounts
3. Load the medical transcriptions dataset
4. Generate embeddings using sentence-transformers (approximately 2-5 minutes)
5. Build and save the FAISS index

Subsequent startups will be faster as the index is loaded from disk.

### Terminal 2: Start the Streamlit UI

```bash
cd Medi-Cure-RAG-Kaustubh
source venv/bin/activate
streamlit run streamlit_app.py --server.port 8501
```

### Access Points

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| API Documentation | http://localhost:8000/docs |
| API Health Check | http://localhost:8000/health |

---

## Usage Guide

### Login

Use one of the demo accounts to access the system:

| Username | Password | Specialty |
|----------|----------|-----------|
| dr.smith | doctor123 | Cardiology |
| dr.jones | doctor123 | General Surgery |
| dr.patel | doctor123 | Internal Medicine |

### Searching for Cases

1. Login with valid credentials
2. Enter a search query describing symptoms, conditions, or procedures
3. Optionally select a specialty filter
4. Choose the number of results to return (5, 10, 15, or 20)
5. Click "Search" to find similar cases
6. Expand result cards to view full transcriptions

### Example Queries

- "Patient presenting with chest pain and shortness of breath"
- "Diabetes management with insulin therapy"
- "Knee replacement surgery post-operative care"
- "Pediatric fever and respiratory symptoms"

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new doctor account |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get current user information |

### Search Endpoints (Requires Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search` | Search for similar medical cases |
| GET | `/specialties` | Get list of available specialties |
| GET | `/stats` | Get system statistics |

### Example API Request

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dr.smith&password=doctor123"

# Search (with token)
curl -X POST "http://localhost:8000/search" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "chest pain", "top_k": 5}'
```

---

## Security Considerations

### Data Privacy

1. **Local Processing**: All text embeddings are generated using a locally running sentence-transformers model. No data is sent to external APIs.

2. **On-Premises Storage**: The FAISS index and MongoDB database are stored locally. Patient data never leaves the system.

3. **No LLM Integration**: The system intentionally does not integrate with cloud-based LLMs to prevent any possibility of data leakage.

### Authentication Security

1. **Password Hashing**: All passwords are hashed using bcrypt before storage.

2. **JWT Tokens**: Access tokens expire after a configurable period (default: 30 minutes).

3. **Protected Endpoints**: All search functionality requires valid authentication.

### Production Recommendations

For production deployment:

1. Generate a strong, unique `JWT_SECRET_KEY`
2. Use HTTPS/TLS for all communications
3. Configure proper MongoDB authentication
4. Implement rate limiting on API endpoints
5. Set up proper logging and monitoring
6. Regular security audits and updates

---

## Dataset

This system uses the Medical Transcriptions Dataset from Kaggle:
- Source: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
- Records: Approximately 5,000 medical transcriptions
- Specialties: 40+ medical specialty categories
- Content: Detailed patient notes, procedures, diagnoses, and treatment plans

---

## Technical Implementation Details

### RAG Pipeline

1. **Data Ingestion**: Medical transcriptions are loaded from CSV and processed
2. **Embedding Generation**: Each document is converted to a 384-dimensional vector using the `all-MiniLM-L6-v2` model
3. **Index Building**: Vectors are indexed using FAISS for efficient similarity search
4. **Query Processing**: User queries are embedded and compared against the index
5. **Result Ranking**: Results are ranked by cosine similarity and returned with metadata

### Embedding Model

The system uses `all-MiniLM-L6-v2` from sentence-transformers:
- Dimension: 384
- Model Size: ~80MB
- Speed: Fast inference suitable for real-time search
- Quality: Good balance between performance and accuracy

---

## Author

**Kaustubh Nair**

---

## License

This project is licensed under the MIT License.
