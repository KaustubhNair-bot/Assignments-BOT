# Medi-Secure: The Private Hospital Assistant

A secure, context-aware RAG application for medical professionals to search patient history and receive AI-generated insights.
**[View Demo on Streamlit Cloud](https://gurkirt-bot-medi-secure-rag-frontendmain-yklv75.streamlit.app/)**

---

## 🚀 Key Improvements & Features
We have upgraded the RAG pipeline from a basic keyword search to a semantic medical assistant. The full technical details are available in the **[RAG Improvement Report](docs/improvement_report.md)**.

### 1. ✂️ Smarter Chunking (Semantic Segmentation)
-   **Old Approach**: Fixed-size character splitting (e.g., every 500 chars), often cutting sentences in half and losing context.
-   **New Approach**: **Semantic Segmentation** using **Spacy**.
-   **Impact**: Respects sentence boundaries and medical context, ensuring retrieved chunks contain complete clinical thoughts (e.g., "Patient has severe chest pain").

### 2. 🧠 Medical Brain Transplant (BioBERT)
-   **Old Approach**: Generic embeddings (`all-MiniLM`) that treated medical terms like standard English.
-   **New Approach**: Integrated **BioBERT (`dmis-lab/biobert-base-cased-v1.1`)**, a model pre-trained on biomedical corpora (PubMed/PMC).
-   **Impact**:The system now understands that "Myocardial Infarction" and "Heart Attack" are semantically identical, whereas a generic model might miss the connection.

### 3. 🎯 Precision Search (FAISS + Cosine Similarity)
-   **Old Approach**: Basic distance metrics.
-   **New Approach**: **FAISS** index with **Cosine Similarity** (Inner Product on normalized vectors).
-   **Impact**: Filters out irrelevant noise by measuring semantic alignment (angle) rather than just keyword overlap, reducing hallucinations.

---

## 📊 Evaluation & Performance
We benchmarked the Enhanced RAG against a Base LLM. Full details are in the **[Evaluation Report](docs/evaluation_report.md)**.

| Metric | Base LLM | Enhanced RAG |
| :--- | :--- | :--- |
| **Accuracy** | 80% (General Knowledge) | 60% (Strictly grounded in data) |
| **Faithfulness** | Low (Hallucination Risk) | **High (Refuses to guess)** |
| **Safety** | Low | **High** |

> **Trade-off**: The RAG system prioritizes **safety**. It may truthfully say "I don't know" (lower accuracy on general trivia) rather than hallucinating an answer, making it suitable for clinical settings.

---

## 📂 Project Structure

```text
secure-medical-rag/
├── app/
│   ├── auth.py                 # JWT authentication logic
│   └── config.py               # Configuration settings
│
├── rag/
│   ├── rag.py                  # RAG pipeline
│   ├── data_loader.py          # Spacy-based Semantic Chunking
│   └── vector_store.py         # BioBERT Embedding Generation & FAISS
│
├── frontend/
│   └── main.py                 # Unified Chat & Evaluation Dashboard
│
├── evaluation/                 # Benchmarking Tools
│   ├── evaluate.py
│   ├── metrics.py
│   └── evaluation_results.json
│
├── docs/                       # Detailed Documentation
│   ├── improvement_report.md
│   └── evaluation_report.md
│
├── data/                       # Local Data Storage
│   ├── mtsamples.csv
│   └── vector_store.faiss
│
├── .gitignore
├── requirements.txt
├── README.md
└── .env
```

---

## 🛠️ Installation & Run

### Prerequisites
- Python 3.8+
- [Groq API Key](https://console.groq.com/)

### Steps
1.  **Clone & Setup**
    ```bash
    git clone <repo-url>
    cd secure-medical-rag
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in the root directory:
    ```bash
    GROQ_API_KEY=your_groq_api_key_here
    JWT_SECRET_KEY=your_jwt_secret_key_here
    ```

3.  **Run Application**
    ```bash
    streamlit run frontend/main.py
    ```

---

## 🔒 Security Summary
-   **Local-First Architecture**: Vector stores and embeddings are processed locally.
-   **JWT Authentication**: Session management prevents unauthorized access.
-   **Zero-Retention**: The LLM provider (Groq) is used only for inference; no patient data is stored on their servers.

---

## 📚 Documentation
-   **[RAG Improvement Report](docs/improvement_report.md)**: Deep dive into Spacy, BioBERT, and FAISS technical choices.
-   **[Evaluation Results Report](docs/evaluation_report.md)**: Detailed metrics breakdown and safety analysis.
