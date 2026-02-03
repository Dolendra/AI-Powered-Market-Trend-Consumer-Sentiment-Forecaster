"""
Configuration management for the Redmi sentiment analysis pipeline.
Loads settings from environment variables with sensible defaults.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
ENV_FILE = Path(__file__).parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    print("⚠️ WARNING: .env file not found. Using environment variables or defaults.")

# ============================================================
# PROXY CONFIGURATION (for corporate networks)
# ============================================================
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

# Apply proxy settings if configured
if HTTP_PROXY or HTTPS_PROXY:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if HTTP_PROXY:
        os.environ["HTTP_PROXY"] = HTTP_PROXY
    if HTTPS_PROXY:
        os.environ["HTTPS_PROXY"] = HTTPS_PROXY
    logger_temp = logging.getLogger("config")
    logger_temp.info(f"✅ Proxy configured: {HTTP_PROXY or HTTPS_PROXY}")

# ============================================================
# API CONFIGURATION
# ============================================================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY not set in .env or environment")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not set in .env or environment")

GROQ_MODEL = "openai/gpt-oss-120b"

# ============================================================
# PROCESSING CONFIGURATION
# ============================================================
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 20))
API_RATE_LIMIT = float(os.getenv("API_RATE_LIMIT", 0.5))  # seconds between calls
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 30))
MAX_RETRIES = 3

# ============================================================
# DATA COLLECTION CONFIGURATION
# ============================================================
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", 50))
MAX_COMMENTS_PER_VIDEO = int(os.getenv("MAX_COMMENTS_PER_VIDEO", 500))
MIN_COMMENT_LENGTH = int(os.getenv("MIN_COMMENT_LENGTH", 15))

# ============================================================
# FEATURE DEFINITIONS
# ============================================================
PRODUCT_MODELS = [
    "Redmi Buds 4 Pro review",
    "Redmi Buds 5 Pro review",
    "Redmi Earbuds S review",
]

PRODUCT_FEATURES = {
    "sound_quality",
    "bass",
    "mic_quality",
    "call_quality",
    "battery",
    "charging",
    "build_quality",
    "comfort",
    "fit",
    "connectivity",
    "latency",
    "anc",  # Active Noise Cancellation
    "price",
    "value_for_money",
    "design",
    "durability",
}

# ============================================================
# DATA PATHS
# ============================================================
DATA_DIR = Path(__file__).parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERMEDIATE_DATA_DIR = DATA_DIR / "intermediate"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_CSV_FILE = RAW_DATA_DIR / "Redmi_YouTube_Large_Final.csv"
CLEAN_STAGE_1_FILE = INTERMEDIATE_DATA_DIR / "clean_stage_1.csv"
FEATURE_SENTIMENT_FILE = PROCESSED_DATA_DIR / "feature_sentiment_cleaned.csv"
CHECKPOINT_FILE = INTERMEDIATE_DATA_DIR / "checkpoint.json"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, INTERMEDIATE_DATA_DIR, PROCESSED_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================
# RAG CONFIGURATION
# ============================================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "redmi-sentiment-reviews")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", 5))

# ============================================================
# DASHBOARD CONFIGURATION
# ============================================================
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8000))
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
FEATURE_SENTIMENT_CLEANED_FILE = PROCESSED_DATA_DIR / "feature_sentiment_cleaned.csv"

# ============================================================
# LOGGING CONFIGURATION
# ============================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path(__file__).parent / os.getenv("LOG_FILE", "pipeline.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

print(f"✅ Configuration loaded successfully")
print(f"   Workers: {MAX_WORKERS}, Batch Size: {BATCH_SIZE}, Rate Limit: {API_RATE_LIMIT}s")
