import os
from dotenv import load_dotenv
import json
import statistics
from groq import Groq
import json
from datetime import datetime


load_dotenv()

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.retriever import search
from rag.llm import generate_response

# ---- CONFIG ----
MODEL_JUDGE = "llama-3.3-70b-versatile"
TEMPERATURE = 0.0

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --------------------------------------------------
# JUDGE FUNCTION
# --------------------------------------------------
def evaluate_response(question, retrieved_context, rag_answer):

    judge_prompt = f"""
You are an expert evaluator of AI-generated business strategy responses.

Evaluate STRICTLY based on the retrieved context.

RETRIEVED CONTEXT:
{retrieved_context}

QUESTION:
{question}

AI ANSWER:
{rag_answer}

Score on:

1) Groundedness (0-5): Uses only retrieved context.
2) Relevance (0-5): Directly answers question.
3) Strategic Depth (0-5): Analytical and structured.
4) Actionability (0-5): Specific and measurable.

Return STRICT JSON:

{{
  "groundedness": number,
  "relevance": number,
  "strategic_depth": number,
  "actionability": number,
  "justification": "short explanation",
  "hallucinations_found": "unsupported claims or 'None'"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_JUDGE,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": judge_prompt}],
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        print("⚠️ Failed to parse JSON. Raw output below:")
        print(content)
        return None


# --------------------------------------------------
# DRIVER FUNCTION (FULL EVALUATION)
# --------------------------------------------------
def run_full_evaluation():

    test_questions = [
        "What strategic moves should McDonald's India prioritize to expand market share over the next two years?",
        "How can McDonald's India optimize its menu portfolio to improve profitability?",
        "What key strategic risks are identified in the financial and competitor documents?",
        "How does competitor positioning impact McDonald's growth strategy?",
        "What is the single most important strategic priority based on current financial performance?"
    ]

    results = []

    for idx, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🔎 Question {idx}: {question}")

        # ---- Retrieval ----
        retrieved_context = search(question)

        # ---- Generation ----
        rag_answer = generate_response(question, retrieved_context)

        # ---- Evaluation ----
        scores = evaluate_response(question, retrieved_context, rag_answer)

        if scores:
            results.append(scores)
            print("✅ Scores:", scores)
        else:
            print("❌ Evaluation failed for this question")

    # ---- Summary ----
        if results:
            summary = summarize_results(results)

            output_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "results_per_question": results,
                "summary": summary
            }

            with open("evaluation_results.json", "w") as f:
                json.dump(output_data, f, indent=4)

            print("\n📁 Results saved to evaluation_results.json")
        else:
            print("No valid results to summarize.")


# --------------------------------------------------
# SUMMARY FUNCTION
# --------------------------------------------------
def summarize_results(results):

    groundedness_avg = statistics.mean([r["groundedness"] for r in results])
    relevance_avg = statistics.mean([r["relevance"] for r in results])
    depth_avg = statistics.mean([r["strategic_depth"] for r in results])
    actionability_avg = statistics.mean([r["actionability"] for r in results])

    print(f"\n{'='*60}")
    print("📊 FINAL EVALUATION SUMMARY")
    print("-" * 60)
    print(f"Groundedness Avg: {groundedness_avg:.2f}/5")
    print(f"Relevance Avg: {relevance_avg:.2f}/5")
    print(f"Strategic Depth Avg: {depth_avg:.2f}/5")
    print(f"Actionability Avg: {actionability_avg:.2f}/5")

    overall = statistics.mean(
        [groundedness_avg, relevance_avg, depth_avg, actionability_avg]
    )

    print(f"\n{'='*60}")
    print("📊 FINAL EVALUATION SUMMARY")
    print("-" * 60)
    print(f"Groundedness Avg: {groundedness_avg:.2f}/5")
    print(f"Relevance Avg: {relevance_avg:.2f}/5")
    print(f"Strategic Depth Avg: {depth_avg:.2f}/5")
    print(f"Actionability Avg: {actionability_avg:.2f}/5")
    print(f"\n🏁 Overall Score: {overall:.2f}/5")

    return {
        "groundedness_avg": groundedness_avg,
        "relevance_avg": relevance_avg,
        "strategic_depth_avg": depth_avg,
        "actionability_avg": actionability_avg,
        "overall_score": overall
    }

# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    run_full_evaluation()
