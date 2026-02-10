from backend.rag import compare_models
from backend.metrics import evaluate_pair
import json
import time

queries = [
    "diagnosis of cough",
    "treatment for pneumonia",
    "symptoms of asthma",
    "management of COPD",
    "causes of chest pain"
]

results = []

for q in queries:
    print("\nEvaluating:", q)

    start = time.time()
    out = compare_models(q)
    t = round(time.time() - start, 2)

    metrics = evaluate_pair(
        query=q,
        base=out["base_llm"],
        rag=out["rag"]["answer"],
        context=out["rag"]["retrieved"]
    )

    metrics["time_sec"] = t

    results.append({
        "query": q,
        "base_llm": out["base_llm"],
        "rag_answer": out["rag"]["answer"],
        "metrics": metrics
    })

with open("evaluation_results.json", "w") as f:
    json.dump(results, f, indent=4)

print("\n✅ Evaluation Complete → evaluation_results.json")
