# 🚀 Groq API Integration Guide

## Overview

This project now uses **Groq** for fast LLM inference! Groq provides ultra-fast inference using OpenAI-compatible models like Llama 3.1, Mixtral, and more.

## ✅ What's Configured

- **Groq API Key**: Already configured in `config.py`
- **Model**: Llama 3.1 70B Versatile (default)
- **Base URL**: https://api.groq.com/openai/v1
- **Usage**: Sentiment analysis, topic extraction, and RAG insights

## 🔑 API Key Security

The Groq API key is stored in `config.py`. For production use, consider:

1. **Environment Variable** (Recommended):
   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY="your_key_here"
   
   # Linux/Mac
   export GROQ_API_KEY="your_key_here"
   ```

2. **Or update config.py**:
   ```python
   GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_key_here")
   ```

## 🎯 Available Groq Models

You can change the model in `config.py`:

```python
# Fast and versatile (default)
LLM_MODEL = "llama-3.1-70b-versatile"

# Other options:
# LLM_MODEL = "mixtral-8x7b-32768"  # Mixtral 8x7B
# LLM_MODEL = "gemma-7b-it"         # Gemma 7B
```

## 🚀 Benefits of Groq

1. **Ultra-Fast**: ~3-5x faster than standard OpenAI API
2. **Cost-Effective**: Lower costs compared to OpenAI
3. **Open Source Models**: Llama, Mixtral, Gemma
4. **OpenAI Compatible**: Same API interface

## 🔄 Switching Between Groq and OpenAI

In `config.py`:

```python
# Use Groq (default, faster)
USE_GROQ = True

# Use OpenAI instead
USE_GROQ = False
```

The system will automatically:
- ✅ Prioritize Groq if `USE_GROQ = True`
- ✅ Fall back to OpenAI if Groq unavailable
- ✅ Fall back to TextBlob if no API keys

## 📊 Current Configuration

```python
# config.py
GROQ_API_KEY = "gsk_nmUqXxxxxxxxxxxxxxxxxxx"
USE_GROQ = True
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
LLM_MODEL = "openai/gpt-oss-120b"
```

## 🔒 Security Note

⚠️ **Important**: The API key is stored in `config.py`. For version control:

1. Add to `.gitignore` if you modify it
2. Use environment variables in production
3. Don't share the key publicly

## 🧪 Testing

Run the pipeline to test Groq integration:

```bash
python quick_start.py
```

You should see:
```
✅ Using Groq API for fast inference
```

## 📝 Notes

- **Embeddings**: Groq doesn't support embeddings, so we use:
  - OpenAI embeddings (if OpenAI key available)
  - sentence-transformers (free, local fallback)
  
- **Rate Limits**: Groq has generous rate limits, minimal delays needed

## 🔗 Resources

- Groq Documentation: https://console.groq.com/docs
- Available Models: https://console.groq.com/docs/models
- OpenAI Compatibility: Uses same `openai` Python package

---

**Ready to use!** The project is now configured with Groq for fast inference. 🚀
