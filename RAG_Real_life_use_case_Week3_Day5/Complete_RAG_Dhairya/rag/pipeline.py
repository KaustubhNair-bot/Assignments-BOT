from .retriever import search
from .llm import generate_response

def rag_query(query, n_results=5):
    chunks = search(query, n_results)

    if not chunks:
        return {"response": "No relevant data found.", "sources": []}

    response = generate_response(query, chunks)

    return {
        "response": response,
        "sources": chunks
    }
