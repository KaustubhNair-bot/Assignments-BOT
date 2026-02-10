from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embed = SentenceTransformer('all-mpnet-base-v2')

# ---- Metric 1: Relevancy ----
def relevancy_score(question, answer):
    q = embed.encode([question])
    a = embed.encode([answer])
    return float(cosine_similarity(q, a)[0][0])


# ---- Metric 2: Faithfulness ----
def faithfulness_score(answer, retrieved_chunks):

    if not retrieved_chunks:
        return 0

    ans = embed.encode([answer])

    scores = []
    for c in retrieved_chunks:
        vec = embed.encode([c])
        scores.append(cosine_similarity(ans, vec)[0][0])

    return float(max(scores))


# ---- Metric 3: Context Utilization ----
def context_util(answer, retrieved_chunks):

    used = 0
    for c in retrieved_chunks:
        for word in c.split()[:50]:
            if word in answer:
                used += 1
                break

    return used / max(len(retrieved_chunks), 1)


def evaluate(question, base_ans, rag_ans, retrieved):

    return {
        "base_relevancy": relevancy_score(question, base_ans),
        "rag_relevancy": relevancy_score(question, rag_ans),

        "faithfulness": faithfulness_score(rag_ans, retrieved),

        "context_util": context_util(rag_ans, retrieved)
    }
