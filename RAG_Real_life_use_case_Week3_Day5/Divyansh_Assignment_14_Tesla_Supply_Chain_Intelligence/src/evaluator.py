import os
import json
from groq import Groq


class RAGEvaluator:
    def __init__(self):
        # We use the same Groq client to act as the "Judge"
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def grade_response(self, question, context, answer):
        """
        ROLE: An AI Professor grading an Auditor's work.
        This provides the Benchmarking data for Tab 2.
        """
        prompt = f"""
        TASK: Grade the following RAG response for FAITHFULNESS and RELEVANCY.
        
        CONTEXT: {context}
        QUESTION: {question}
        STUDENT ANSWER: {answer}
        
        GRADING CRITERIA:
        1. Faithfulness (0-10): Is every fact in the answer supported by the context?
        2. Relevancy (0-10): Does the answer actually solve the user's question?
        
        OUTPUT FORMAT (Strict JSON only):
        {{
            "faithfulness": score,
            "relevancy": score,
            "reasoning": "A one-sentence explanation of the grade."
        }}
        """

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            # Fallback if the API is busy
            return {
                "faithfulness": 0,
                "relevancy": 0,
                "reasoning": f"Evaluation error: {str(e)}",
            }
