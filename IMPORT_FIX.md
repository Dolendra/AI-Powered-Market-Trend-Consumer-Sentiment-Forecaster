# Import Fix for LangChain 0.2.0+

## ✅ Issue Fixed

**Error:** `cannot import name 'Groq' from 'langchain.llms'`

**Cause:** LangChain 0.2.0+ deprecated and removed LLMs from `langchain.llms`. All LLMs must now be imported from `langchain_community.llms`.

## 🔧 Fix Applied

**File:** `rag/retrieval_chain.py`

**Before (Broken):**
```python
try:
    from langchain_community.llms import Groq
except ImportError:
    from langchain.llms import Groq  # ❌ Doesn't work in 0.2.0+
```

**After (Fixed):**
```python
# MUST use langchain_community for LangChain 0.2.0+
from langchain_community.llms import Groq
```

## ✅ Verification

After the fix, test with:

```bash
python -c "from rag.retrieval_chain import RAGQueryEngine; print('✅ Import OK')"
```

Or run setup again:

```bash
python setup_rag.py
```

## 📝 Note

If you still get import errors, ensure `langchain-community` is installed:

```bash
pip install langchain-community>=0.2.0
```

---

**Status:** ✅ Fixed
**Compatibility:** LangChain 0.2.0+
