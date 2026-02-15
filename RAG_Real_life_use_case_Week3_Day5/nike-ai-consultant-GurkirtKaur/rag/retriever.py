from config.settings import RETRIEVER_K

def get_retriever(vector_store):
    """
    Returns a retriever object from the vector store.
    """
    return vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})

if __name__ == "__main__":
    from rag.embeddings import get_embedding_model
    from rag.vector_store import load_vector_store
    
    embed_model = get_embedding_model()
    vector_store = load_vector_store(embed_model)
    
    if vector_store:
        retriever = get_retriever(vector_store)
        docs = retriever.invoke("What is the policy on parental leave?")
        for i, doc in enumerate(docs):
            print(f"Result {i+1}: {doc.page_content[:150]}...")
