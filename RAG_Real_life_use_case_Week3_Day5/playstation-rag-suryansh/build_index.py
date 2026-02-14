import faiss
import pickle
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

model = SentenceTransformer("BAAI/bge-base-en-v1.5") # load embedding model

pdf_path = "data/playstation.pdf" # reading main PDF knowledge base

reader = PdfReader(pdf_path)
text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

official_links_path = "data/official_links.txt" # appending official support links

if os.path.exists(official_links_path):
    with open(official_links_path, "r") as f:
        text += "\n" + f.read()

# sliding window chunking
def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks

chunks = chunk_text(text)

print(f"Total Chunks Created: {len(chunks)}")

# create embeddings (normalized for cosine)
embeddings = model.encode(
    chunks,
    normalize_embeddings=True,
    show_progress_bar=True
)

embeddings = np.array(embeddings)

# build FAISS index (cosine similarity)
dimension = embeddings.shape[1] 

index = faiss.IndexFlatIP(dimension)  # inner product = cosine (normalized)
index.add(embeddings)

# save index + chunks
os.makedirs("faiss_index", exist_ok=True)

faiss.write_index(index, "faiss_index/index.faiss")

with open("faiss_index/chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("✅ FAISS Index Built Successfully with:")
print("- Sliding Window Chunking")
print("- Official Support Links Embedded")
print("- BGE Embeddings (High Accuracy)")
print("- Cosine Similarity Search")
