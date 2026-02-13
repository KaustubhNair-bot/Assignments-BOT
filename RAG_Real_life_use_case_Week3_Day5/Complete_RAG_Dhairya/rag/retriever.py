from .vector_store import get_collection
from .embeddings import generate_embeddings

def search(query, n_results=5):
    collection = get_collection()
    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": 1 - results["distances"][0][i]
        })

    return formatted
