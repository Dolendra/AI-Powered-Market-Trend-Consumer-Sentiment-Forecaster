"""
LangChain retrieval chain for RAG queries.
Provides semantic search and context-aware question answering.
"""

import logging
from typing import List, Dict, Optional

# Import LangChain components
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GROQ_API_KEY, GROQ_MODEL
from rag.vector_store import VectorStoreManager
from rag.groq_llm import GroqLLM

logger = logging.getLogger(__name__)


class RAGQueryEngine:
    """RAG query engine for semantic search and question answering."""
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager = None,
        llm_model: str = None,
        temperature: float = 0.1
    ):
        """
        Initialize RAG query engine.
        
        Args:
            vector_store_manager: VectorStoreManager instance
            llm_model: Groq model name
            temperature: LLM temperature
        """
        self.vector_store_manager = vector_store_manager or VectorStoreManager()
        self.llm_model = llm_model or GROQ_MODEL
        self.temperature = temperature
        
        # Initialize LLM using custom Groq wrapper
        self.llm = GroqLLM(
            groq_api_key=GROQ_API_KEY,
            model_name=self.llm_model,
            temperature=temperature
        )
        
        # Create custom prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an AI assistant helping analyze Redmi product reviews and sentiment data.

Context from reviews:
{context}

Question: {question}

Based on the context provided above, answer the question. If the context doesn't contain enough information, say so.
Focus on providing specific insights about product features, sentiment patterns, and user feedback.

Answer:"""
        )
        
        self.qa_chain = None
        self._initialize_chain()
    
    def _initialize_chain(self) -> None:
        """Initialize the QA chain."""
        retriever = self.vector_store_manager.get_retriever(k=5)
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        
        logger.info("✅ RAG query chain initialized")
    
    def query(self, question: str, k: int = 5, filters: Dict = None) -> Dict:
        """
        Query the RAG system with a question.
        
        Args:
            question: User question
            k: Number of documents to retrieve
            filters: Metadata filters (e.g., {"sentiment": "positive", "feature": "sound_quality"})
        
        Returns:
            Dictionary with answer and source documents
        """
        logger.info(f"🔍 Query: {question}")
        
        # Update retriever with filters if provided
        if filters:
            retriever = self.vector_store_manager.get_retriever(k=k, filter_dict=filters)
            self.qa_chain.retriever = retriever
        
        try:
            result = self.qa_chain({"query": question})
            
            # Format response
            response = {
                "question": question,
                "answer": result["result"],
                "sources": []
            }
            
            # Extract source documents
            for doc in result.get("source_documents", []):
                response["sources"].append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                })
            
            logger.info(f"✅ Retrieved {len(response['sources'])} relevant documents")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error querying RAG: {e}")
            return {
                "question": question,
                "answer": f"Error processing query: {str(e)}",
                "sources": []
            }
    
    def search_similar_reviews(
        self,
        query: str,
        k: int = 10,
        sentiment_filter: str = None,
        feature_filter: str = None,
        model_filter: str = None
    ) -> List[Dict]:
        """
        Search for similar reviews without LLM generation.
        Useful for finding specific examples.
        
        Args:
            query: Search query
            k: Number of results
            sentiment_filter: Filter by sentiment (positive/negative/neutral)
            feature_filter: Filter by feature name
            model_filter: Filter by product model
        
        Returns:
            List of similar reviews with metadata
        """
        filters = {}
        if sentiment_filter:
            filters["sentiment"] = sentiment_filter
        if feature_filter:
            filters["feature"] = feature_filter
        if model_filter:
            filters["model"] = model_filter
        
        results = self.vector_store_manager.search(
            query=query,
            k=k,
            filter_dict=filters if filters else None
        )
        
        return results
    
    def get_feature_insights(self, feature: str) -> Dict:
        """
        Get comprehensive insights about a specific feature.
        
        Args:
            feature: Feature name (e.g., "sound_quality", "battery")
        
        Returns:
            Dictionary with feature insights
        """
        question = f"What are the main concerns and positive feedback about {feature} in Redmi product reviews?"
        
        # Filter by feature
        filters = {"feature": feature}
        response = self.query(question, k=10, filters=filters)
        
        # Get sentiment breakdown
        positive_reviews = self.search_similar_reviews(
            query=f"positive feedback about {feature}",
            k=5,
            sentiment_filter="positive",
            feature_filter=feature
        )
        
        negative_reviews = self.search_similar_reviews(
            query=f"negative feedback about {feature}",
            k=5,
            sentiment_filter="negative",
            feature_filter=feature
        )
        
        return {
            "feature": feature,
            "summary": response["answer"],
            "positive_examples": positive_reviews[:3],
            "negative_examples": negative_reviews[:3],
            "all_sources": response["sources"]
        }
    
    def compare_models(self, model1: str, model2: str) -> Dict:
        """
        Compare two product models.
        
        Args:
            model1: First model name
            model2: Second model name
        
        Returns:
            Comparison insights
        """
        question = f"Compare {model1} and {model2} based on user reviews. What are the key differences in features, sentiment, and user satisfaction?"
        
        response = self.query(question, k=15)
        
        return {
            "models": [model1, model2],
            "comparison": response["answer"],
            "sources": response["sources"]
        }


def main():
    """Example usage of RAG query engine."""
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize
        engine = RAGQueryEngine()
        
        # Example queries
        queries = [
            "What are the main complaints about sound quality?",
            "Which features receive the most positive feedback?",
            "What do users say about battery life?",
        ]
        
        for query in queries:
            print("\n" + "=" * 70)
            print(f"Question: {query}")
            print("=" * 70)
            
            result = engine.query(query)
            print(f"\nAnswer: {result['answer']}")
            print(f"\nSources ({len(result['sources'])}):")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"\n{i}. {source['metadata'].get('evidence', 'N/A')}")
                print(f"   Feature: {source['metadata'].get('feature', 'N/A')}")
                print(f"   Sentiment: {source['metadata'].get('sentiment', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
