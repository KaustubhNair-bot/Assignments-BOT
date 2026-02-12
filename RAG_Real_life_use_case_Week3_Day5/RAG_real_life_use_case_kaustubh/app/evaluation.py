"""
Evaluation Module for Airtel RAG Customer Support Chatbot.

Benchmarks:
- Retrieval quality (context relevance)
- Response faithfulness (hallucination detection)
- Temperature/Top-P impact on hallucination
- Response quality metrics (ROUGE, coherence)
"""

import json
import time
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

EVAL_DIR = Path(__file__).parent.parent / "evaluation_results"

# ---------- Test Questions & Expected Answers ----------
TEST_CASES = [
    {
        "id": 1,
        "question": "What is the cheapest prepaid plan available on Airtel?",
        "expected_keywords": ["₹79", "28 days", "voice calling", "no data"],
        "category": "Prepaid Plans",
    },
    {
        "id": 2,
        "question": "Tell me about the Airtel Infinity ₹999 postpaid plan. What OTT subscriptions are included?",
        "expected_keywords": ["Netflix", "Disney+", "Amazon Prime", "150 GB", "₹999"],
        "category": "Postpaid Plans",
    },
    {
        "id": 3,
        "question": "How can I port my number to Airtel?",
        "expected_keywords": ["PORT", "1900", "UPC", "Unique Porting Code", "3-7 working days", "₹6.46"],
        "category": "Porting / MNP",
    },
    {
        "id": 4,
        "question": "What are the international roaming charges for the USA?",
        "expected_keywords": ["₹196", "500 MB", "35+ countries", "USA"],
        "category": "International Roaming",
    },
    {
        "id": 5,
        "question": "What is Airtel's refund policy for prepaid recharges?",
        "expected_keywords": ["non-refundable", "24 hours", "talk-time balance", "7 working days"],
        "category": "Refund Policy",
    },
    {
        "id": 6,
        "question": "What broadband plan gives me 1 Gbps speed?",
        "expected_keywords": ["Ultra Plan", "₹3,999", "1 Gbps", "no FUP", "truly unlimited"],
        "category": "Broadband",
    },
    {
        "id": 7,
        "question": "How do I file a complaint with Airtel?",
        "expected_keywords": ["121", "Level 1", "Docket Number", "7 working days", "Appellate Authority"],
        "category": "Customer Support",
    },
    {
        "id": 8,
        "question": "What are the benefits of the Airtel Thanks Platinum tier?",
        "expected_keywords": ["Netflix", "ZEE5", "SonyLIV", "airport lounge", "handset protection", "relationship manager"],
        "category": "Rewards",
    },
    {
        "id": 9,
        "question": "What happens if I exceed the fair usage limit on my prepaid plan?",
        "expected_keywords": ["64 Kbps", "speed is reduced", "12:00 AM", "data resets"],
        "category": "FUP Policy",
    },
    {
        "id": 10,
        "question": "How can I cancel my Airtel postpaid connection?",
        "expected_keywords": ["Airtel store", "ID proof", "outstanding bills", "₹500", "60 working days"],
        "category": "Cancellation",
    },
]


def evaluate_keyword_match(response: str, expected_keywords: List[str]) -> dict:
    """
    Evaluate how many expected keywords appear in the response.
    This is a proxy for factual correctness / faithfulness.
    """
    response_lower = response.lower()
    matches = []
    misses = []

    for kw in expected_keywords:
        if kw.lower() in response_lower:
            matches.append(kw)
        else:
            misses.append(kw)

    score = len(matches) / len(expected_keywords) if expected_keywords else 0.0

    return {
        "score": round(score, 4),
        "matched": matches,
        "missed": misses,
        "total_expected": len(expected_keywords),
        "total_matched": len(matches),
    }


def evaluate_hallucination_risk(response: str, retrieved_chunks: List[str]) -> dict:
    """
    Simple hallucination detection:
    Check if the response contains specific claims (numbers, names)
    that are NOT present in any of the retrieved chunks.
    """
    import re

    # Extract numbers/prices from response
    response_numbers = set(re.findall(r'₹[\d,]+', response))
    response_numbers.update(re.findall(r'\d+\s*(?:GB|MB|Kbps|Mbps|days|months|years)', response, re.IGNORECASE))

    # Extract same from chunks
    chunks_combined = " ".join(retrieved_chunks)
    chunk_numbers = set(re.findall(r'₹[\d,]+', chunks_combined))
    chunk_numbers.update(re.findall(r'\d+\s*(?:GB|MB|Kbps|Mbps|days|months|years)', chunks_combined, re.IGNORECASE))

    # Find claims in response NOT in chunks (potential hallucinations)
    unsupported = response_numbers - chunk_numbers
    supported = response_numbers & chunk_numbers

    total = len(response_numbers)
    hallucination_rate = len(unsupported) / total if total > 0 else 0.0

    return {
        "hallucination_rate": round(hallucination_rate, 4),
        "total_claims": total,
        "supported_claims": len(supported),
        "unsupported_claims": len(unsupported),
        "unsupported_details": list(unsupported),
        "supported_details": list(supported),
    }


def run_full_evaluation(rag_engine, llm_engine) -> dict:
    """
    Run the complete evaluation suite across all test cases
    and multiple temperature/top-p settings.

    Returns a comprehensive results dictionary.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "model": llm_engine.get_config()["model"],
        "rag_stats": rag_engine.get_stats(),
        "test_results": [],
        "temperature_comparison": [],
        "summary": {},
    }

    # --- Per-question evaluation ---
    total_keyword_score = 0.0
    total_hallucination_rate = 0.0

    for tc in TEST_CASES:
        print(f"\n[EVAL] Question {tc['id']}: {tc['question'][:60]}...")

        # Retrieve
        retrieved = rag_engine.retrieve(tc["question"], top_k=5)
        chunk_texts = [r[0] for r in retrieved]

        # Generate
        response = llm_engine.generate(tc["question"], retrieved)

        # Evaluate keywords
        kw_eval = evaluate_keyword_match(response, tc["expected_keywords"])
        total_keyword_score += kw_eval["score"]

        # Evaluate hallucination
        hall_eval = evaluate_hallucination_risk(response, chunk_texts)
        total_hallucination_rate += hall_eval["hallucination_rate"]

        result = {
            "test_id": tc["id"],
            "question": tc["question"],
            "category": tc["category"],
            "keyword_evaluation": kw_eval,
            "hallucination_evaluation": hall_eval,
            "response_length": len(response),
            "num_chunks_retrieved": len(retrieved),
        }
        results["test_results"].append(result)

    n = len(TEST_CASES)
    results["summary"]["avg_keyword_score"] = round(total_keyword_score / n, 4)
    results["summary"]["avg_hallucination_rate"] = round(total_hallucination_rate / n, 4)

    # --- Temperature comparison on a sample question ---
    sample_q = TEST_CASES[0]["question"]
    retrieved = rag_engine.retrieve(sample_q, top_k=5)
    chunk_texts = [r[0] for r in retrieved]

    comparison = llm_engine.generate_with_comparison(sample_q, retrieved)
    for setting, resp in comparison.items():
        kw_eval = evaluate_keyword_match(resp, TEST_CASES[0]["expected_keywords"])
        hall_eval = evaluate_hallucination_risk(resp, chunk_texts)
        results["temperature_comparison"].append({
            "setting": setting,
            "keyword_score": kw_eval["score"],
            "hallucination_rate": hall_eval["hallucination_rate"],
            "response_length": len(resp),
        })

    # Save results
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EVAL_DIR / f"eval_{timestamp_str}.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[EVAL] Results saved to: {output_path}")
    print(f"[EVAL] Average Keyword Score: {results['summary']['avg_keyword_score']}")
    print(f"[EVAL] Average Hallucination Rate: {results['summary']['avg_hallucination_rate']}")

    return results
