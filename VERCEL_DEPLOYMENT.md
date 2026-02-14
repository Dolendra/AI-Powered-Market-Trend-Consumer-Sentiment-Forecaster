   # Vercel Deployment Guide for React + FastAPI

## Quick Deploy Steps

### 1. Deploy React Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project root
cd d:/Infosys project

# Login to Vercel
vercel login

# Deploy frontend
cd dashboards/frontend
vercel --prod
```

### 2. Deploy FastAPI Backend (Recommended: Render.com)

**Why Render.com?**
- Free tier available
- Native Python/FastAPI support
- Easy setup

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub repository
3. Create a "Web Service":
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables (API keys, etc.)
5. Deploy

**Required Backend Dependencies**

Your [`requirements.txt`](requirements.txt) now includes all required packages:

| Category | Packages |
|----------|----------|
| Core | pandas, numpy, python-dotenv, requests, tqdm, urllib3 |
| API Clients | google-api-python-client, groq, langdetect |
| RAG | langchain, langchain-community, langchain-pinecone, pinecone-client, sentence-transformers |
| Dashboard | plotly, fastapi, uvicorn, pydantic, kaleido |
| Alerts | yagmail, reportlab, openpyxl |

### 3. Update Frontend API URL

After backend deployment, update [`dashboards/frontend/src/App.js`](dashboards/frontend/src/App.js):

```javascript
// Replace localhost with your Render URL
const API_BASE_URL = process.env.REACT_APP_API_URL || "https://your-backend.onrender.com";
```

### 4. Environment Variables

Create `.env` file in `dashboards/frontend/`:
```
REACT_APP_API_URL=https://your-fastapi-backend.onrender.com
```

## Vercel + Backend Platform Architecture

```
┌─────────────────────────────────────┐
│           Vercel (Frontend)         │
│   dashboards/frontend (React App)   │
└─────────────────┬───────────────────┘
                  │ HTTPS
                  ▼
┌─────────────────────────────────────┐
│      Render.com (Backend)           │
│         FastAPI + Python            │
│   (uvicorn main:app --port $PORT)   │
└─────────────────────────────────────┘
```

## Alternative: Full Backend on Vercel (Limited)

Vercel supports Python Serverless Functions, but FastAPI has limitations:

**Create API endpoint:**
```python
# api/analysis.py
def handler(request):
    import sys
    sys.path.append('/var/task')
    from main import app
    return app(request)
```

**Note:** This approach has timeout limits (10s free tier) and may not support all FastAPI features.

## Recommended Production Setup

| Component | Platform | Cost |
|-----------|----------|------|
| React Frontend | Vercel | Free |
| FastAPI Backend | Render.com | Free |
| Database | Render PostgreSQL / Supabase | Free tier |
| API Keys | Environment variables | - |

## Deploy Commands Summary

```bash
# 1. Deploy backend to Render (via GitHub integration)
# URL will be like: https://your-app.onrender.com

# 2. Build and deploy frontend
cd dashboards/frontend
npm run build
vercel --prod

# 3. Set environment variables in Vercel dashboard
REACT_APP_API_URL=https://your-render-backend.onrender.com
```

## Verification

After deployment:
1. Frontend: `https://your-project.vercel.app`
2. Backend: `https://your-app.onrender.com/docs` (Swagger UI)
3. Test API calls from frontend to backend
