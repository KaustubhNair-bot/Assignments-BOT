# 🔋 Tesla Supply Chain Intelligence: AI Logistics & Parts Auditor

### **Project Overview**
This project is a high-performance, **Native RAG (Retrieval-Augmented Generation)** application designed for enterprise-level auditing. Acting as a **Tesla Lead Logistics Auditor**, the system processes complex, unstructured data from Tesla's **Impact Report 2023** and **Master Plan Part 3** to provide factual, reasoned, and benchmarked insights into supply chain and energy targets.

---

## 🚀 Key Features
* **Native RAG Architecture:** Built without heavy frameworks like LangChain to minimize latency and ensure maximum architectural control.
* **Hybrid Model Strategy:** Combines a local **Small Language Model (SLM)** for lightning-fast retrieval with a powerful **LLM (Llama 3.3-70B)** for complex reasoning.
* **JWT Security Vault:** Implemented an enterprise-grade authentication system with Access and Refresh token rotation.
* **Automated Benchmarking:** Built-in "LLM-as-a-Judge" loop that scores every response on Faithfulness and Relevancy in real-time.

---

## 📂 Project Structure & File Map

| File | Responsibility |
| :--- | :--- |
| **`app.py`** | The "Control Tower." Manages the Streamlit UI, session states, multi-tab navigation, and secure login screens. |
| **`src/engine.py`** | The "Brain." Handles vector search logic, data sanitization (Regex cleaning), and the Auditor Persona prompt execution. |
| **`src/auth.py`** | The "Security Guard." Manages JWT token creation, verification, and the silent refresh mechanism for user sessions. |
| **`src/evaluator.py`** | The "Judge." A dedicated class that uses an LLM to benchmark the Auditor's accuracy and faithfulness. |
| **`src/utils.py`** | The "Worker." Handles PDF processing, text extraction via `PyMuPDF4LLM`, and initial chunking logic. |
| **`data/`** | The "Library." Contains the raw Tesla PDF documents used as the knowledge base. |

---

## 🔄 System Workflow (The Flow)

### 1. Data Ingestion & Retrieval (The Librarian Phase)
* **Step A:** `utils.py` parses the Tesla PDFs and breaks them into logical "chunks".
* **Step B:** The SLM (`all-MiniLM-L6-v2`) converts these chunks into mathematical vectors stored in **ChromaDB**.
* **Step C:** When a user asks a question, the system finds the **top 3 most relevant segments** using semantic search.

### 2. Reasoning & Generation (The Auditor Phase)
* **Step D:** The retrieved segments are "cleaned" using **Regex** in `engine.py` to remove messy PDF gaps and headers.
* **Step E:** The cleaned text is passed to **Llama 3.3-70B** with a strict **Chain-of-Thought (CoT)** prompt.
* **Step F:** The Auditor explains its logic first, then provides the final answer with cited evidence.

### 3. Verification & Security (The Guard Phase)
* **Step G:** Before every query, `auth.py` validates the user's JWT token.
* **Step H:** After every response, `evaluator.py` automatically generates a score (0-10) displayed in the **Performance Benchmark** tab.

---

## 📊 Benchmarking Methodology
We experimented with generation parameters to find the "Auditor's Sweet Spot":
* **Temperature (0.0):** Set to zero to ensure deterministic, factual responses.
* **Top-P (0.9):** Adjusted to allow professional vocabulary while cutting off low-probability "hallucinations".
* **Result:** The system successfully calculated complex targets, such as the **47.2 TWh** total battery storage capacity, with 100% faithfulness.

---

## 🛠️ Setup Instructions
1.  **Environment:** Create a `.env` file with your `GROQ_API_KEY`, `JWT_ACCESS_SECRET`, and `JWT_REFRESH_SECRET`.
2.  **Dependencies:** Run `pip install -r requirements.txt`.
3.  **Run:** Execute `streamlit run app.py`.
4.  **Login:** Use `admin@tesla.com` / `elon123`.