"""
Setup script for RAG pipeline.
Helps users set up Pinecone and populate vector store.
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    missing = []
    
    try:
        import langchain
        logger.info("✅ langchain")
    except ImportError:
        missing.append("langchain")
        logger.error("❌ langchain")
    
    try:
        import pinecone
        logger.info("✅ pinecone-client")
    except ImportError:
        missing.append("pinecone-client")
        logger.error("❌ pinecone-client")
    
    try:
        import sentence_transformers
        logger.info("✅ sentence-transformers")
    except ImportError:
        missing.append("sentence-transformers")
        logger.error("❌ sentence-transformers")
    
    try:
        import plotly
        logger.info("✅ plotly")
    except ImportError:
        missing.append("plotly")
        logger.error("❌ plotly")
    
    try:
        import fastapi
        logger.info("✅ fastapi")
    except ImportError:
        missing.append("fastapi")
        logger.error("❌ fastapi")
    
    if missing:
        logger.error(f"\n❌ Missing dependencies: {', '.join(missing)}")
        logger.error("Install with: pip install -r requirements.txt")
        return False
    
    logger.info("\n✅ All dependencies installed!")
    return True


def check_data_file():
    """Check if processed data file exists."""
    from config import FEATURE_SENTIMENT_CLEANED_FILE
    
    if FEATURE_SENTIMENT_CLEANED_FILE.exists():
        logger.info(f"✅ Data file found: {FEATURE_SENTIMENT_CLEANED_FILE}")
        return True
    else:
        logger.warning(f"⚠️ Data file not found: {FEATURE_SENTIMENT_CLEANED_FILE}")
        logger.warning("   Run the main pipeline first to generate this file.")
        return False


def check_pinecone_config():
    """Check Pinecone API key configuration."""
    import os
    from dotenv import load_dotenv
    
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    api_key = os.getenv("PINECONE_API_KEY")
    
    if api_key:
        logger.info("✅ PINECONE_API_KEY configured")
        return True
    else:
        logger.error("❌ PINECONE_API_KEY not set")
        logger.error("   Add to .env file: PINECONE_API_KEY=your_key_here")
        logger.error("   Get your key from: https://www.pinecone.io/")
        return False


def populate_vector_store():
    """Populate Pinecone vector store."""
    logger.info("\n" + "=" * 70)
    logger.info("POPULATING VECTOR STORE")
    logger.info("=" * 70)
    
    try:
        from rag.vector_store import VectorStoreManager
        
        manager = VectorStoreManager()
        manager.populate_vector_store()
        
        logger.info("\n✅ Vector store populated successfully!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Error populating vector store: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("=" * 70)
    logger.info("RAG PIPELINE SETUP")
    logger.info("=" * 70)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check data file
    if not check_data_file():
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check Pinecone config
    if not check_pinecone_config():
        sys.exit(1)
    
    # Populate vector store
    response = input("\nPopulate vector store now? (y/n): ")
    if response.lower() == 'y':
        success = populate_vector_store()
        if success:
            logger.info("\n" + "=" * 70)
            logger.info("✅ SETUP COMPLETE!")
            logger.info("=" * 70)
            logger.info("\nNext steps:")
            logger.info("1. Test RAG query: python -m rag.retrieval_chain")
            logger.info("2. Generate dashboard: python -m dashboards.plotly_dashboard")
            logger.info("3. Start API server: python dashboards/api_server.py")
        else:
            sys.exit(1)
    else:
        logger.info("\nSkipping vector store population.")
        logger.info("Run later with: python -m rag.vector_store")


if __name__ == "__main__":
    main()
