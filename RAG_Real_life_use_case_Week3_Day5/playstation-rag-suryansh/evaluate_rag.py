import time
import os
from dotenv import load_dotenv
from rag_engine import rag_pipeline
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# evaluation queries 
test_queries = [
    "What kind of M.2 SSD can I install in my PS5?",
    "How do I boot my PS5 into Safe Mode?",
    "My PS5 won’t turn on. What should I check first?",
    "Why does my PS5 show a black screen?",
    "What USB drive works for PS5 extended storage?",
    "Can I upgrade the PS5 graphics card?"
]

# base LLM 
def base_llm_answer(query, temperature=0.0):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a PlayStation support assistant."},
            {"role": "user", "content": query}
        ],
        temperature=temperature,
        top_p=0.9,
        max_tokens=500
    )
    return completion.choices[0].message.content


# groundedness metric
def groundedness_score(answer, retrieved_chunks):

    retrieved_text = " ".join(retrieved_chunks).lower()

    answer_words = [
        w for w in answer.lower().split()
        if len(w) > 6
    ]

    if len(answer_words) == 0:
        return 1.0

    overlap = sum(
        1 for w in answer_words
        if w in retrieved_text
    )

    return overlap / len(answer_words)

# hallucination detection
def detect_hallucination(answer, retrieved_chunks):

    retrieved_text = " ".join(retrieved_chunks).lower()

    suspicious_terms = [
        "overclock",
        "graphics card upgrade",
        "crypto",
        "mining",
        "firmware hack"
    ]

    for term in suspicious_terms:
        if term in answer.lower() and term not in retrieved_text:
            return True

    return False

# evaluation function
def evaluate(temp):
    print(f"\nEvaluating at Temperature = {temp}")
    print("=" * 70)

    rag_latency = 0
    base_latency = 0

    rag_groundedness = 0
    rag_hallucinations = 0

    base_hallucinations = 0

    for q in test_queries:
        print(f"\nQuery: {q}")

        # RAG
        start = time.time()
        rag_answer, retrieved, scores, _ = rag_pipeline(q, temperature=temp)
        end = time.time()

        rag_latency += (end - start)

        g_score = groundedness_score(rag_answer, retrieved)
        rag_groundedness += g_score

        if detect_hallucination(rag_answer, retrieved):
            rag_hallucinations += 1

        # base LLM
        start = time.time()
        base_answer = base_llm_answer(q, temperature=temp)
        end = time.time()

        base_latency += (end - start)

        if "upgrade the ps5 graphics card" in base_answer.lower():
            base_hallucinations += 1

    total = len(test_queries)

    print("\nFINAL RESULTS")
    print("=" * 70)

    print("RAG System:")
    print(f"Avg Latency: {rag_latency/total:.2f}s")
    print(f"Avg Groundedness: {(rag_groundedness/total):.2f}")
    print(f"Hallucinations: {rag_hallucinations}")

    print("\nBase LLM (No Retrieval):")
    print(f"Avg Latency: {base_latency/total:.2f}s")
    print(f"Hallucinations: {base_hallucinations}")

    print("=" * 70)


if __name__ == "__main__":
    for t in [0.0, 0.3, 0.6]: #testing across different temperatures
        evaluate(t)
