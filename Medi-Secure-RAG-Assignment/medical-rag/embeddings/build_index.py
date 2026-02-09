import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer #used to convert text into vector embeddings 
import faiss #does vector similarity search

df = pd.read_csv("data/medical.csv")

texts = df["transcription"].dropna().unique().tolist() #removing any missing values and converting to list

model = SentenceTransformer('all-mpnet-base-v2') 
embeddings = model.encode(texts) #converting the list of texts into a numpy array of vector embeddings

print("Total unique documents:", len(texts))

# mpnet gives 768 dimension vectors
index = faiss.IndexFlatL2(768) #creating a faiss index for efficient similarity search; uses L2 distance (Euclidean distance) to measure similarity.
index.add(np.array(embeddings)) #adding the vector embeddings to the faiss index for efficient similarity search

faiss.write_index(index, "embeddings/medical.index") #saving the faiss index 

# Save texts line-by-line while removing internal newlines for clean retrieval mapping
with open("embeddings/texts.txt", "w", encoding="utf-8") as f:
    for text in texts:
        cleaned_text = text.replace("\n", " ")  # Replace internal newlines with spaces
        f.write(cleaned_text + "\n")  # Write each cleaned text on a new line

print("Index Created Successfully!")

#medical.index stores vector embeddings
#texts.txt stores the original transcriptions