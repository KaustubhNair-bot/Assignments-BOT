"""
Metrics Calculation Module
Contains functions to calculate Accuracy, Precision, Recall, F1, Faithfulness, Completeness, and Response Time.
"""

from typing import List, Union
import time
from groq import Groq
from app.config import Config

# Initialize Groq client for LLM-based metrics
client = Groq(api_key=Config.GROQ_API_KEY)

def calculate_accuracy(prediction: str, ground_truth: str) -> float:
    """
    Calculate accuracy by checking semantic similarity between prediction and ground truth using LLM.
    Returns 1.0 if accurate, 0.0 otherwise.
    """
    prompt = f"""
    Ground Truth: "{ground_truth}"
    Prediction: "{prediction}"
    
    Is the Prediction factually consistent with the Ground Truth? Answer strictly "YES" or "NO".
    """
    try:
        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5
        )
        answer = response.choices[0].message.content.strip().upper()
        return 1.0 if "YES" in answer else 0.0
    except Exception:
        return 0.0

def calculate_precision(retrieved_ids: List[int], relevant_ids: List[int]) -> float:
    """
    Calculate Precision: Proportion of retrieved documents that are relevant.
    """
    if not retrieved_ids:
        return 0.0
    relevant_retrieved = len(set(retrieved_ids).intersection(set(relevant_ids)))
    return relevant_retrieved / len(retrieved_ids)

def calculate_recall(retrieved_ids: List[int], relevant_ids: List[int]) -> float:
    """
    Calculate Recall: Proportion of relevant documents successfully retrieved.
    """
    if not relevant_ids:
        return 0.0
    relevant_retrieved = len(set(retrieved_ids).intersection(set(relevant_ids)))
    return relevant_retrieved / len(relevant_ids)

def calculate_f1(precision: float, recall: float) -> float:
    """
    Calculate F1 Score: Harmonic mean of Precision and Recall.
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def calculate_faithfulness(answer: str, context: str) -> float:
    """
    Calculate Faithfulness: Does the answer come strictly from the context?
    Uses LLM to evaluate. Returns score 0.0 to 1.0.
    """
    prompt = f"""
    Context: "{context}"
    Answer: "{answer}"
    
    Is the Answer fully supported by the Context? 
    Give a score from 0.0 to 1.0 where 1.0 means fully supported and 0.0 means completely hallucinated.
    Return ONLY the score.
    """
    try:
        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        score = float(response.choices[0].message.content.strip())
        return min(max(score, 0.0), 1.0)
    except Exception:
        return 0.0

def calculate_completeness(answer: str, ground_truth: str) -> float:
    """
    Calculate Completeness: How much of the ground truth information is covered?
    Uses LLM to evaluate. Returns score 0.0 to 1.0.
    """
    prompt = f"""
    Ground Truth: "{ground_truth}"
    Answer: "{answer}"
    
    How much of the key information from Ground Truth is covered in the Answer?
    Give a score from 0.0 to 1.0. Return ONLY the score.
    """
    try:
        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        score = float(response.choices[0].message.content.strip())
        return min(max(score, 0.0), 1.0)
    except Exception:
        return 0.0
