from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer('all-mpnet-base-v2') # Loading mpnet model

index = faiss.read_index("embeddings/medical.index") # Loading FAISS index

texts = open("embeddings/texts.txt", encoding="utf-8").read().split("\n") # Loading texts.txt and and converting each line into a list item

def search(query):

    q = model.encode([query]) # Converting the query into a vector embedding using the same mpnet model used for indexing

    D, I = index.search(q, 5) # D contains the distances(similarity scores) of the top 5 results, I contains the indices of the top 5 results in the original texts list

    results = []

    for idx, dist in zip(I[0], D[0]):

        if idx < len(texts):

            results.append({
                "text": texts[idx],
                "distance": float(dist)
            })

    return results



