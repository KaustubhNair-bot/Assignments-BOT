# Medi-Secure: The Private Hospital Assistant

A beginner-friendly, secure web application that allows doctors to search for past patient cases with similar symptoms using Retrieval-Augmented Generation (RAG) while protecting patient data through local storage and JWT authentication.

**The working version of this Streamlit application is deployed on Streamlit Cloud and can be viewed online through : https://gurkirt-bot-medi-secure-rag-frontendmain-yklv75.streamlit.app/**



## Project Overview

This project demonstrates a complete RAG (Retrieval-Augmented Generation) system specifically designed for healthcare professionals. It enables doctors to:

-  Search for similar patient cases using natural language queries
-  Receive AI-generated insights based on retrieved medical cases
-  Maintain data privacy with local-only storage and JWT authentication
-  Access a knowledge base built from real medical transcription data
-  Get relevant medical information quickly and efficiently


### Data Flow

1. **Authentication**: Doctors login with JWT-based authentication
2. **Query Processing**: User enters natural language medical query
3. **Document Retrieval**: System searches vector store for similar medical cases
4. **Context Generation**: Retrieved cases are formatted as context
5. **AI Response**: GROQ LLM generates insights based on retrieved context
6. **Results Display**: Both retrieved cases and AI response are shown to user

## Security Considerations

### Data Protection
- **Local Storage Only**: All patient data remains on local machine, no external APIs for storage
- **No Cloud Dependencies**: Vector store and data files stored locally
- **JWT Authentication**: Secure token-based authentication with configurable expiration


## How to Run

### Step 1: Create Virtual Environment
```bash
python -m venv .venv

# On macOS/Linux
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
streamlit run frontend/main.py
```

## Project Structure

```
secure-medical-rag/
├── app/
│   ├── auth.py                 # JWT authentication logic
│   └── config.py               # Configuration settings
│
├── rag/
│   ├── rag.py                  # RAG pipeline (embedding, retrieval, generation)
│   ├── data_loader.py          # Load & preprocess dataset
│   └── vector_store.py         # FAISS vector store setup
│
├── frontend/
│   └── main.py                 # Streamlit entry point and UI
│
├── data/
│   ├── mtsamples.csv           # Medical dataset (download from Kaggle)
│   ├── vector_store.faiss      # Generated FAISS index
│   └── vector_store_metadata.pkl  # Document metadata
│
├── .gitignore                  # to keep files untracked
├── requirements.txt            # Python dependencies
├── README.md                 
└── .env                       # Environment variables (untracked by git)
```

## Technology Choices Explained

### Frontend Framework: Streamlit
I chose Streamlit because it's perfect for beginners and rapid development. Unlike complex web frameworks like React or Angular, Streamlit lets you build functional web applications using simple Python code. It handles all the web development complexity behind the scenes while you focus on the actual functionality. For medical professionals who aren't web developers, this means they can understand and modify the application easily.

### Authentication: JWT (JSON Web Tokens)
JWT is the industry standard for web authentication. Instead of storing passwords in sessions or databases, JWT creates secure tokens that prove who you are. These tokens expire automatically, making them more secure than traditional sessions. They're also stateless, meaning the server doesn't need to remember who's logged in - this makes the application more reliable and easier to scale.

### Vector Storage: FAISS
FAISS (Facebook AI Similarity Search) is incredibly fast at finding similar documents. When you have thousands of medical cases, you need to search through them instantly. FAISS uses advanced mathematical techniques to find the most similar cases in milliseconds, not seconds. It was developed by Facebook's AI research team specifically for this type of similarity search, making it perfect for medical case retrieval.

### Embedding Model: Sentence Transformers (all-MiniLM-L6-v2)
I chose this embedding model because it's specifically designed to understand the meaning of sentences, not just keywords. For medical text, this is crucial - the model understands that "chest pain" and "heart discomfort" might mean similar things. The all-MiniLM-L6-v2 model is small enough to run on any computer but powerful enough to capture medical terminology accurately. It creates numerical representations (embeddings) of medical text that capture semantic meaning, allowing the system to find cases that are truly similar in content, not just matching words.

### AI Language Model: Groq Llama 3.1
Groq provides access to Meta's Llama 3.1 model with incredibly fast response times. I chose this over OpenAI because it's more cost-effective, runs faster, and provides high-quality medical insights. Llama 3.1 is excellent at understanding medical context and generating helpful responses based on the provided patient cases. Groq's optimized infrastructure means doctors get insights in seconds rather than waiting for slower cloud services.

### Data Processing: Pandas
Pandas is the standard library for working with structured data in Python. Medical data often comes in CSV format with various columns like patient symptoms, diagnoses, and treatments. Pandas makes it easy to load, clean, and process this data efficiently. It's well-documented and widely used, making it accessible for developers at any skill level.

### Environment Management: python-dotenv
Security is critical in medical applications. python-dotenv allows us to store sensitive information like API keys and database credentials in a separate file that's not tracked by git. This means secrets don't accidentally get shared when code is distributed. It's a simple but effective way to maintain security best practices.

## Why This Technology Stack Works Well Together

All these technologies were chosen to work seamlessly while keeping the system simple and secure. Streamlit handles the user interface, FAISS manages the complex search operations, and the embedding model ensures accurate medical understanding. The stack avoids complex cloud dependencies while still providing powerful AI capabilities. Most importantly, every component can run on a standard computer without specialized hardware, making it accessible to small medical practices.

## What I Learned During This Project
**1. I gained a practical understanding of how RAG works end-to-end**

This project helped me understand Retrieval-Augmented Generation beyond theory. I learned how a user query is first converted into an embedding, matched against stored document embeddings in a vector database, and how only the most relevant medical cases are passed to the language model as context. Seeing how the LLM’s output changes based on retrieved context made it clear why retrieval quality directly affects response accuracy, especially in domains like healthcare where hallucinations are risky.

**2. Building RAG systems is mostly about data quality, not the LLM**

Before this project, I assumed the language model would be the most important part. In practice, I learned that cleaning, chunking, and embedding the medical notes correctly had a much bigger impact on answer quality. Small choices like chunk size and overlap significantly changed help­fulness of results, especially with long medical transcriptions.

**3. Security decisions affect architecture from day one**

Implementing JWT authentication early made me think differently about the entire application flow. I learned that security is not something you “add later” — even a simple demo needs protected routes, session handling, and token validation. This project helped me understand how authentication shapes UI, backend logic, and user experience.

**4. Local-first design is critical for healthcare applications**

Working with medical data made it very clear why local storage and zero data exfiltration are essential. I learned how to design a system where embeddings, vector stores, and raw data all remain on the same machine, while still enabling semantic search and AI responses. This was my first hands-on experience designing with real privacy constraints.

**5. Modular code makes experimentation much easier**

Separating authentication, RAG logic, data loading, and UI into different modules saved a lot of time. When I needed to tweak embeddings or rebuild the FAISS index, I didn’t have to touch the UI or auth logic. This project showed me how clean separation of concerns directly improves development speed and maintainability.

**6. Simple tools are often the best choice for production-ready demos**

Using Streamlit, FAISS, and sentence-transformers taught me that you don’t need heavy frameworks to build something useful. These tools allowed me to focus on functionality instead of boilerplate. I learned how to balance simplicity with real-world requirements, which is especially important when building internal tools or proof-of-concepts.


This project helped me understand how AI systems must be designed differently in regulated domains like healthcare, where correctness, privacy, and explainability matter more than raw model capability.