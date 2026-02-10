from sentence_transformers import SentenceTransformer
import faiss
from backend.generator import generate_answer, base_llm_answer

model = SentenceTransformer('all-mpnet-base-v2') # Loading mpnet model

index = faiss.read_index("embeddings/medical.index") # Loading FAISS index

texts = open("embeddings/texts.txt", encoding="utf-8").read().split("\n") # Loading texts.txt and and converting each line into a list item

def get_retrieved_texts(query, k=5):

    q = model.encode([query]) # Converting the query into a vector embedding using the same mpnet model used for indexing
    D, I = index.search(q, k) # D contains the distances(similarity scores) of the top 5 results, I contains the indices of the top 5 results in the original texts list

    chunks = []

    for idx, dist in zip(I[0], D[0]):
        if idx < len(texts) and dist < 1.4:
            chunks.append(texts[idx][:1800])

    return chunks


def rag_with_llm(query):

    retrieved = get_retrieved_texts(query)

    final = generate_answer(query, retrieved) # Send query + retrieved context to LLM

    # Return both retrieved documents and final LLM answer
    return {
        "retrieved": retrieved,
        "answer": final,
        "confidence": len(retrieved)
    }

# Comparison Function to compare base LLM answer with RAG-enhanced answer for the same query
def compare_models(query):

    base = base_llm_answer(query) #Base LLM result

    rag = rag_with_llm(query) #RAG result

    return {
        "base_llm": base,
        "rag": rag
    }