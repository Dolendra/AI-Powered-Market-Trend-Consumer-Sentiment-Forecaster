"""
Example script demonstrating RAG query capabilities.
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Run example RAG queries."""
    try:
        from rag.retrieval_chain import RAGQueryEngine
        
        logger.info("=" * 70)
        logger.info("RAG QUERY EXAMPLES")
        logger.info("=" * 70)
        
        # Initialize engine
        logger.info("\nInitializing RAG engine...")
        engine = RAGQueryEngine()
        logger.info("✅ RAG engine ready!")
        
        # Example queries
        queries = [
            "What are the main complaints about sound quality?",
            "Which features receive the most positive feedback?",
            "What do users say about battery life and charging?",
            "What are common connectivity issues mentioned?",
        ]
        
        for i, query in enumerate(queries, 1):
            logger.info("\n" + "-" * 70)
            logger.info(f"Query {i}: {query}")
            logger.info("-" * 70)
            
            result = engine.query(query, k=5)
            
            logger.info(f"\nAnswer:\n{result['answer']}")
            logger.info(f"\nSources ({len(result['sources'])}):")
            
            for j, source in enumerate(result['sources'][:3], 1):
                logger.info(f"\n  {j}. {source['metadata'].get('evidence', 'N/A')}")
                logger.info(f"     Feature: {source['metadata'].get('feature', 'N/A')}")
                logger.info(f"     Sentiment: {source['metadata'].get('sentiment', 'N/A')}")
        
        # Feature insights example
        logger.info("\n" + "=" * 70)
        logger.info("FEATURE INSIGHTS EXAMPLE")
        logger.info("=" * 70)
        
        insights = engine.get_feature_insights("sound_quality")
        logger.info(f"\nFeature: {insights['feature']}")
        logger.info(f"\nSummary:\n{insights['summary']}")
        logger.info(f"\nPositive Examples: {len(insights['positive_examples'])}")
        logger.info(f"Negative Examples: {len(insights['negative_examples'])}")
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ Examples complete!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error("\nMake sure:")
        logger.error("1. Vector store is populated (run: python setup_rag.py)")
        logger.error("2. PINECONE_API_KEY is set in .env")
        logger.error("3. GROQ_API_KEY is set in .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
