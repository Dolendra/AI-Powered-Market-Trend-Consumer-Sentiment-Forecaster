# Optimized Installation Guide

## 🚀 Fast Installation (Recommended)

### Step 1: Install Core Dependencies (Fast - ~1 minute)
```bash
pip install pandas==2.1.4 numpy python-dotenv requests tqdm
pip install google-api-python-client groq langdetect
```

### Step 2: Install RAG Dependencies (Medium - ~2-3 minutes)
```bash
pip install langchain>=0.2.0 langchain-community>=0.2.0
pip install pinecone-client>=3.0.0
```

### Step 3: Install Embeddings (Heavy - ~5 minutes, optional for now)
```bash
# Only install if you need RAG immediately
pip install sentence-transformers
```

### Step 4: Install Dashboard (Fast - ~1 minute)
```bash
pip install plotly fastapi "uvicorn[standard]"
```

**Total time: ~5-10 minutes** (vs 15-20 minutes with all at once)

---

## 📦 Alternative: Use Optimized Requirements

```bash
# Install from optimized file (skips heavy dependencies)
pip install -r requirements-optimized.txt

# Then add embeddings separately if needed
pip install sentence-transformers
```

---

## 🔧 Fix Common Issues

### Issue: LangChain Import Errors

**Solution:** Install compatible versions:
```bash
pip uninstall langchain langchain-community -y
pip install langchain==0.2.0 langchain-community==0.2.0
```

### Issue: Pinecone Connection Errors

**Solution:** Update Pinecone client:
```bash
pip install --upgrade pinecone-client
```

### Issue: Sentence Transformers Too Slow

**Solution:** Install without cache:
```bash
pip install --no-cache-dir sentence-transformers
```

Or use a lighter model in `config.py`:
```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight
```

---

## ✅ Verification

After installation, verify:

```bash
# Check Python packages
python -c "import langchain; print('LangChain:', langchain.__version__)"
python -c "import pinecone; print('Pinecone: OK')"
python -c "import plotly; print('Plotly:', plotly.__version__)"
```

---

## 🎯 Minimal Setup (Dashboard Only)

If you only need dashboards (no RAG):

```bash
pip install pandas numpy python-dotenv plotly fastapi uvicorn
```

Skip RAG setup in `setup_rag.py` when prompted.

---

## 📝 Notes

- **First install**: Takes longer due to model downloads
- **Subsequent installs**: Much faster (cached)
- **Embeddings**: Only needed for RAG, not for dashboards
- **Kaleido**: Only needed for PNG/PDF export
