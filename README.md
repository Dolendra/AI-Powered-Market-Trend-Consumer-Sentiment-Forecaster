# AI-Powered-Market-Trend-Consumer-Sentiment-Forecaster

# 🚀 AI Consumer Intelligence Platform

**Complete End-to-End Project for Infosys**

A comprehensive AI-powered system for analyzing consumer opinions from multiple sources, providing sentiment insights, topic modeling, and contextual explanations using RAG (Retrieval-Augmented Generation).

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Modules Explained](#modules-explained)
9. [RAG Pipeline](#rag-pipeline)
10. [Dashboard](#dashboard)
11. [Reports & Alerts](#reports--alerts)

---

## 🎯 Overview

This platform transforms unstructured consumer text from various sources (social media, reviews, news) into actionable business intelligence:

- **Sentiment Analysis**: Understand how consumers feel
- **Topic Modeling**: Identify what consumers talk about
- **Trend Analytics**: Track sentiment changes over time
- **RAG Insights**: Get contextual explanations (not just numbers)
- **Automated Alerts**: Get notified of critical changes
- **Visual Dashboard**: Interactive analytics interface

---

## ✨ Features

### 1. **Multi-Source Data Collection**
- ✅ Amazon product reviews
- ✅ Flipkart reviews (new!)
- ✅ Reddit posts/comments
- ✅ Twitter/X tweets
- ✅ News articles (via News API)

### 1a. **Scalable Mobile Review Scraper** (NEW!)
- ✅ Discover all mobile brands and models from GSMArena
- ✅ Multi-platform review scraping (Amazon, Flipkart, etc.)
- ✅ Parallel processing with worker threads
- ✅ Queue-based architecture for scalability
- ✅ Model-wise analytics and monitoring

### 2. **Advanced Data Processing**
- Text cleaning (emojis, URLs, HTML)
- Stopword removal
- Keyword extraction
- Normalization

### 3. **LLM-Powered Analysis**
- GPT-based sentiment analysis
- Topic extraction
- Vector embeddings for semantic search

### 4. **RAG (Retrieval-Augmented Generation)**
- Semantic search over reviews
- Contextual insights generation
- "Why" explanations, not just metrics

### 5. **Trend Analytics**
- Sentiment trends over time
- KPI calculation
- Anomaly detection

### 6. **Interactive Dashboard**
- Real-time analytics
- Visual charts and graphs
- RAG-powered Q&A
- Export reports

### 7. **Alert System**
- Sentiment drop detection
- Email notifications
- Excel/PDF reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────────┐   │
│  │ Amazon  │  │ Reddit  │  │ Twitter │  │ News API   │   │
│  └─────────┘  └─────────┘  └─────────┘  └────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Data Collection & Ingestion                     │
│         (data_collectors.py)                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│          Data Cleaning & Preprocessing                       │
│         (preprocessing.py)                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Storage Layer                                   │
│  ┌──────────────┐              ┌──────────────┐           │
│  │  SQLite DB   │              │  ChromaDB    │           │
│  │ (Structured) │              │  (Vectors)   │           │
│  └──────────────┘              └──────────────┘           │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│          LLM Sentiment & Topic Modeling                      │
│         (llm_integration.py)                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  RAG Pipeline                                │
│         (rag_pipeline.py)                                    │
│  • Retrieval: Find similar reviews                           │
│  • Generation: Explain insights with context                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Trend Analytics Engine                          │
│         (trend_analytics.py)                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│           Dashboard & Alert System                           │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ Streamlit UI     │          │  Alert System    │        │
│  └──────────────────┘          └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### 1. Clone/Download the Project

```bash
cd "D:\Infosys project"
```

### 2. Create Virtual Environment (if not already created)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## ⚙️ Configuration

### 1. Set API Keys (Optional but Recommended)

Create a `.env` file or set environment variables:

```bash
# OpenAI API (for LLM features)
OPENAI_API_KEY=your_openai_api_key_here

# Reddit API (optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Twitter API (optional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# News API (optional)
NEWS_API_KEY=your_news_api_key

# Email Alerts (optional)
ALERT_EMAIL=your_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
```

**Note**: 
- ✅ **Groq API Key**: Already configured in `.env` file!
- ⚠️ The system works without other API keys but with reduced functionality:
  - Without Reddit/Twitter: Uses mock data for demo
  - Without News API: Uses mock news data
  - Without OpenAI: Uses Groq (already configured) or TextBlob fallback

---

## 🚀 Usage

### Option 1: Run Full Pipeline (Recommended)

```bash
python main.py --product "iPhone 15" --max-per-source 50
```

This runs the complete end-to-end pipeline:
1. Data collection from all sources
2. Data cleaning
3. Sentiment analysis
4. Topic extraction
5. RAG indexing
6. Trend calculation
7. Alert generation

### Option 2: Run Individual Steps

```python
# Data collection only
from data_collectors import DataCollector
collector = DataCollector()
data = collector.collect_all_sources("iPhone 15", max_per_source=50)

# Cleaning only
from preprocessing import BatchPreprocessor
preprocessor = BatchPreprocessor()
cleaned = preprocessor.process_dataframe(df)

# Sentiment analysis only
from llm_integration import LLMSentimentAnalyzer
analyzer = LLMSentimentAnalyzer()
result = analyzer.analyze_sentiment_llm("Great product!")
```

### Option 3: Launch Dashboard

```bash
streamlit run dashboard.py
```

This opens an interactive dashboard where you can:
- View KPIs and trends
- Query RAG insights
- Generate reports
- Check alerts

---

## 📁 Project Structure

```
Infosys project/
│
├── config.py                 # Configuration settings
├── database.py               # SQLite database layer
├── data_collectors.py        # Multi-source data collection
├── preprocessing.py          # Text cleaning & preprocessing
├── llm_integration.py        # LLM sentiment & topic extraction
├── rag_pipeline.py          # RAG implementation
├── trend_analytics.py       # Trend analysis & KPIs
├── alert_system.py          # Alerts & reporting
├── dashboard.py             # Streamlit dashboard
├── main.py                  # Main orchestration script
│
├── data/                    # Data directories (auto-created)
│   ├── raw/                 # Raw collected data
│   └── processed/           # Processed data
│
├── models/                  # Saved models (if any)
├── reports/                 # Generated reports
├── vector_db/              # ChromaDB vector database
│
├── consumer_intelligence.db  # SQLite database
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🧩 Modules Explained

### 1. **Data Collection Layer** (`data_collectors.py`)

Collects data from multiple sources:
- **AmazonCollector**: Scrapes Amazon product reviews
- **RedditCollector**: Fetches Reddit posts (requires API)
- **TwitterCollector**: Collects tweets (requires API)
- **NewsCollector**: Gets news articles (requires API)

### 2. **Preprocessing** (`preprocessing.py`)

Cleans and normalizes text:
- Removes URLs, HTML, emojis
- Normalizes whitespace
- Extracts keywords
- Removes stopwords (optional)

### 3. **LLM Integration** (`llm_integration.py`)

AI-powered analysis:
- **LLMSentimentAnalyzer**: GPT-based sentiment (falls back to TextBlob)
- **LLMTopicExtractor**: Extracts topics from text
- **EmbeddingGenerator**: Creates vector embeddings

### 4. **RAG Pipeline** (`rag_pipeline.py`)

Retrieval-Augmented Generation:
- Stores embeddings in ChromaDB
- Retrieves similar reviews
- Generates contextual insights using LLM

### 5. **Trend Analytics** (`trend_analytics.py`)

Business intelligence:
- Calculates KPIs (Customer Satisfaction, Sentiment Rates)
- Detects sentiment drops
- Analyzes topic trends
- Generates insights

### 6. **Alert System** (`alert_system.py`)

Notifications and reports:
- Detects alert conditions
- Generates Excel/PDF reports
- Sends email alerts (optional)

### 7. **Dashboard** (`dashboard.py`)

Interactive Streamlit UI:
- Overview metrics
- RAG-powered Q&A
- Trend visualizations
- Report generation

---

## 🔍 RAG Pipeline Explained

**RAG = Retrieval-Augmented Generation**

Instead of just saying "Sentiment dropped by 23%", RAG explains WHY:

1. **Query**: "Why is sentiment decreasing for iPhone 15?"
2. **Retrieval**: System finds similar negative reviews about battery issues
3. **Generation**: LLM combines retrieved reviews with context:
   > "Sentiment dropped because users complain about battery drain after the latest update. Multiple reviews mention the phone dies quickly and charging is slow."

### How It Works:

```python
from rag_pipeline import RAGPipeline

rag = RAGPipeline()

# Add documents to vector DB
rag.add_documents(texts=["review 1", "review 2"], metadatas=[...])

# Generate insight
insight = rag.generate_insight(
    "Why is sentiment changing?",
    product_name="iPhone 15"
)

print(insight['insight'])  # Contextual explanation
```

---

## 📊 Dashboard Features

### Tab 1: Overview
- KPIs (Customer Satisfaction, Total Reviews)
- Sentiment distribution pie chart
- Top topics bar chart

### Tab 2: RAG Insights
- Ask questions about consumer sentiment
- Get AI-generated contextual explanations
- View supporting evidence

### Tab 3: Trends
- Sentiment trend line chart
- Positive/negative review counts
- Review volume over time

### Tab 4: Alerts
- View active alerts
- Check for new alerts
- Alert severity indicators

### Tab 5: Reports
- Generate Excel reports
- Generate PDF reports
- Download reports

---

## 📧 Reports & Alerts

### Generate Reports

**Via Dashboard:**
1. Go to "Reports" tab
2. Click "Generate Excel Report" or "Generate PDF Report"
3. Download the report

**Via Code:**
```python
from alert_system import AlertSystem

alerts = AlertSystem()
alerts.generate_excel_report("report.xlsx", product_name="iPhone 15")
alerts.generate_pdf_report("report.pdf", product_name="iPhone 15")
```

### Alert Conditions

- Sentiment drop > 20%
- Negative sentiment rate > 30%
- High review volume with negative trend

---

## 🎓 Key Concepts for Presentation

### 1. **End-to-End Pipeline**
- Data collection → Cleaning → Analysis → Insights → Dashboard

### 2. **RAG (Most Important)**
- Not just numbers, but explanations
- "Why" insights, not just "what"

### 3. **Multi-Source Integration**
- Amazon, Reddit, Twitter, News
- Unified processing pipeline

### 4. **LLM Integration**
- GPT for advanced sentiment
- Embeddings for semantic search

### 5. **Business Intelligence**
- KPIs, trends, alerts
- Actionable insights

---

## 🐛 Troubleshooting

### Issue: "No module named 'openai'"
**Solution**: `pip install openai`

### Issue: "ChromaDB connection error"
**Solution**: Check `vector_db/` directory permissions

### Issue: "Amazon blocking scraper"
**Solution**: 
- Use proxies
- Increase delays in `config.py`
- Use Amazon Product API instead

### Issue: "OpenAI API rate limit"
**Solution**: 
- Use fallback mode (TextBlob)
- Reduce batch sizes
- Add delays

---

## 📝 Next Steps / Enhancements

- [ ] Add more data sources (Facebook, Instagram)
- [ ] Implement real-time streaming
- [ ] Add multi-language support
- [ ] Implement advanced topic modeling (BERTopic)
- [ ] Add competitor comparison
- [ ] Implement A/B testing for models
- [ ] Add user authentication
- [ ] Deploy to cloud (AWS/GCP)

---

## 📄 License

This project is created for Infosys educational purposes.

---

## 👥 Author

Built for Infosys Project - AI Consumer Intelligence Platform

---

## 🎯 Summary

This is a **complete, production-ready** end-to-end project that demonstrates:

✅ Multi-source data collection  
✅ Advanced NLP preprocessing  
✅ LLM-powered sentiment analysis  
✅ RAG for contextual insights  
✅ Trend analytics & KPIs  
✅ Interactive dashboard  
✅ Automated alerts & reports  

**Ready to present and demonstrate!** 🚀
