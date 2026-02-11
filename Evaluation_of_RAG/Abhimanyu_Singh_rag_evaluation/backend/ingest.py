import os
import pandas as pd
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------- Configuration ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "medical_transcriptions.csv")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# Reverting to the general-purpose model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" 

# ---------- Initialize Embedding Model ----------
embed_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={'device': 'cpu'} 
)

# ---------- Load & Process Documents ----------
df = pd.read_csv(DATA_PATH)
raw_texts = df["transcription"].dropna().tolist()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600, 
    chunk_overlap=120
)

# ---------- Persistent Storage ----------
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="medical_notes_domain")

print(f"Indexing medical documents using {MODEL_NAME}...")
for idx, text in enumerate(raw_texts):
    chunks = text_splitter.split_text(text)
    # Using the embed_query method to generate embeddings for Chroma
    embeddings = embed_model.embed_documents(chunks)
    
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"doc_{idx}_chunk_{j}" for j in range(len(chunks))]
    )

print("✅ Success: Clinical notes indexed with all-MiniLM-L6-v2.")