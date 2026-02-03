# Step-by-Step Setup Commands

## 🚀 Complete Setup Guide

### Step 1: Install Python Dependencies

```bash
# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:** All packages installed successfully

---

### Step 2: Configure API Keys

```bash
# Open .env file (create if it doesn't exist)
notepad .env
```

**Add these lines to `.env` file:**
```env
# Existing keys (if you have them)
YOUTUBE_API_KEY=your_youtube_key_here
GROQ_API_KEY=your_groq_key_here

# New RAG key (required)
PINECONE_API_KEY=your_pinecone_key_here
```

**Get Pinecone API key:**
1. Visit: https://www.pinecone.io/
2. Sign up / Login
3. Go to API Keys section
4. Copy your API key

---

### Step 3: Set Up RAG Pipeline

```bash
# Run setup script
python setup_rag.py
```

**What this does:**
- ✅ Checks all dependencies
- ✅ Verifies data file exists
- ✅ Checks Pinecone configuration
- ✅ Populates vector store (if you choose 'y')

**Expected output:**
```
✅ All dependencies installed!
✅ Data file found
✅ PINECONE_API_KEY configured
✅ Vector store populated successfully!
```

---

### Step 4: Choose Your Dashboard

#### Option A: Plotly Dashboard (Python - Quick Start)

```bash
# Generate and open Plotly dashboard
python -m dashboards.plotly_dashboard
```

**What happens:**
- Creates HTML dashboard file
- Opens in your default browser
- Interactive charts ready to use

**Output location:** `data/dashboards/sentiment_dashboard.html`

---

#### Option B: React Dashboard (Web App - Full Featured)

**Terminal 1 - Start API Server:**
```bash
# Start FastAPI server
python dashboards/api_server.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Start React Frontend:**
```bash
# Navigate to frontend directory
cd dashboards/frontend

# Install Node.js dependencies (first time only)
npm install

# Start React development server
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view redmi-sentiment-dashboard in the browser.
  Local:            http://localhost:3000
```

**Access dashboard:** Open browser to `http://localhost:3000`

---

## 📋 Quick Command Reference

### RAG Operations

```bash
# Test RAG queries (example usage)
python rag/query_example.py

# Populate vector store manually
python -m rag.vector_store

# Test retrieval chain
python -m rag.retrieval_chain
```

### Dashboard Operations

```bash
# Generate Plotly dashboard
python -m dashboards.plotly_dashboard

# Start API server only
python dashboards/api_server.py

# Build React app for production
cd dashboards/frontend
npm run build
```

### Analytics

```bash
# Generate analytics report
python analytics.py

# Run full pipeline (if needed)
python main.py
```

---

## 🔍 Verification Commands

### Check Installation

```bash
# Check Python packages
pip list | findstr "langchain pinecone plotly fastapi"

# Check if data file exists
dir data\processed\feature_sentiment_cleaned.csv

# Check API server health
curl http://localhost:8000/api/health
```

### Test RAG System

```python
# Open Python and test
python

>>> from rag.retrieval_chain import RAGQueryEngine
>>> engine = RAGQueryEngine()
>>> result = engine.query("What are main complaints?")
>>> print(result["answer"])
```

---

## 🛠️ Troubleshooting Commands

### If Dependencies Fail

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install in stages
pip install pandas numpy python-dotenv
pip install langchain langchain-community
pip install pinecone-client sentence-transformers
pip install plotly fastapi uvicorn kaleido
```

### If Vector Store Not Populated

```bash
# Check Pinecone key
python -c "from config import PINECONE_API_KEY; print('Key set' if PINECONE_API_KEY else 'Key missing')"

# Re-populate vector store
python -m rag.vector_store
```

### If React App Fails

```bash
# Clear npm cache
cd dashboards/frontend
rm -rf node_modules
rm package-lock.json
npm install

# Check if API server is running
curl http://localhost:8000/api/health
```

---

## 📊 Complete Workflow Example

```bash
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env file
notepad .env
# (Add PINECONE_API_KEY)

# 4. Set up RAG
python setup_rag.py

# 5. Start API server (Terminal 1)
python dashboards/api_server.py

# 6. Start React app (Terminal 2)
cd dashboards/frontend
npm install
npm start

# 7. Open browser
# Navigate to: http://localhost:3000
```

---

## 🎯 Common Use Cases

### Generate Dashboard Report

```bash
python -m dashboards.plotly_dashboard
# Opens HTML file automatically
```

### Query RAG System

```bash
python rag/query_example.py
```

### Start Full Stack (API + Frontend)

**Terminal 1:**
```bash
python dashboards/api_server.py
```

**Terminal 2:**
```bash
cd dashboards/frontend && npm start
```

---

## 📝 Notes

- **First time setup:** Takes 5-10 minutes (includes model downloads)
- **Vector store population:** Takes 2-5 minutes for 1000+ reviews
- **API server:** Runs on port 8000 by default
- **React app:** Runs on port 3000 by default
- **Pinecone free tier:** Supports up to 100K vectors

---

**Ready to go!** 🎉
