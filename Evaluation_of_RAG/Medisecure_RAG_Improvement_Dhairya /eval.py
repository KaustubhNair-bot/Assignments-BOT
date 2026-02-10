import time
import pandas as pd
from bert_score import score
from backend.rag import load_vector_store, rag_pipeline, generate_response
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"
TEMPERATURE = 0.0
MAX_TOKENS = 300

# Fixed evaluation queries
QUERIES = [
    "Persistent high blood pressure despite medication",
    "Chest pain with shortness of breath in elderly patient",
    "Fever with rash and joint swelling",
    "Confusion and urinary incontinence in elderly",
    "Severe abdominal pain with vomiting"
]

OUTPUT_FILE = "evaluation_results.csv"


def run_base_llm(query):

    prompt = f"""
You are a clinical assistant.

Answer the doctor's query concisely.
If unsure, state: Insufficient information.

Doctor Query:
{query}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "stream": False
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["response"]


def compute_semantic_similarity(answer, context):

    P, R, F1 = score(
        [answer],
        [context],
        lang="en",
        verbose=False
    )

    return round(F1.mean().item(), 4)



def evaluate():

    print("Loading vector store...")
    index, metadata, bm25 = load_vector_store()

    results = []

    for query in QUERIES:

        print(f"\nRunning Query: {query}")

        # --------------------
        # BASE LLM
        # --------------------
        start = time.time()
        base_answer = run_base_llm(query)
        base_latency = round(time.time() - start, 2)

        # --------------------
        # RAG
        # --------------------
        start = time.time()
        rag_result = rag_pipeline(query, index, metadata, bm25)
        rag_answer = rag_result["generated_response"]
        retrieved_chunks = rag_result["retrieved_cases"]
        rag_latency = round(time.time() - start, 2)

        # Combine retrieved context for semantic similarity
        combined_context = " ".join(retrieved_chunks)

        base_similarity = compute_semantic_similarity(base_answer, combined_context)
        rag_similarity = compute_semantic_similarity(rag_answer, combined_context)

        results.append({
            "Query": query,
            "Base_Answer": base_answer,
            "RAG_Answer": rag_answer,
            "Base_Latency(s)": base_latency,
            "RAG_Latency(s)": rag_latency,
            "Base_Semantic_Similarity": base_similarity,
            "RAG_Semantic_Similarity": rag_similarity
        })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nEvaluation complete.")
    print(f"Results saved to {OUTPUT_FILE}")

    print("\nAverage Semantic Similarity:")
    print("Base:", round(df["Base_Semantic_Similarity"].mean(), 4))
    print("RAG :", round(df["RAG_Semantic_Similarity"].mean(), 4))

    print("\nAverage Latency:")
    print("Base:", round(df["Base_Latency(s)"].mean(), 2), "seconds")
    print("RAG :", round(df["RAG_Latency(s)"].mean(), 2), "seconds")


if __name__ == "__main__":
    evaluate()
