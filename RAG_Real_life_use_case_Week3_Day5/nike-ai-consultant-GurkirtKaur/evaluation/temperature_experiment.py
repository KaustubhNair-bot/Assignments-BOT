import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.loader import load_documents
from rag.chunking import split_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import load_vector_store, create_vector_store
from rag.retriever import get_retriever
from rag.generator_llm import generate_answer_llm as generate_answer
from config.settings import FAISS_INDEX_PATH

def run_experiment():
    print("=========================================================")
    print("NIKE AI CONSULTANT - TEMPERATURE EXPERIMENT")
    print("=========================================================\n")

    # 1. Setup RAG components
    embed_model = get_embedding_model()
    
    # Ensure Vector Store exists
    if not os.path.exists(FAISS_INDEX_PATH):
        print("Initializing Vector Store for experiment...")
        docs = load_documents()
        chunks = split_documents(docs)
        vector_store = create_vector_store(chunks, embed_model)
    else:
        vector_store = load_vector_store(embed_model)
    
    retriever = get_retriever(vector_store)

    # Test Query
    query = "Can I work from a coffee shop?"

    # Experiment Matrix
    temperatures = [0.0, 0.4, 0.8]
    top_ps = [0.5, 0.9, 1.0]

    for temp in temperatures:
        for tp in top_ps:
            print(f"--- RUNNING: Temp={temp}, Top_P={tp} ---")
            try:
                res = generate_answer(query, retriever, temp, tp)
                print(f"[Response Preview]: {res['result'][:100]}...")
            except Exception as e:
                print(f"Error for Temp={temp}, Top_P={tp}: {e}")
            print("-" * 30)

    print("\n=========================================================")
    print("Experiment Complete. Check output for analysis.")

if __name__ == "__main__":
    load_dotenv()
    run_experiment()
