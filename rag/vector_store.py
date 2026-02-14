"""
Vector store module for RAG pipeline using Pinecone and LangChain.
Handles embedding generation, vector storage, and retrieval.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from pinecone import Pinecone, ServerlessSpec

# Try to import langchain-pinecone (newer package)
try:
    from langchain_pinecone import PineconeVectorStore
    USE_LANGCHAIN_PINECONE = True
except ImportError:
    USE_LANGCHAIN_PINECONE = False

# Import embeddings (try newest first, fallback to older)
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings

# Import Pinecone vector store (try newer first, fallback to older)
if not USE_LANGCHAIN_PINECONE:
    try:
        from langchain_community.vectorstores import Pinecone as LangChainPinecone
    except ImportError:
        from langchain.vectorstores import Pinecone as LangChainPinecone

from langchain.text_splitter import RecursiveCharacterTextSplitter
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSED_DATA_DIR, INTERMEDIATE_DATA_DIR

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector store operations for RAG pipeline."""
    
    def __init__(
        self,
        pinecone_api_key: str = None,
        pinecone_index_name: str = "redmi-sentiment-reviews",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store manager.
        
        Args:
            pinecone_api_key: Pinecone API key (from env if not provided)
            pinecone_index_name: Name of Pinecone index
            embedding_model: HuggingFace embedding model name
        """
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not set in environment or .env file")
        
        self.index_name = pinecone_index_name
        self.embedding_model = embedding_model
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Initialize embeddings
        logger.info(f"Loading embedding model: {embedding_model}")
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except ImportError:
            from langchain.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        
        self.vector_store = None
        self._ensure_index()
    
    def _ensure_index(self) -> None:
        """Create Pinecone index if it doesn't exist."""
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Index '%s' created successfully", self.index_name)
            else:
                logger.info("Index '%s' already exists", self.index_name)
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error("Error managing Pinecone index: %s", e)
            raise
    
    def load_data_from_csv(self, csv_path: Path) -> pd.DataFrame:
        """Load processed data from CSV file."""
        logger.info(f"Loading data from: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info("Loaded %s records", len(df))
        return df
    
    def prepare_documents(self, df: pd.DataFrame) -> List[Dict]:
        """
        Prepare documents for vectorization.
        Creates rich text documents with metadata.
        """
        documents = []
        
        for idx, row in df.iterrows():
            # Create document text with context
            text_parts = []
            
            if pd.notna(row.get("evidence")):
                text_parts.append(f"Review: {row['evidence']}")
            
            if pd.notna(row.get("feature")):
                text_parts.append(f"Feature: {row['feature']}")
            
            if pd.notna(row.get("model")):
                text_parts.append(f"Product: {row['model']}")
            
            if pd.notna(row.get("sentiment")):
                text_parts.append(f"Sentiment: {row['sentiment']}")
            
            document_text = " | ".join(text_parts)
            
            # Create metadata
            metadata = {
                "comment_id": str(row.get("comment_id", "")),
                "model": str(row.get("model", "")),
                "feature": str(row.get("feature", "")),
                "sentiment": str(row.get("sentiment", "")),
                "evidence": str(row.get("evidence", "")),
                "likes": int(row.get("likes", 0)),
            }
            
            documents.append({
                "text": document_text,
                "metadata": metadata
            })
        
        logger.info("Prepared %s documents", len(documents))
        return documents
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Split documents into chunks for better retrieval."""
        chunked_docs = []
        
        for doc in documents:
            # Split text if too long
            chunks = self.text_splitter.split_text(doc["text"])
            
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    "text": chunk,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                })
        
        logger.info("Created %s chunks from %s documents", len(chunked_docs), len(documents))
        return chunked_docs
    
    def populate_vector_store(self, csv_path: Path = None) -> None:
        """
        Populate vector store with documents from CSV.
        
        Args:
            csv_path: Path to feature_sentiment_cleaned.csv
        """
        if csv_path is None:
            csv_path = PROCESSED_DATA_DIR / "feature_sentiment_cleaned.csv"
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Data file not found: {csv_path}")
        
        logger.info("=" * 70)
        logger.info("📥 POPULATING VECTOR STORE")
        logger.info("=" * 70)
        
        # Load and prepare data
        df = self.load_data_from_csv(csv_path)
        documents = self.prepare_documents(df)
        chunked_docs = self.chunk_documents(documents)
        
        # Check if index already has data
        stats = self.index.describe_index_stats()
        existing_count = stats.get("total_vector_count", 0)
        
        if existing_count > 0:
            logger.warning("Index already contains %s vectors", existing_count)
            response = input("Do you want to delete existing vectors and re-index? (y/n): ")
            if response.lower() == 'y':
                logger.info("Deleting existing index...")
                self.pc.delete_index(self.index_name)
                self._ensure_index()
            else:
                logger.info("Skipping population. Using existing vectors.")
                return
        
        # Create LangChain vector store
        logger.info("Creating vector embeddings and uploading to Pinecone...")
        
        texts = [doc["text"] for doc in chunked_docs]
        metadatas = [doc["metadata"] for doc in chunked_docs]
        
        # Batch upload to avoid timeout
        batch_size = 100
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_texts)} documents)...")
            
            if USE_LANGCHAIN_PINECONE:
                # Use newer langchain-pinecone package
                from langchain_pinecone import PineconeVectorStore
                if i == 0:
                    # First batch - create new store
                    self.vector_store = PineconeVectorStore.from_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas,
                        embedding=self.embeddings,
                        index_name=self.index_name
                    )
                else:
                    # Subsequent batches - add to existing
                    self.vector_store.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas
                    )
            else:
                # Use older langchain_community
                self.vector_store = LangChainPinecone.from_texts(
                    texts=batch_texts,
                    metadatas=batch_metadatas,
                    embedding=self.embeddings,
                    index_name=self.index_name,
                    pinecone_api_key=self.pinecone_api_key
                )
        
        logger.info("Vector store populated successfully")
        
        # Verify
        stats = self.index.describe_index_stats()
        logger.info("Index stats: %s vectors", stats.get("total_vector_count", 0))
    
    def get_retriever(self, k: int = 5, filter_dict: Dict = None):
        """Get LangChain retriever for querying."""
        if self.vector_store is None:
            # Connect to existing index
            if USE_LANGCHAIN_PINECONE:
                from langchain_pinecone import PineconeVectorStore
                self.vector_store = PineconeVectorStore.from_existing_index(
                    index_name=self.index_name,
                    embedding=self.embeddings
                )
            else:
                self.vector_store = LangChainPinecone.from_existing_index(
                    index_name=self.index_name,
                    embedding=self.embeddings,
                    pinecone_api_key=self.pinecone_api_key
                )
        
        retriever = self.vector_store.as_retriever(
            search_kwargs={
                "k": k,
                "filter": filter_dict or {}
            }
        )
        
        return retriever
    
    def search(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filters (e.g., {"sentiment": "positive"})
        
        Returns:
            List of relevant documents with metadata
        """
        if self.vector_store is None:
            if USE_LANGCHAIN_PINECONE:
                from langchain_pinecone import PineconeVectorStore
                self.vector_store = PineconeVectorStore.from_existing_index(
                    index_name=self.index_name,
                    embedding=self.embeddings
                )
            else:
                self.vector_store = LangChainPinecone.from_existing_index(
                    index_name=self.index_name,
                    embedding=self.embeddings,
                    pinecone_api_key=self.pinecone_api_key
                )
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict or {}
        )
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return formatted_results
    
    def delete_index(self) -> None:
        """Delete the Pinecone index (use with caution!)."""
        logger.warning("Deleting index: %s", self.index_name)
        self.pc.delete_index(self.index_name)
        logger.info("Index deleted")


def main():
    """Main function to populate vector store."""
    import sys
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        manager = VectorStoreManager()
        manager.populate_vector_store()
        logger.info("Vector store setup complete")
        
    except Exception as e:
        logger.error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
