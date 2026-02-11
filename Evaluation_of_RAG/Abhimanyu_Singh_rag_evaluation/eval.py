import json
import time
import requests
import os
import sys
from backend.rag import query_rag # Imports your actual RAG pipeline

# Configuration - Update MODEL to match your local Ollama model (e.g., 'mistral')
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral" 

# 5 Diverse Medical Queries for Benchmarking
TEST_SUITE = [
    {
        "id": 1,
        "category": "Cardiology",
        "query": "Middle-aged patient with exertional chest discomfort, shortness of breath, and a history of hypertension",
        "expected_topics": [
            "coronary artery disease",
            "hypertension",
            "ECG",
            "cardiac risk factors"
        ]
    },
    {
        "id": 2,
        "category": "Endocrinology",
        "query": "Long-term management considerations for a patient with poorly controlled type 2 diabetes and progressive sensory complications",
        "expected_topics": [
            "type 2 diabetes",
            "glycemic control",
            "neuropathy",
            "chronic complications"
        ]
    },
    {
        "id": 3,
        "category": "Orthopedics",
        "query": "Surgical intervention options for an elderly patient with advanced degenerative knee joint disease",
        "expected_topics": [
            "osteoarthritis",
            "knee arthroplasty",
            "joint degeneration",
            "orthopedic surgery"
        ]
    },
    {
        "id": 4,
        "category": "Pediatrics",
        "query": "Young child with recurrent upper respiratory infections and frequent antibiotic exposure over multiple clinical visits",
        "expected_topics": [
            "upper respiratory infection",
            "pediatric infections",
            "antibiotic use",
            "otitis media"
        ]
    },
    {
        "id": 5,
        "category": "Gastroenterology",
        "query": "Evaluation of chronic abdominal discomfort in a patient undergoing diagnostic endoscopy to rule out inflammatory bowel conditions",
        "expected_topics": [
            "endoscopy",
            "inflammatory bowel disease",
            "chronic abdominal pain",
            "IBD differential diagnosis"
        ]
    }
]


def query_base_llm(question):
    """Calls the Base LLM (no RAG context) for comparison."""
    start = time.time()
    payload = {"model": MODEL, "prompt": f"Answer as a medical expert: {question}", "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return r.json().get("response", ""), int((time.time() - start) * 1000)
    except Exception as e:
        return f"Error: {str(e)}", 0

def judge_response(query, answer, is_rag=False):
    """Automated LLM-as-Judge to score metrics 1-10."""
    prompt = f"### Query: {query}\n### Answer: {answer}\n\nRate on 1-10:\n1. Completeness\n2. Specificity"
    if is_rag: prompt += "\n3. Groundedness (Does it cite/use specific case details from the database?)"
    prompt += "\n\nReturn ONLY a JSON object: {\"completeness\": X, \"specificity\": Y, \"groundedness\": Z}"
    
    payload = {"model": MODEL, "prompt": prompt, "stream": False, "format": "json"}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=30)
        return json.loads(r.json().get("response", "{}"))
    except:
        return {"completeness": 5, "specificity": 5, "groundedness": 5}

def run_eval():
    final_data = []
    print(f"🚀 Starting Task 2 Evaluation using model: {MODEL}...")
    
    for item in TEST_SUITE:
        print(f"-> Evaluating Query {item['id']}: {item['category']}...")
        
        # 1. Base LLM Test
        b_ans, b_lat = query_base_llm(item['query'])
        b_scores = judge_response(item['query'], b_ans)
        
        # 2. RAG System Test
        r_start = time.time()
        r_ans = query_rag(item['query'])
        r_lat = int((time.time() - r_start) * 1000)
        r_scores = judge_response(item['query'], r_ans, is_rag=True)
        
        final_data.append({
            "id": item['id'],
            "category": item['category'],
            "query": item['query'],
            "base_llm": {"answer": b_ans, "latency_ms": b_lat, "scores": b_scores},
            "rag_system": {"answer": r_ans, "latency_ms": r_lat, "scores": r_scores}
        })
    
    # Save results for documentation
    with open("evaluation_results.json", "w") as f:
        json.dump(final_data, f, indent=4)
    print("✅ Evaluation complete! Results saved to evaluation_results.json")

if __name__ == "__main__":
    run_eval()