"""RAG vs Base LLM Evaluation Script."""
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from groq import Groq
from config import settings
from rag import RAGPipeline
from .metrics import EvaluationMetrics


class RAGEvaluator:
    """
    Evaluator for comparing RAG system vs Base LLM.
    
    Purpose:
    - Prove that RAG provides better, more grounded answers than base LLM
    - Measure key metrics: relevance, faithfulness, hallucination risk
    - Generate comparison report for documentation
    """
    
    # Medical queries for evaluation (diverse specialties)
    EVALUATION_QUERIES = [
        {
            "query": "What are the common symptoms and treatment approaches for patients with chest pain and shortness of breath?",
            "category": "Cardiology"
        },
        {
            "query": "How should a patient with persistent cough, fever, and difficulty breathing be evaluated?",
            "category": "Pulmonology"
        },
        {
            "query": "What are the typical findings and management for a patient presenting with abdominal pain and nausea?",
            "category": "Gastroenterology"
        },
        {
            "query": "Describe the evaluation process for a patient with headache and dizziness symptoms.",
            "category": "Neurology"
        },
        {
            "query": "What are the key considerations when treating a patient with joint pain and swelling?",
            "category": "Orthopedics"
        }
    ]
    
    def __init__(self):
        """Initialize the evaluator."""
        self.rag_pipeline = RAGPipeline()
        self.metrics = EvaluationMetrics()
        self._groq_client = None
        
        # Initialize RAG pipeline
        if not self.rag_pipeline.initialize():
            print("Warning: RAG pipeline not initialized. Run build_index.py first.")
    
    @property
    def groq_client(self) -> Groq:
        """Lazy initialization of Groq client."""
        if self._groq_client is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set in environment")
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
        return self._groq_client
    
    def get_rag_answer(self, query: str) -> tuple:
        """
        Get answer from RAG system (retrieval + LLM).
        
        Returns:
            Tuple of (answer, retrieved_contexts)
        """
        # Search for similar cases
        results = self.rag_pipeline.search_similar_cases(query, top_k=5)
        
        if not results:
            return "No relevant cases found.", []
        
        # Extract contexts
        contexts = [r.get('transcription', '')[:500] for r in results]
        
        # Build context for LLM
        context_text = "\n\n".join([
            f"Case {i+1} ({r.get('specialty', 'Unknown')}):\n{r.get('description', '')}\n{r.get('transcription', '')[:300]}"
            for i, r in enumerate(results[:3])
        ])
        
        # Generate answer using RAG
        prompt = f"""Based on the following medical case records from our database, answer the query.

Query: {query}

Retrieved Medical Cases:
{context_text}

Provide a comprehensive answer based ONLY on the information from these cases. 
If the cases don't contain relevant information, say so.
Do not make up information not present in the cases."""

        try:
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant. Answer based only on the provided case records."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error generating RAG answer: {str(e)}"
        
        return answer, contexts
    
    def get_base_llm_answer(self, query: str) -> str:
        """
        Get answer from base LLM (no retrieval, no context).
        
        This represents what the LLM knows from training data only.
        """
        prompt = f"""Answer the following medical query based on your general medical knowledge.

Query: {query}

Provide a comprehensive answer about symptoms, diagnosis, and treatment approaches."""

        try:
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant. Answer based on general medical knowledge."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating base LLM answer: {str(e)}"
    
    def evaluate_single_query(self, query: str, category: str = "") -> Dict[str, Any]:
        """
        Evaluate a single query on both RAG and Base LLM.
        
        Args:
            query: The medical query
            category: Medical category/specialty
            
        Returns:
            Dictionary with answers and metrics
        """
        print(f"\nEvaluating: {query[:50]}...")
        
        # Get answers from both systems
        rag_answer, contexts = self.get_rag_answer(query)
        base_llm_answer = self.get_base_llm_answer(query)
        
        # Calculate metrics
        metrics = self.metrics.calculate_all_metrics(
            query=query,
            rag_answer=rag_answer,
            base_llm_answer=base_llm_answer,
            retrieved_contexts=contexts
        )
        
        return {
            "query": query,
            "category": category,
            "rag_answer": rag_answer,
            "base_llm_answer": base_llm_answer,
            "retrieved_contexts": contexts,
            "metrics": metrics
        }
    
    def run_full_evaluation(self, queries: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Run evaluation on all queries.
        
        Args:
            queries: Optional list of query dicts. Uses default if not provided.
            
        Returns:
            List of evaluation results
        """
        queries = queries or self.EVALUATION_QUERIES
        results = []
        
        print("=" * 60)
        print("RAG vs Base LLM Evaluation")
        print("=" * 60)
        
        for q in queries:
            result = self.evaluate_single_query(q["query"], q.get("category", ""))
            results.append(result)
            
            # Print quick summary
            rag_rel = result["metrics"]["rag"]["answer_relevance"]
            llm_rel = result["metrics"]["base_llm"]["answer_relevance"]
            rag_hall = result["metrics"]["rag"]["hallucination_risk"]
            llm_hall = result["metrics"]["base_llm"]["hallucination_risk"]
            
            print(f"  RAG Relevance: {rag_rel:.3f} | Base LLM Relevance: {llm_rel:.3f}")
            print(f"  RAG Hallucination Risk: {rag_hall:.3f} | Base LLM Risk: {llm_hall:.3f}")
        
        return results
    
    def save_results(self, results: List[Dict], output_path: Path = None) -> None:
        """Save evaluation results to JSON file."""
        output_path = output_path or Path(__file__).parent / "results.json"
        
        # Prepare serializable results
        serializable_results = []
        for r in results:
            serializable_results.append({
                "query": r["query"],
                "category": r["category"],
                "rag_answer": r["rag_answer"],
                "base_llm_answer": r["base_llm_answer"],
                "metrics": r["metrics"],
                "timestamp": datetime.now().isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate markdown evaluation report."""
        return self.metrics.generate_comparison_report(results)


def main():
    """Run the evaluation."""
    evaluator = RAGEvaluator()
    
    # Check if RAG is ready
    if not evaluator.rag_pipeline.is_ready:
        print("Error: RAG pipeline not ready. Please run:")
        print("  python scripts/build_index.py")
        return
    
    # Run evaluation
    results = evaluator.run_full_evaluation()
    
    # Save results
    evaluator.save_results(results)
    
    # Generate and save report
    report = evaluator.generate_report(results)
    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    
    # Calculate averages
    rag_relevance = sum(r["metrics"]["rag"]["answer_relevance"] for r in results) / len(results)
    llm_relevance = sum(r["metrics"]["base_llm"]["answer_relevance"] for r in results) / len(results)
    rag_faithful = sum(r["metrics"]["rag"]["faithfulness"] for r in results) / len(results)
    rag_halluc = sum(r["metrics"]["rag"]["hallucination_risk"] for r in results) / len(results)
    llm_halluc = sum(r["metrics"]["base_llm"]["hallucination_risk"] for r in results) / len(results)
    
    print(f"\nAverage Answer Relevance:")
    print(f"  RAG System:  {rag_relevance:.3f}")
    print(f"  Base LLM:    {llm_relevance:.3f}")
    
    print(f"\nRAG Faithfulness (grounding in context): {rag_faithful:.3f}")
    
    print(f"\nHallucination Risk:")
    print(f"  RAG System:  {rag_halluc:.3f} (lower is better)")
    print(f"  Base LLM:    {llm_halluc:.3f}")
    
    if rag_halluc < llm_halluc:
        print("\n✓ RAG system shows LOWER hallucination risk than base LLM")
    
    if rag_faithful > 0.5:
        print("✓ RAG answers are well-grounded in retrieved context")


if __name__ == "__main__":
    main()
