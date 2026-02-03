# RAG & Dashboard Implementation Guide

## Milestone 3: RAG & Dashboards - Complete Implementation

This guide covers the complete implementation of Retrieval-Augmented Generation (RAG) pipelines using LangChain + Pinecone and interactive dashboards with Plotly/React.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Setup & Installation](#setup--installation)
3. [RAG Pipeline](#rag-pipeline)
4. [Plotly Dashboard](#plotly-dashboard)
5. [React Dashboard](#react-dashboard)
6. [API Server](#api-server)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What's Been Implemented

1. **RAG Pipeline** (`rag/`)
   - Vector store management with Pinecone
   - LangChain retrieval chains
   - Semantic search over reviews
   - Question-answering system

2. **Plotly Dashboard** (`dashboards/plotly_dashboard.py`)
   - Interactive Python-based visualizations
   - Comprehensive sentiment charts
   - Export to HTML/PNG/PDF

3. **React Dashboard** (`dashboards/frontend/`)
   - Modern web interface
   - Real-time data visualization
   - RAG query interface
   - Material-UI components

4. **API Server** (`dashboards/api_server.py`)
   - FastAPI REST endpoints
   - Analytics data API
   - RAG query endpoints
   - CORS-enabled for frontend

---

## 🚀 Setup & Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies added:**
- `langchain` & `langchain-community` - RAG framework
- `pinecone-client` - Vector database
- `sentence-transformers` - Embeddings
- `plotly` - Interactive visualizations
- `fastapi` & `uvicorn` - API server
- `kaleido` - Static image export

### 2. Set Up Pinecone

1. **Create Pinecone account**: https://www.pinecone.io/
2. **Get API key** from Pinecone dashboard
3. **Add to `.env` file**:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=redmi-sentiment-reviews
   ```

### 3. Install Node.js Dependencies (for React Dashboard)

```bash
cd dashboards/frontend
npm install
```

---

## 🔍 RAG Pipeline

### Architecture

```
feature_sentiment_cleaned.csv
    ↓
VectorStoreManager
    ↓ (embeddings)
Pinecone Vector Database
    ↓
LangChain Retriever
    ↓
RAGQueryEngine (Groq LLM)
    ↓
Answer + Sources
```

### Step 1: Populate Vector Store

```python
from rag.vector_store import VectorStoreManager

# Initialize manager
manager = VectorStoreManager()

# Populate with your data
manager.populate_vector_store()
```

**Or use command line:**
```bash
python -m rag.vector_store
```

This will:
- Load `feature_sentiment_cleaned.csv`
- Generate embeddings for each review
- Upload to Pinecone index
- Create searchable vector store

### Step 2: Query the RAG System

```python
from rag.retrieval_chain import RAGQueryEngine

# Initialize engine
engine = RAGQueryEngine()

# Ask questions
result = engine.query("What are the main complaints about sound quality?")
print(result["answer"])
print(f"Sources: {len(result['sources'])} documents")
```

### Example Queries

```python
# General question
result = engine.query("What do users say about battery life?")

# Filtered search
results = engine.search_similar_reviews(
    query="positive feedback about ANC",
    k=10,
    sentiment_filter="positive",
    feature_filter="anc"
)

# Feature insights
insights = engine.get_feature_insights("sound_quality")

# Model comparison
comparison = engine.compare_models("Redmi Buds 3 Pro", "Redmi Buds 4 Pro")
```

---

## 📊 Plotly Dashboard

### Generate Dashboard

```python
from dashboards.plotly_dashboard import SentimentDashboard

# Initialize
dashboard = SentimentDashboard()

# Save as HTML (opens in browser)
dashboard.save_dashboard(format="html")

# Or display directly
dashboard.show_dashboard()
```

### Available Visualizations

1. **Sentiment Distribution** - Pie chart of overall sentiment
2. **Feature Sentiment Scores** - Bar chart by feature
3. **Feature Sentiment Heatmap** - Heatmap showing sentiment % by feature
4. **Model Comparison** - Stacked bar chart across models
5. **Top Features** - Horizontal bar chart of most mentioned features
6. **Sentiment Timeline** - Time series (if date data available)

### Export Formats

```python
# HTML (interactive)
dashboard.save_dashboard(format="html")

# PNG (static image)
dashboard.save_dashboard(format="png")

# PDF
dashboard.save_dashboard(format="pdf")

# JSON (for custom processing)
dashboard.save_dashboard(format="json")
```

### Individual Charts

```python
# Get specific chart
fig = dashboard.create_sentiment_distribution_chart()
fig.show()

fig = dashboard.create_feature_sentiment_scores()
fig.show()
```

---

## ⚛️ React Dashboard

### Start Development Server

```bash
# Terminal 1: Start API server
python dashboards/api_server.py

# Terminal 2: Start React app
cd dashboards/frontend
npm start
```

The dashboard will open at `http://localhost:3000`

### Features

1. **Overview Tab**
   - Overall sentiment pie chart
   - Feature sentiment scores
   - Model comparison
   - Top features chart

2. **RAG Query Tab**
   - Natural language query interface
   - AI-powered answers
   - Source document display
   - Filter by sentiment/feature/model

### Customization

Edit `dashboards/frontend/src/App.js` to:
- Add new visualizations
- Modify chart layouts
- Add new API endpoints
- Customize UI components

---

## 🌐 API Server

### Start Server

```bash
python dashboards/api_server.py
```

Server runs on `http://localhost:8000`

### API Endpoints

#### Analytics Endpoints

- `GET /api/health` - Health check
- `GET /api/overall-sentiment` - Overall sentiment stats
- `GET /api/feature-sentiments` - Sentiment by feature
- `GET /api/model-sentiments` - Sentiment by model
- `GET /api/top-features?n=10` - Top mentioned features
- `GET /api/feature-insights/{feature}` - Detailed feature insights

#### RAG Endpoints

- `POST /api/rag/query` - Query RAG system
  ```json
  {
    "question": "What are main complaints?",
    "k": 5,
    "filters": {"sentiment": "negative"}
  }
  ```

- `GET /api/rag/search` - Semantic search
  ```
  /api/rag/search?query=sound quality&k=10&sentiment=positive
  ```

- `GET /api/rag/feature-insights/{feature}` - Feature insights
- `GET /api/rag/compare-models?model1=X&model2=Y` - Model comparison

### API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI

---

## 💡 Usage Examples

### Example 1: Complete RAG Workflow

```python
# 1. Populate vector store (one-time setup)
from rag.vector_store import VectorStoreManager
manager = VectorStoreManager()
manager.populate_vector_store()

# 2. Query system
from rag.retrieval_chain import RAGQueryEngine
engine = RAGQueryEngine()

# 3. Get insights
result = engine.query("What are users' main concerns about connectivity?")
print(result["answer"])

# 4. Find specific examples
reviews = engine.search_similar_reviews(
    "connectivity issues",
    k=5,
    sentiment_filter="negative"
)
for review in reviews:
    print(f"- {review['metadata']['evidence']}")
```

### Example 2: Generate Dashboard Report

```python
from dashboards.plotly_dashboard import SentimentDashboard

dashboard = SentimentDashboard()

# Generate comprehensive dashboard
dashboard.save_dashboard(
    output_path="reports/sentiment_dashboard.html",
    format="html"
)

# Generate individual charts
fig = dashboard.create_feature_sentiment_heatmap()
fig.write_html("reports/heatmap.html")
```

### Example 3: API Integration

```python
import requests

# Query API
response = requests.get("http://localhost:8000/api/overall-sentiment")
data = response.json()
print(f"Sentiment Score: {data['sentiment_score']}")

# RAG query
response = requests.post(
    "http://localhost:8000/api/rag/query",
    json={"question": "What do users like about battery?"}
)
result = response.json()
print(result["answer"])
```

---

## 🔧 Configuration

### Environment Variables

Add to `.env`:

```env
# Existing
YOUTUBE_API_KEY=...
GROQ_API_KEY=...

# New for RAG
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=redmi-sentiment-reviews
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_TOP_K=5

# Dashboard
DASHBOARD_PORT=8000
DASHBOARD_HOST=0.0.0.0
```

### Config File

Settings in `config.py`:
- `PINECONE_INDEX_NAME` - Pinecone index name
- `EMBEDDING_MODEL` - HuggingFace model for embeddings
- `RAG_TOP_K` - Default number of retrieved documents
- `DASHBOARD_PORT` - API server port

---

## 🐛 Troubleshooting

### Issue: Pinecone API Key Error

**Error**: `PINECONE_API_KEY not set`

**Solution**:
1. Get API key from Pinecone dashboard
2. Add to `.env` file
3. Restart Python process

### Issue: Vector Store Not Populated

**Error**: `RAG engine not available`

**Solution**:
```python
from rag.vector_store import VectorStoreManager
manager = VectorStoreManager()
manager.populate_vector_store()
```

### Issue: LangChain Import Errors

**Error**: `ModuleNotFoundError: No module named 'langchain_community'`

**Solution**:
```bash
pip install langchain-community
```

### Issue: React App Can't Connect to API

**Error**: CORS or connection refused

**Solution**:
1. Ensure API server is running: `python dashboards/api_server.py`
2. Check `API_BASE` in `App.js` matches server URL
3. Verify CORS settings in `api_server.py`

### Issue: Embedding Model Download

**Error**: Model download fails

**Solution**:
- First run downloads model (~80MB)
- Ensure internet connection
- Model cached after first download

### Issue: Pinecone Index Already Exists

**Warning**: Index already contains vectors

**Solution**:
- Option 1: Use existing index (recommended)
- Option 2: Delete and recreate:
  ```python
  manager = VectorStoreManager()
  manager.delete_index()
  manager.populate_vector_store()
  ```

---

## 📈 Performance Tips

1. **Batch Processing**: Vector store uploads in batches of 100
2. **Caching**: Embeddings are cached after first generation
3. **Index Size**: Pinecone free tier supports 100K vectors
4. **Query Speed**: Typical RAG query: 1-3 seconds
5. **Dashboard Load**: React dashboard loads data on mount

---

## 🎯 Next Steps

1. **Customize Embeddings**: Try different models (e.g., `all-mpnet-base-v2`)
2. **Add Filters**: Implement date range, model filters in UI
3. **Export Reports**: Add PDF export for dashboards
4. **Real-time Updates**: WebSocket for live data updates
5. **Advanced RAG**: Add re-ranking, multi-query retrieval

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [React Plotly.js](https://plotly.com/javascript/react/)

---

## ✅ Checklist

- [x] RAG pipeline with LangChain + Pinecone
- [x] Vector store population
- [x] Query interface
- [x] Plotly dashboard
- [x] React frontend
- [x] FastAPI server
- [x] Documentation
- [x] Error handling
- [x] Configuration management

---

**Status**: ✅ Complete | **Version**: 1.0.0 | **Last Updated**: January 2026
