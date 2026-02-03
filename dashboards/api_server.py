"""
FastAPI server for dashboard API endpoints.
Provides REST API for frontend dashboard and RAG queries.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import numpy as np
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from analytics import SentimentAnalyzer
from rag.retrieval_chain import RAGQueryEngine
from rag.vector_store import VectorStoreManager
from dashboards.json_encoder import convert_numpy_types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Redmi Sentiment Analysis API",
    description="API for sentiment analysis dashboard and RAG queries",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
analyzer = None
rag_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global analyzer, rag_engine
    
    try:
        analyzer = SentimentAnalyzer()
        logger.info("✅ Analytics initialized")
        
        # Initialize RAG engine (may fail if vector store not populated)
        try:
            rag_engine = RAGQueryEngine()
            logger.info("✅ RAG engine initialized")
        except Exception as e:
            logger.warning(f"⚠️ RAG engine not available: {e}")
            rag_engine = None
            
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")


# Request/Response models
class RAGQueryRequest(BaseModel):
    question: str
    k: int = 5
    filters: Optional[Dict] = None


class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]


# Analytics endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "analytics": analyzer is not None,
        "rag": rag_engine is not None
    }


@app.get("/api/overall-sentiment")
async def get_overall_sentiment():
    """Get overall sentiment statistics."""
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analytics not initialized")
    
    result = analyzer.get_overall_sentiment_score()
    return convert_numpy_types(result)


@app.get("/api/feature-sentiments")
async def get_feature_sentiments():
    """Get sentiment breakdown by feature."""
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analytics not initialized")
    
    result = analyzer.get_feature_sentiments()
    return convert_numpy_types(result)


@app.get("/api/model-sentiments")
async def get_model_sentiments():
    """Get sentiment breakdown by model."""
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analytics not initialized")
    
    result = analyzer.get_model_sentiments()
    return convert_numpy_types(result)


@app.get("/api/top-features")
async def get_top_features(n: int = Query(10, ge=1, le=50)):
    """Get top mentioned features."""
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analytics not initialized")
    
    result = analyzer.get_top_features(n=n)
    return convert_numpy_types(result)


@app.get("/api/feature-insights/{feature}")
async def get_feature_insights(feature: str):
    """Get detailed insights for a specific feature."""
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analytics not initialized")
    
    # Get top comments
    positive_comments = analyzer.get_top_comments_by_feature(feature, "positive", n=5)
    negative_comments = analyzer.get_top_comments_by_feature(feature, "negative", n=5)
    
    feature_sentiments = analyzer.get_feature_sentiments()
    feature_stats = feature_sentiments.get(feature, {})
    
    result = {
        "feature": feature,
        "statistics": feature_stats,
        "positive_examples": positive_comments,
        "negative_examples": negative_comments
    }
    return convert_numpy_types(result)


# RAG endpoints
@app.post("/api/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """Query the RAG system."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not available. Please populate vector store first.")
    
    try:
        result = rag_engine.query(
            question=request.question,
            k=request.k,
            filters=request.filters
        )
        return RAGQueryResponse(**result)
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/search")
async def rag_search(
    query: str = Query(..., description="Search query"),
    k: int = Query(5, ge=1, le=20),
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    feature: Optional[str] = Query(None),
    model: Optional[str] = Query(None)
):
    """Search for similar reviews."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not available")
    
    try:
        results = rag_engine.search_similar_reviews(
            query=query,
            k=k,
            sentiment_filter=sentiment,
            feature_filter=feature,
            model_filter=model
        )
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/feature-insights/{feature}")
async def rag_feature_insights(feature: str):
    """Get RAG-powered insights for a feature."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not available")
    
    try:
        insights = rag_engine.get_feature_insights(feature)
        return insights
    except Exception as e:
        logger.error(f"RAG feature insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/compare-models")
async def compare_models(
    model1: str = Query(..., description="First model to compare"),
    model2: str = Query(..., description="Second model to compare")
):
    """Compare two product models using RAG."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not available")
    
    try:
        comparison = rag_engine.compare_models(model1, model2)
        return comparison
    except Exception as e:
        logger.error(f"Model comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
