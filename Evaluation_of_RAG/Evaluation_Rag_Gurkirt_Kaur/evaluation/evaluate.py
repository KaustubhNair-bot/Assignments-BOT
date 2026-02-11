"""
Evaluation Script for Medical RAG Pipeline
Runs queries on Base LLM and Enhanced RAG, calculates metrics, and saves results.
"""

import time
import json
import os
import pandas as pd
from app.config import Config
from rag.rag import RAGPipeline
from groq import Groq
from evaluation.metrics import (
    calculate_accuracy,
    calculate_faithfulness,
    calculate_completeness
)

# Test Data with Ground Truth
# Note: Ground Truths are idealized for the purpose of metrics calculation.
# In a real scenario, these should be vetted by experts.
TEST_CASES = [
    {
        "query": "What are the symptoms of a heart attack?",
        "ground_truth": "Chest pain or discomfort, shortness of breath, pain or discomfort in the jaw, neck, back, arm, or shoulder, feeling weak, light-headed, or faint.",
        "key_facts": ["Chest pain", "Shortness of breath", "Jaw/neck/back pain", "Weakness/fainting"]
    },
    {
        "query": "How is diabetes managed in elderly patients?",
        "ground_truth": "Management involves blood sugar monitoring, healthy diet, regular exercise, medication (insulin or oral), and monitoring for complications. Special care is needed for hypoglycemia risks.",
        "key_facts": ["Blood sugar monitoring", "Diet", "Exercise", "Medication", "Hypoglycemia risk"]
    },
    {
        "query": "What treatments are available for hypertension?",
        "ground_truth": "Lifestyle changes (diet, exercise, weight loss) and medications such as ACE inhibitors, beta-blockers, diuretics, and calcium channel blockers.",
        "key_facts": ["Lifestyle changes", "ACE inhibitors", "Beta-blockers", "Diuretics"]
    },
    {
        "query": "What are the common side effects of chemotherapy?",
        "ground_truth": "Fatigue, hair loss, nausea and vomiting, infection, anemia, bruising and bleeding, and appetite changes.",
        "key_facts": ["Fatigue", "Hair loss", "Nausea", "Infection", "Anemia"]
    },
    {
        "query": "What are the complications of untreated asthma?",
        "ground_truth": "Severe asthma attacks, permanent narrowing of bronchial tubes (airway remodeling), hospitalization, and side effects from long-term medication use.",
        "key_facts": ["Severe attacks", "Airway remodeling", "Hospitalization"]
    }
]

def run_evaluation():
    print("Initializing components...")
    rag = RAGPipeline()
    # Using existing vector store (fast)
    if not rag.initialize_vector_store(force_rebuild=False):
        print("Failed to initialize vector store.")
        return

    client = Groq(api_key=Config.GROQ_API_KEY)
    
    results = []
    
    print(f"Starting evaluation on {len(TEST_CASES)} queries...")
    
    for case in TEST_CASES:
        query = case["query"]
        ground_truth = case["ground_truth"]
        print(f"\nProcessing: {query}")
        
        # --- Base LLM Evaluation ---
        start_time = time.time()
        try:
            base_resp = client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": query}
                ],
                max_tokens=500
            )
            base_answer = base_resp.choices[0].message.content
        except Exception as e:
            base_answer = f"Error: {e}"
        base_time = time.time() - start_time
        
        # Calculate Base Metrics
        base_metrics = {
            "Accuracy": calculate_accuracy(base_answer, ground_truth),
            "Faithfulness": 0.5, # Base LLM has no context to be faithful to, arbitrarily 0.5 or N/A
            "Completeness": calculate_completeness(base_answer, ground_truth),
            "Response Time": base_time
        }
        
        # --- RAG Evaluation ---
        start_time = time.time()
        rag_output = rag.search_and_respond(query)
        rag_answer = rag_output['response']
        rag_time = time.time() - start_time
        
        # Context for faithfulness check
        retrieved_context = "\n".join([doc['text'] for doc, _ in rag_output.get('retrieved_documents', [])])
        
        # Calculate RAG Metrics
        rag_metrics = {
            "Accuracy": calculate_accuracy(rag_answer, ground_truth),
            "Faithfulness": calculate_faithfulness(rag_answer, retrieved_context),
            "Completeness": calculate_completeness(rag_answer, ground_truth),
            "Response Time": rag_time
        }
        
        # Append Result
        results.append({
            "Query": query,
            "Ground_Truth": ground_truth,
            "Base_Answer": base_answer,
            "Base_Metrics": base_metrics,
            "RAG_Answer": rag_answer,
            "RAG_Metrics": rag_metrics,
            "Retrieved_Context": retrieved_context
        })
        
    # Save to JSON
    output_path = "evaluation/evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nEvaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    run_evaluation()
