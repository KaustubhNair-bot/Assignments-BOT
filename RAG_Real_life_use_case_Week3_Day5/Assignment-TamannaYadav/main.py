"""
Tesla RAG System - CLI Entry Point
Main script for running the Tesla Policy and Product Knowledge Assistant.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import DATA_DIR, TOP_K, TEMPERATURE, TOP_P
from utils.logger import get_logger
from ingestion.pdf_loader import PDFLoader
from preprocessing.text_cleaner import TextCleaner
from chunking.text_splitter import RecursiveTextSplitter
from embeddings.embedding_generator import EmbeddingGenerator
from vector_db.faiss_store import FAISSVectorStore
from retrieval.retriever import Retriever
from prompts.templates import TeslaPromptTemplate
from rag.orchestrator import RAGOrchestrator
from evaluation.metrics import RAGEvaluator

logger = get_logger(__name__)


def build_index(data_dir: str = None, force_rebuild: bool = False):
    """
    Build the FAISS index from Tesla documents.
    
    Args:
        data_dir: Path to directory containing PDFs
        force_rebuild: Force rebuild even if index exists
    """
    data_path = Path(data_dir) if data_dir else DATA_DIR
    
    logger.info(f"Building index from documents in: {data_path}")
    
    vector_store = FAISSVectorStore()
    
    if not force_rebuild and vector_store.load():
        logger.info("Existing index loaded. Use --force to rebuild.")
        return vector_store
    
    logger.info("Step 1: Loading PDF documents...")
    loader = PDFLoader(str(data_path))
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents")
    
    logger.info("Step 2: Preprocessing documents...")
    cleaner = TextCleaner()
    cleaned_docs = cleaner.clean_batch(documents)
    
    logger.info("Step 3: Chunking documents...")
    splitter = RecursiveTextSplitter()
    chunks = splitter.split_documents(cleaned_docs)
    logger.info(f"Created {len(chunks)} chunks")
    
    logger.info("Step 4: Generating embeddings...")
    embedding_generator = EmbeddingGenerator()
    embedded_chunks = embedding_generator.embed_chunks(chunks)
    
    logger.info("Step 5: Building FAISS index...")
    vector_store.create_index()
    vector_store.add_embedded_chunks(embedded_chunks)
    
    logger.info("Step 6: Saving index to disk...")
    vector_store.save()
    
    stats = vector_store.get_stats()
    logger.info(f"Index built successfully: {stats}")
    
    return vector_store


def initialize_rag_system(data_dir: str = None):
    """
    Initialize the complete RAG system.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        RAGOrchestrator instance
    """
    vector_store = FAISSVectorStore()
    
    if not vector_store.load():
        logger.info("No existing index found. Building new index...")
        vector_store = build_index(data_dir)
    
    embedding_generator = EmbeddingGenerator()
    retriever = Retriever(embedding_generator, vector_store)
    prompt_template = TeslaPromptTemplate()
    orchestrator = RAGOrchestrator(retriever, prompt_template)
    
    logger.info("RAG system initialized successfully")
    return orchestrator


def interactive_mode(orchestrator: RAGOrchestrator):
    """
    Run interactive query mode.
    
    Args:
        orchestrator: RAGOrchestrator instance
    """
    print("\n" + "="*60)
    print("TESLA KNOWLEDGE ASSISTANT")
    print("="*60)
    print("Ask questions about Tesla policies and products.")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'sources' to toggle source display.")
    print("="*60 + "\n")
    
    show_sources = True
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using Tesla Knowledge Assistant. Goodbye!")
                break
            
            if query.lower() == 'sources':
                show_sources = not show_sources
                print(f"Source display: {'ON' if show_sources else 'OFF'}")
                continue
            
            print("\nProcessing your query...")
            result = orchestrator.query_with_sources(query)
            
            print("\n" + "-"*60)
            print("ANSWER:")
            print("-"*60)
            print(result['answer'])
            
            if show_sources and result['sources']:
                print("\n" + "-"*60)
                print("SOURCES:")
                print("-"*60)
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n[{i}] {source['filename']} (Score: {source['score']:.3f})")
                    print(f"    {source['excerpt']}")
            
            metadata = result['metadata']
            print(f"\n[Time: {metadata['total_time']:.2f}s | Chunks: {metadata['num_chunks']}]")
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\nError: {e}")


def run_evaluation(orchestrator: RAGOrchestrator, queries: list = None):
    """
    Run evaluation on sample queries.
    
    Args:
        orchestrator: RAGOrchestrator instance
        queries: List of test queries
    """
    if queries is None:
        queries = [
            "What is Tesla's privacy policy regarding customer data?",
            "How does Tesla handle vehicle service appointments?",
            "What are Tesla's environmental sustainability initiatives?",
            "What safety features are included in Tesla vehicles?",
            "How can I contact Tesla customer support?"
        ]
    
    evaluator = RAGEvaluator()
    
    print("\nRunning evaluation on sample queries...")
    evaluator.evaluate_batch(queries, orchestrator)
    
    report = evaluator.generate_report()
    print(report)
    
    evaluator.save_results()
    print("\nEvaluation results saved.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Tesla RAG System - Policy and Product Knowledge Assistant"
    )
    
    parser.add_argument(
        '--mode',
        choices=['build', 'query', 'interactive', 'evaluate', 'benchmark'],
        default='interactive',
        help='Operation mode (benchmark runs comprehensive evaluation)'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default=None,
        help='Path to directory containing Tesla PDFs'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        default=None,
        help='Single query to process (for query mode)'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=TOP_K,
        help='Number of chunks to retrieve'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=TEMPERATURE,
        help='LLM temperature parameter'
    )
    
    parser.add_argument(
        '--top-p',
        type=float,
        default=TOP_P,
        help='LLM top-p parameter'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force rebuild of index'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'build':
        build_index(args.data_dir, force_rebuild=args.force)
        
    elif args.mode == 'query':
        if not args.query:
            print("Error: --query is required for query mode")
            sys.exit(1)
        
        orchestrator = initialize_rag_system(args.data_dir)
        orchestrator.update_parameters(
            temperature=args.temperature,
            top_p=args.top_p
        )
        
        result = orchestrator.query_with_sources(args.query, top_k=args.top_k)
        
        print("\nAnswer:")
        print(result['answer'])
        print("\nSources:")
        for source in result['sources']:
            print(f"  - {source['filename']} (Score: {source['score']:.3f})")
            
    elif args.mode == 'interactive':
        orchestrator = initialize_rag_system(args.data_dir)
        orchestrator.update_parameters(
            temperature=args.temperature,
            top_p=args.top_p
        )
        interactive_mode(orchestrator)
        
    elif args.mode == 'evaluate':
        orchestrator = initialize_rag_system(args.data_dir)
        run_evaluation(orchestrator)
        
    elif args.mode == 'benchmark':
        from evaluation.run_benchmark import (
            run_full_benchmark,
            run_rag_comparison,
            run_temperature_experiment,
            generate_final_report
        )
        
        orchestrator = initialize_rag_system(args.data_dir)
        
        print("\n" + "="*60)
        print("TESLA RAG SYSTEM - COMPREHENSIVE BENCHMARK")
        print("="*60)
        
        pipeline, results = run_full_benchmark(orchestrator, "benchmark_results")
        benchmark_data = {
            "total_experiments": len(results),
            "results": [r.to_dict() for r in results],
            "aggregate_by_config": pipeline._get_aggregate_by_config()
        }
        
        rag_comparison = run_rag_comparison(orchestrator, "benchmark_results")
        temp_analysis = run_temperature_experiment(orchestrator, "benchmark_results")
        
        generate_final_report(benchmark_data, rag_comparison, temp_analysis, "benchmark_results")
        
        print("\nBenchmark complete! Check benchmark_results/ for reports.")


if __name__ == "__main__":
    main()
