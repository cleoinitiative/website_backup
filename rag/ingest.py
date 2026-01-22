#!/usr/bin/env python3
"""
Ingestion script for CLEO Tech Help corpus.

Run this to index the tech help documents for the chatbot.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import RAGPipeline, PipelineConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Ingest the tech help corpus into the vector store."""
    
    # Path to corpus directory
    corpus_path = Path(__file__).parent / "corpus"
    
    if not corpus_path.exists():
        logger.error(f"Corpus directory not found: {corpus_path}")
        return 1
    
    logger.info(f"📚 Ingesting documents from: {corpus_path}")
    
    # Configure pipeline
    config = PipelineConfig(
        input_path=str(corpus_path),
        file_extensions=[".md", ".txt", ".pdf", ".html"],
        recursive=True,
        
        # Database settings
        db_path=os.getenv("RAG_DB_PATH", "./rag_db"),
        table_name="tech_help",
        
        # Chunking settings (smaller chunks for senior-friendly answers)
        chunk_size=400,
        chunk_overlap=50,
        min_chunk_size=80,
        
        # Embedding settings
        embedding_model="BAAI/bge-base-en-v1.5",
        embedding_batch_size=16,
        embedding_device=os.getenv("EMBEDDING_DEVICE", "cpu"),
        
        # Incremental updates
        incremental=True,
    )
    
    # Create and run pipeline
    pipeline = RAGPipeline(config)
    
    logger.info("🔄 Running ingestion pipeline (simple mode)...")
    stats = pipeline.run_simple()
    
    logger.info("✅ Ingestion complete!")
    logger.info(f"   Files found: {stats.get('files_found', 0)}")
    logger.info(f"   Files processed: {stats.get('files_processed', 0)}")
    logger.info(f"   Files skipped (unchanged): {stats.get('files_skipped', 0)}")
    logger.info(f"   Chunks created: {stats.get('chunks_created', 0)}")
    logger.info(f"   Database path: {stats.get('db_path', 'N/A')}")
    
    if stats.get('errors'):
        logger.warning(f"   Errors: {len(stats['errors'])}")
        for error in stats['errors']:
            logger.warning(f"     - {error['file']}: {error['error']}")
    
    # Test a sample query
    logger.info("\n🧪 Testing with sample query...")
    try:
        results = pipeline.search("How do I make a video call?", limit=3)
        if results:
            logger.info(f"   Found {len(results)} relevant chunks")
            logger.info(f"   Top result from: {results[0].source_path}")
        else:
            logger.warning("   No results found - check if documents were indexed")
    except Exception as e:
        logger.warning(f"   Test query failed: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
