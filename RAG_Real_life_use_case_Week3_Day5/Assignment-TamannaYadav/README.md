# Tesla RAG System

A Retrieval-Augmented Generation (RAG) system for Tesla Policy and Product Knowledge Assistant.

## Overview

This enterprise-grade RAG system answers user queries using Tesla documents (PDFs), preventing hallucinations by grounding responses in retrieved context while maintaining Tesla's professional engineering and corporate tone.

## Architecture

```
Assignment-TamannaYadav/
├── app/                 # Streamlit frontend
│   ├── streamlit_app.py # Main Streamlit application
│   ├── auth.py          # Mock authentication
│   └── ui_components.py # Tesla-themed UI components
├── config/              # Configuration settings
├── ingestion/           # PDF loading and text extraction
├── preprocessing/       # Text cleaning and normalization
├── chunking/            # Recursive text splitting
├── embeddings/          # Embedding generation
├── vector_db/           # FAISS index management
├── retrieval/           # Similarity search
├── prompts/             # Tesla persona templates
├── rag/                 # RAG orchestration
├── evaluation/          # Benchmarking and metrics
├── utils/               # Helper functions
├── data/                # Tesla PDF documents
├── main.py              # CLI entry point
└── requirements.txt     # Dependencies
```

## Installation

1. Clone the repository and navigate to the project:
```bash
cd tesla_rag_project
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Build the FAISS index (generates embeddings)
python scripts/build_index.py

# Run the evaluation
python -m evaluation.evaluate_rag

# Start the Streamlit app
streamlit run app/streamlit_app.py
```

---

## Usage

### Build the Index
First, build the FAISS index from Tesla documents:
```bash
python scripts/build_index.py
```

Or using main.py:
```bash
python main.py --mode build
```

To force rebuild:
```bash
python main.py --mode build --force
```

### Interactive Mode
Start an interactive session:
```bash
python main.py --mode interactive
```

### Single Query
Process a single query:
```bash
python main.py --mode query --query "What is Tesla's privacy policy?"
```

### Evaluation
Run evaluation on sample queries:
```bash
python main.py --mode evaluate
```

### Advanced Options
```bash
python main.py --mode interactive \
    --top-k 5 \
    --temperature 0.1 \
    --top-p 0.9
```

## Configuration

Key parameters in `config/settings.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| CHUNK_SIZE | 600 | Target chunk size in tokens |
| CHUNK_OVERLAP | 120 | Overlap between chunks |
| TOP_K | 5 | Number of chunks to retrieve |
| TEMPERATURE | 0.1 | LLM generation temperature |
| TOP_P | 0.9 | Top-p sampling parameter |
| SIMILARITY_THRESHOLD | 0.3 | Minimum similarity score |

## Components

### Document Ingestion
- Loads PDF files using `pdfplumber`
- Extracts text with page-level metadata
- Supports single files or directories

### Text Preprocessing
- Removes headers, footers, and noise
- Normalizes whitespace
- Preserves semantic structure

### Chunking
- Recursive character text splitting
- Configurable chunk size and overlap
- Maintains document metadata

### Embeddings
- Uses `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional dense vectors
- Batch processing support

### Vector Database
- FAISS with cosine similarity (Inner Product)
- Persistent storage to disk
- Efficient similarity search

### Retrieval
- Query embedding generation
- Top-k similarity search
- Configurable threshold filtering

### Prompt Engineering
- Tesla brand persona
- Grounded response generation
- Hallucination prevention

### RAG Orchestration
- Combines retrieval and generation
- Groq LLM integration
- Configurable parameters

### Evaluation & Benchmarking
- Latency metrics (P50, P95, P99)
- Retrieval quality metrics
- JSON/CSV report generation
- RAG vs Non-RAG comparison
- Temperature experimentation

## Evaluation Framework

### Running Comprehensive Benchmarks
```bash
python main.py --mode benchmark
```

Or use the dedicated benchmark runner:
```bash
python evaluation/run_benchmark.py --mode all
```

### Benchmark Modes
| Mode | Description |
|------|-------------|
| `full` | Run all experiment configurations |
| `rag-comparison` | Compare RAG vs Non-RAG baseline |
| `temperature` | Test temperature variations |
| `all` | Run all benchmarks and generate report |

### Test Dataset
10 Tesla-related queries across 3 categories:

| Category | Count | Examples |
|----------|-------|----------|
| **Policy** | 3 | Service terms, dispute resolution |
| **Technical** | 4 | Safety features, charging, touchscreen |
| **Privacy/Legal** | 3 | Data collection, privacy rights |

### Metrics Computed

| Metric | Description |
|--------|-------------|
| **Relevance Score** | Semantic similarity between answer and retrieved chunks |
| **Groundedness Score** | % of answer sentences supported by context |
| **Hallucination Rate** | Proportion of unsupported claims |
| **Retrieval Precision** | Quality of top-k retrieved chunks |
| **Response Consistency** | Stability across multiple runs |

### Experiment Configurations

| Configuration | Temperature | Top-P | RAG |
|---------------|-------------|-------|-----|
| RAG_Factual | 0.0 | 0.9 | ✓ |
| RAG_Balanced | 0.3 | 0.9 | ✓ |
| RAG_Creative | 0.8 | 0.9 | ✓ |
| RAG_HighTopP | 0.1 | 0.95 | ✓ |
| NoRAG_Baseline | 0.1 | 0.9 | ✗ |

### Output Files
Benchmarks generate the following in `benchmark_results/`:
- `benchmark_YYYYMMDD_HHMMSS.json` - Full results
- `benchmark_YYYYMMDD_HHMMSS.csv` - Tabular results
- `BENCHMARK_REPORT.md` - Comprehensive analysis
- `benchmark_analysis.json` - Structured conclusions

---

## 📊 Evaluation Results - RAG vs Base LLM

### Summary Comparison

| Metric | RAG System | Base LLM | Winner | Improvement |
|--------|:----------:|:--------:|:------:|:-----------:|
| **Answer Relevance** | 0.980 | 1.000 | Tie | - |
| **Faithfulness** | 0.396 | 0.000 | **RAG** | ∞ |
| **Hallucination Risk** | 0.201 | 0.320 | **RAG** | **37% lower** |
| **ROUGE-L** | 0.215 | 0.000 | **RAG** | ∞ |
| **MRR** | 0.500 | 0.000 | **RAG** | ∞ |

### Key Finding

> **RAG system shows 37% lower hallucination risk** (0.201 vs 0.320) because answers are grounded in actual Tesla documents, not fabricated from training data.

### Why RAG Outperforms Base LLM

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG vs Base LLM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BASE LLM (Without RAG):                                         │
│  ├── Relies only on training data (knowledge cutoff)            │
│  ├── May hallucinate specific details                           │
│  ├── Generic knowledge                                          │
│  └── No grounding in actual documents                           │
│                                                                  │
│  RAG SYSTEM (With Retrieval):                                    │
│  ├── Retrieves relevant chunks from Tesla PDFs                  │
│  ├── Answers grounded in real documents                         │
│  ├── Cites specific sources                                     │
│  └── 37% lower hallucination risk                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Metrics Explained

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| **Answer Relevance** | Does the answer address the query? | Basic quality check |
| **Faithfulness** | Is the answer grounded in retrieved context? | RAG's key advantage |
| **Hallucination Risk** | Does the response contain fabricated info? | Critical for enterprise use |
| **ROUGE-L** | Text overlap with source documents | Measures grounding quality |
| **MRR** | Rank of first relevant retrieved document | Retriever effectiveness |

---

### Key Findings

#### Why RAG Reduces Hallucinations
1. **Context Grounding** - Retrieval provides factual anchors
2. **Explicit Instructions** - Persona prompt forbids fabrication
3. **Source Verification** - Retrieved chunks enable fact-checking
4. **Reduced Parametric Reliance** - Uses current documents vs training data

#### Why Low Temperature Improves Accuracy
1. **Deterministic Sampling** - Selects most probable tokens
2. **Consistent Outputs** - Reproducible responses
3. **Reduced Exploration** - Stays close to high-confidence predictions

#### Tesla Persona Impact
1. **Role Definition** - Sets professional expectations
2. **Explicit Constraints** - Prevents hallucination
3. **Fallback Behavior** - Handles uncertainty gracefully
4. **Tone Consistency** - Maintains brand voice

## Streamlit Frontend

### Running the Web Application

Start the Streamlit app:
```bash
streamlit run app/streamlit_app.py
```

The app will open at `http://localhost:8501`

### Login Credentials (Demo)

| Username | Password |
|----------|----------|
| `tesla_admin` | `tesla123` |
| `demo_user` | `demo123` |

### Frontend Features

1. **Mock Authentication**
   - Secure login page
   - Session management
   - Logout functionality

2. **Chat Interface**
   - Real-time query processing
   - Conversation history
   - Tesla-styled responses

3. **Retrieved Context Panel**
   - View top-k retrieved chunks
   - Source document names
   - Similarity scores
   - Verify answer grounding

4. **Generation Controls (Sidebar)**
   - Temperature slider (0.0 - 1.0)
   - Top-P slider (0.5 - 1.0)
   - Top-K dropdown (3, 5, 7, 10)

5. **Tesla-Themed UI**
   - Clean, minimalistic design
   - Tesla brand colors
   - Professional layout

### Frontend Structure

```
app/
├── streamlit_app.py    # Main application
├── auth.py             # Authentication module
└── ui_components.py    # Reusable UI components
```

## API Keys

This system requires a Groq API key for LLM inference:
1. Sign up at [Groq Console](https://console.groq.com)
2. Generate an API key
3. Set as environment variable: `export GROQ_API_KEY="your-key"`

## License

This project is for educational purposes.
