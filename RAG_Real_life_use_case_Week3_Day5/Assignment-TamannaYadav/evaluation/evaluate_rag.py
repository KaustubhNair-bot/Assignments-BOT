"""RAG vs Base LLM Evaluation Script for Tesla Knowledge Assistant."""
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from groq import Groq
from config import settings
from ingestion.pdf_loader import PDFLoader
from preprocessing.text_cleaner import TextCleaner
from chunking.text_splitter import RecursiveTextSplitter
from embeddings.embedding_generator import EmbeddingGenerator
from vector_db.faiss_store import FAISSVectorStore
from retrieval.retriever import Retriever
from prompts.templates import TeslaPromptTemplate
from rag.orchestrator import RAGOrchestrator
from .metrics import EvaluationMetrics


class RAGvsBaseLLMEvaluator:
    """
    Evaluator for comparing RAG system vs Base LLM.
    
    Purpose:
    - Prove that RAG provides better, more grounded answers than base LLM
    - Measure key metrics: relevance, faithfulness, hallucination risk
    - Generate comparison report for documentation
    """
    
    # Tesla-specific queries for evaluation
    EVALUATION_QUERIES = [
        {
            "query": "What is Tesla's privacy policy regarding data collection from vehicles?",
            "category": "Privacy"
        },
        {
            "query": "How do I use the touchscreen controls in my Tesla vehicle?",
            "category": "Technical"
        },
        {
            "query": "What are Tesla's terms of service for vehicle owners?",
            "category": "Policy"
        },
        {
            "query": "What safety features does Tesla Autopilot include?",
            "category": "Technical"
        },
        {
            "query": "How does Tesla handle customer disputes and complaints?",
            "category": "Policy"
        }
    ]
    
    def __init__(self):
        """Initialize the evaluator."""
        self.metrics = EvaluationMetrics()
        self._groq_client = None
        self.rag_orchestrator = None
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize the RAG pipeline."""
        try:
            vector_store = FAISSVectorStore()
            
            if not vector_store.load():
                print("Building index from Tesla documents...")
                loader = PDFLoader(str(settings.DATA_DIR))
                documents = loader.load()
                
                cleaner = TextCleaner()
                cleaned_docs = cleaner.clean_batch(documents)
                
                splitter = RecursiveTextSplitter()
                chunks = splitter.split_documents(cleaned_docs)
                
                embedding_generator = EmbeddingGenerator()
                embedded_chunks = embedding_generator.embed_chunks(chunks)
                
                vector_store.create_index()
                vector_store.add_embedded_chunks(embedded_chunks)
                vector_store.save()
            
            embedding_generator = EmbeddingGenerator()
            retriever = Retriever(embedding_generator, vector_store)
            prompt_template = TeslaPromptTemplate()
            self.rag_orchestrator = RAGOrchestrator(retriever, prompt_template)
            print("RAG pipeline initialized successfully.")
            
        except Exception as e:
            print(f"Warning: Failed to initialize RAG pipeline: {e}")
            self.rag_orchestrator = None
    
    @property
    def groq_client(self) -> Groq:
        """Lazy initialization of Groq client."""
        if self._groq_client is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set in environment")
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
        return self._groq_client
    
    @property
    def is_ready(self) -> bool:
        """Check if evaluator is ready."""
        return self.rag_orchestrator is not None
    
    def get_rag_answer(self, query: str) -> tuple:
        """
        Get answer from RAG system (retrieval + LLM).
        
        Returns:
            Tuple of (answer, retrieved_contexts)
        """
        if not self.rag_orchestrator:
            return "RAG system not initialized.", []
        
        result = self.rag_orchestrator.query(query, top_k=5)
        
        answer = result.get('answer', '')
        chunks = result.get('chunks', [])
        contexts = [c.get('content', '')[:500] for c in chunks]
        
        return answer, contexts
    
    def get_base_llm_answer(self, query: str) -> str:
        """
        Get answer from base LLM (no retrieval, no context).
        
        This represents what the LLM knows from training data only.
        """
        prompt = f"""Answer the following query about Tesla based on your general knowledge.

Query: {query}

Provide a comprehensive answer about Tesla's policies, products, or services."""

        try:
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant answering questions about Tesla based on general knowledge."},
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
            query: The Tesla-related query
            category: Query category (Privacy, Technical, Policy)
            
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
        print("RAG vs Base LLM Evaluation - Tesla Knowledge Assistant")
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
    evaluator = RAGvsBaseLLMEvaluator()
    
    # Check if RAG is ready
    if not evaluator.is_ready:
        print("Error: RAG pipeline not ready. Please check your setup.")
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
    
    if rag_faithful > 0.3:
        print("✓ RAG answers are well-grounded in retrieved Tesla documents")


if __name__ == "__main__":
    main()
