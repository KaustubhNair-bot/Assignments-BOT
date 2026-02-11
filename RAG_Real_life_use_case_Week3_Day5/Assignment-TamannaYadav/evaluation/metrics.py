"""
Evaluation Metrics for RAG vs Base LLM comparison.
Implements standard RAG evaluation metrics inspired by RAGAS framework.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import time
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import numpy as np

# ROUGE Score
try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False

# BERTScore
try:
    from bert_score import score as bert_score_fn
    BERT_SCORE_AVAILABLE = True
except ImportError:
    BERT_SCORE_AVAILABLE = False

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    query: str
    rag_answer: str
    base_llm_answer: str
    retrieved_contexts: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


class EvaluationMetrics:
    """
    Evaluation metrics for comparing RAG vs Base LLM responses.
    
    Metrics Implemented:
    1. Answer Relevance - How relevant is the answer to the query?
    2. Faithfulness - Does the answer stick to provided context (RAG only)?
    3. Hallucination Risk - Does the response contain made-up information?
    4. ROUGE-L Score - N-gram overlap between generated and reference text
    5. MRR (Mean Reciprocal Rank) - Retriever ranking quality
    
    Why These Metrics:
    - They are standard in RAG evaluation (RAGAS framework inspired)
    - ROUGE-L is industry-standard NLG metric for text generation quality
    - MRR evaluates retriever ranking quality
    - They help prove RAG provides grounded, factual responses
    - They highlight where base LLM may hallucinate
    """
    
    def __init__(self, groq_client=None):
        """
        Initialize metrics calculator.
        
        Args:
            groq_client: Optional Groq client for LLM-based evaluation
        """
        self.groq_client = groq_client
    
    def calculate_all_metrics(
        self, 
        query: str,
        rag_answer: str,
        base_llm_answer: str,
        retrieved_contexts: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate all evaluation metrics for both RAG and Base LLM.
        
        Args:
            query: The user query
            rag_answer: Answer from RAG system
            base_llm_answer: Answer from base LLM (no context)
            retrieved_contexts: List of retrieved document texts
            
        Returns:
            Dictionary with metrics for both systems
        """
        results = {
            "rag": {},
            "base_llm": {}
        }
        
        # Answer Relevance (both systems)
        results["rag"]["answer_relevance"] = self.answer_relevance(query, rag_answer)
        results["base_llm"]["answer_relevance"] = self.answer_relevance(query, base_llm_answer)
        
        # Faithfulness (RAG only - measures grounding in context)
        results["rag"]["faithfulness"] = self.faithfulness(rag_answer, retrieved_contexts)
        results["base_llm"]["faithfulness"] = 0.0  # No context to be faithful to
        
        # Hallucination Detection (heuristic-based)
        results["rag"]["hallucination_risk"] = self.hallucination_risk(rag_answer, retrieved_contexts)
        results["base_llm"]["hallucination_risk"] = self.hallucination_risk(base_llm_answer, [])
        
        # ROUGE Score (using context as reference for RAG)
        if retrieved_contexts:
            reference_text = " ".join(retrieved_contexts)
            results["rag"]["rouge_l"] = self.rouge_score(rag_answer, reference_text)
        else:
            results["rag"]["rouge_l"] = 0.0
        results["base_llm"]["rouge_l"] = 0.0  # No reference for base LLM
        
        # MRR (Mean Reciprocal Rank) - for retriever evaluation
        results["rag"]["mrr"] = self.mean_reciprocal_rank(query, retrieved_contexts)
        results["base_llm"]["mrr"] = 0.0  # No retrieval
        
        return results
    
    def answer_relevance(self, query: str, answer: str) -> float:
        """
        Measure how relevant the answer is to the query.
        
        Uses keyword overlap and semantic indicators.
        Score: 0.0 (irrelevant) to 1.0 (highly relevant)
        """
        if not answer or not query:
            return 0.0
        
        # Extract key terms from query
        query_terms = set(self._extract_key_terms(query.lower()))
        answer_terms = set(self._extract_key_terms(answer.lower()))
        
        if not query_terms:
            return 0.5  # Neutral if no key terms
        
        # Calculate overlap
        overlap = len(query_terms.intersection(answer_terms))
        relevance = min(overlap / len(query_terms), 1.0)
        
        # Boost if answer is substantial
        if len(answer) > 100:
            relevance = min(relevance + 0.1, 1.0)
        
        return round(relevance, 3)
    
    def faithfulness(self, answer: str, contexts: List[str]) -> float:
        """
        Measure how faithful the answer is to the provided contexts.
        
        Checks if claims in the answer can be traced to context.
        Score: 0.0 (unfaithful) to 1.0 (fully grounded)
        """
        if not contexts or not answer:
            return 0.0
        
        # Combine all contexts
        combined_context = " ".join(contexts).lower()
        
        # Extract key claims/terms from answer
        answer_terms = set(self._extract_key_terms(answer.lower()))
        
        if not answer_terms:
            return 0.5
        
        # Check how many answer terms appear in context
        grounded_terms = sum(1 for term in answer_terms if term in combined_context)
        faithfulness = grounded_terms / len(answer_terms)
        
        return round(min(faithfulness, 1.0), 3)
    
    def context_precision(self, query: str, contexts: List[str]) -> float:
        """
        Measure how relevant the retrieved contexts are to the query.
        
        Score: 0.0 (irrelevant contexts) to 1.0 (all contexts relevant)
        """
        if not contexts or not query:
            return 0.0
        
        query_terms = set(self._extract_key_terms(query.lower()))
        
        if not query_terms:
            return 0.5
        
        relevant_count = 0
        for context in contexts:
            context_terms = set(self._extract_key_terms(context.lower()))
            overlap = len(query_terms.intersection(context_terms))
            if overlap >= 1:  # At least one key term matches
                relevant_count += 1
        
        precision = relevant_count / len(contexts)
        return round(precision, 3)
    
    def answer_completeness(self, query: str, answer: str) -> float:
        """
        Measure how complete the answer is.
        
        Checks for:
        - Sufficient length
        - Multiple aspects covered
        - Structured response
        """
        if not answer:
            return 0.0
        
        score = 0.0
        
        # Length check (Tesla answers should be detailed)
        if len(answer) > 50:
            score += 0.2
        if len(answer) > 150:
            score += 0.2
        if len(answer) > 300:
            score += 0.1
        
        # Check for structured elements
        if any(marker in answer for marker in ['1.', '2.', '-', '•', ':']):
            score += 0.2
        
        # Check for Tesla-specific terminology
        tesla_terms = ['vehicle', 'autopilot', 'charging', 'battery', 'touchscreen', 
                      'supercharger', 'model', 'driver', 'safety', 'software']
        term_count = sum(1 for term in tesla_terms if term.lower() in answer.lower())
        score += min(term_count * 0.05, 0.3)
        
        return round(min(score, 1.0), 3)
    
    def hallucination_risk(self, answer: str, contexts: List[str]) -> float:
        """
        Estimate the risk of hallucination in the answer.
        
        Higher score = Higher risk of hallucination
        Score: 0.0 (low risk) to 1.0 (high risk)
        
        For RAG: Low risk if grounded in context
        For Base LLM: Higher risk as no grounding
        """
        if not answer:
            return 0.0
        
        # Indicators of potential hallucination
        risk_score = 0.0
        
        # Specific numbers/statistics without context
        has_specific_numbers = bool(re.search(r'\b\d{2,}%|\b\d+\.\d+\b', answer))
        if has_specific_numbers and not contexts:
            risk_score += 0.3
        
        # Definitive claims without hedging
        definitive_phrases = ['always', 'never', 'definitely', 'certainly', 'proven that', 'studies show']
        for phrase in definitive_phrases:
            if phrase in answer.lower():
                risk_score += 0.1
        
        # If no context provided (base LLM), higher base risk
        if not contexts:
            risk_score += 0.3
        else:
            # Check grounding - if well grounded, lower risk
            faithfulness = self.faithfulness(answer, contexts)
            risk_score += (1 - faithfulness) * 0.3
        
        return round(min(risk_score, 1.0), 3)
    
    def rouge_score(self, generated: str, reference: str) -> float:
        """
        Calculate ROUGE-L score between generated text and reference.
        
        ROUGE-L measures longest common subsequence (LCS) overlap.
        Score: 0.0 to 1.0 (higher is better)
        """
        if not ROUGE_AVAILABLE:
            # Fallback to simple LCS-based calculation
            return self._simple_rouge_l(generated, reference)
        
        if not generated or not reference:
            return 0.0
        
        try:
            scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            scores = scorer.score(reference, generated)
            return round(scores['rougeL'].fmeasure, 3)
        except Exception:
            return self._simple_rouge_l(generated, reference)
    
    def _simple_rouge_l(self, generated: str, reference: str) -> float:
        """Simple ROUGE-L fallback using LCS."""
        if not generated or not reference:
            return 0.0
        
        gen_words = generated.lower().split()
        ref_words = reference.lower().split()
        
        if not gen_words or not ref_words:
            return 0.0
        
        # Simple LCS length calculation
        m, n = len(gen_words), len(ref_words)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if gen_words[i-1] == ref_words[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[m][n]
        precision = lcs_length / m if m > 0 else 0
        recall = lcs_length / n if n > 0 else 0
        
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * precision * recall / (precision + recall)
        return round(f1, 3)
    
    def bert_score(self, generated: str, reference: str) -> float:
        """
        Calculate BERTScore between generated text and reference.
        
        BERTScore uses BERT embeddings for semantic similarity.
        Score: 0.0 to 1.0 (higher is better)
        """
        if not BERT_SCORE_AVAILABLE:
            # Fallback to simple semantic overlap
            return self._simple_semantic_score(generated, reference)
        
        if not generated or not reference:
            return 0.0
        
        try:
            # Calculate BERTScore (returns P, R, F1)
            P, R, F1 = bert_score_fn(
                [generated], 
                [reference], 
                lang="en", 
                verbose=False,
                rescale_with_baseline=True
            )
            return round(F1.item(), 3)
        except Exception:
            return self._simple_semantic_score(generated, reference)
    
    def _simple_semantic_score(self, generated: str, reference: str) -> float:
        """Simple semantic similarity fallback using word overlap."""
        if not generated or not reference:
            return 0.0
        
        gen_terms = set(self._extract_key_terms(generated.lower()))
        ref_terms = set(self._extract_key_terms(reference.lower()))
        
        if not gen_terms or not ref_terms:
            return 0.0
        
        intersection = len(gen_terms.intersection(ref_terms))
        union = len(gen_terms.union(ref_terms))
        
        return round(intersection / union, 3) if union > 0 else 0.0
    
    def mean_reciprocal_rank(self, query: str, retrieved_contexts: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR) for retriever evaluation.
        
        MRR = 1/rank of first relevant document
        Score: 0.0 to 1.0 (higher is better, 1.0 means first doc is relevant)
        """
        if not retrieved_contexts or not query:
            return 0.0
        
        query_terms = set(self._extract_key_terms(query.lower()))
        
        if not query_terms:
            return 0.5
        
        # Find rank of first relevant document
        for rank, context in enumerate(retrieved_contexts, 1):
            context_terms = set(self._extract_key_terms(context.lower()))
            overlap = len(query_terms.intersection(context_terms))
            
            # Consider relevant if at least 2 query terms match
            if overlap >= 2:
                return round(1.0 / rank, 3)
        
        # No relevant document found
        return 0.0
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text, filtering stopwords."""
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
            'and', 'but', 'if', 'or', 'because', 'until', 'while', 'this', 'that',
            'these', 'those', 'what', 'which', 'who', 'whom', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my',
            'your', 'his', 'its', 'our', 'their', 'about', 'also'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter stopwords and return unique terms
        return [w for w in words if w not in stopwords]
    
    def generate_comparison_report(
        self, 
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a markdown comparison report from evaluation results.
        
        Args:
            results: List of evaluation result dictionaries
            
        Returns:
            Markdown formatted report
        """
        report = "# RAG vs Base LLM Evaluation Report\n\n"
        report += "## Summary\n\n"
        
        # Calculate averages
        rag_avg = {}
        llm_avg = {}
        
        metrics = ['answer_relevance', 'faithfulness', 'hallucination_risk', 'rouge_l', 'mrr']
        
        for metric in metrics:
            rag_values = [r['metrics']['rag'].get(metric, 0) for r in results]
            llm_values = [r['metrics']['base_llm'].get(metric, 0) for r in results]
            rag_avg[metric] = sum(rag_values) / len(rag_values) if rag_values else 0
            llm_avg[metric] = sum(llm_values) / len(llm_values) if llm_values else 0
        
        report += "| Metric | RAG System | Base LLM | Winner |\n"
        report += "|--------|------------|----------|--------|\n"
        
        for metric in metrics:
            rag_val = rag_avg[metric]
            llm_val = llm_avg[metric]
            
            # For hallucination_risk, lower is better
            if metric == 'hallucination_risk':
                winner = "RAG ✓" if rag_val < llm_val else ("Base LLM ✓" if llm_val < rag_val else "Tie")
            else:
                winner = "RAG ✓" if rag_val > llm_val else ("Base LLM ✓" if llm_val > rag_val else "Tie")
            
            metric_display = metric.replace('_', ' ').title()
            report += f"| {metric_display} | {rag_val:.3f} | {llm_val:.3f} | {winner} |\n"
        
        report += "\n## Detailed Results\n\n"
        
        for i, result in enumerate(results, 1):
            report += f"### Query {i}: {result['query']}\n\n"
            report += f"**RAG Answer:**\n{result['rag_answer'][:500]}...\n\n"
            report += f"**Base LLM Answer:**\n{result['base_llm_answer'][:500]}...\n\n"
            report += "**Metrics:**\n\n"
            report += "| Metric | RAG | Base LLM |\n"
            report += "|--------|-----|----------|\n"
            for metric in metrics:
                rag_val = result['metrics']['rag'].get(metric, 0)
                llm_val = result['metrics']['base_llm'].get(metric, 0)
                report += f"| {metric.replace('_', ' ').title()} | {rag_val:.3f} | {llm_val:.3f} |\n"
            report += "\n---\n\n"
        
        return report


class RAGEvaluator:
    """
    Legacy evaluator for backward compatibility.
    Wraps EvaluationMetrics for simple RAG-only evaluation.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("evaluation_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[EvaluationResult] = []
        self.metrics = EvaluationMetrics()
        logger.info(f"Initialized RAGEvaluator with output_dir={self.output_dir}")
    
    def evaluate_single(self, query: str, rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single RAG query result."""
        chunks = rag_result.get('chunks', [])
        contexts = [c.get('content', '') for c in chunks]
        
        return {
            'query': query,
            'answer': rag_result.get('answer', ''),
            'contexts': contexts,
            'metadata': rag_result.get('metadata', {})
        }
    
    def save_results(self, results: List[Dict], filename: str = "results.json"):
        """Save evaluation results to JSON file."""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to: {output_path}")
    
    def clear_results(self):
        """Clear all stored results."""
        self.results = []
        logger.info("Cleared evaluation results")
