import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "medical_transcriptions.csv")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

os.makedirs(CHROMA_DIR, exist_ok=True)
print("📁 Persistent Chroma directory:", CHROMA_DIR)

# ---------- Load data ----------
df = pd.read_csv(DATA_PATH)
texts = df["transcription"].dropna().tolist()
print("📄 Documents found in CSV:", len(texts))

# ---------- Embedding model ----------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- Persistent Client ----------
# Using PersistentClient ensures data is saved to CHROMA_DIR
client = chromadb.PersistentClient(path=CHROMA_DIR)

# Using get_or_create prevents errors if re-running the script
collection = client.get_or_create_collection(name="medical_notes")

# ---------- Add documents ----------
print(" Indexing documents... this may take a minute.")
for i, text in enumerate(texts):
    collection.add(
        documents=[text],
        embeddings=[model.encode(text).tolist()],
        ids=[str(i)]
    )

print(" Total vectors stored:", collection.count())
print("Medical notes indexed and saved successfully.")