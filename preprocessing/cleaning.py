"""
Optimized data cleaning pipeline with batch processing and language detection.
Removes non-English comments, handles encoding issues, and removes duplicates.
"""

import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import re
from langdetect import detect, LangDetectException
from tqdm import tqdm

# Import configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    RAW_CSV_FILE,
    CLEAN_STAGE_1_FILE,
    MIN_COMMENT_LENGTH,
    LOG_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def basic_clean(text):
    """
    Basic text cleaning: lowercase, remove URLs, special chars, extra spaces.
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|ftp\S+", "", text)  # Remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s\.\!\?\-']", " ", text)  # Keep only alphanumeric + punctuation
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace
    return text.strip()


def is_english_batch(texts, batch_size=100):
    """
    Batch language detection for efficiency.
    Optimized version using cached results and fallback strategies.
    
    Args:
        texts: List of text strings
        batch_size: Number of texts to process before yielding
        
    Yields:
        Boolean indicating if text is English
    """
    cache = {}
    
    for text in texts:
        # Skip empty texts
        if not text or len(text.strip()) < 3:
            yield False
            continue
        
        # Check cache first
        if text in cache:
            yield cache[text]
            continue
        
        try:
            is_eng = detect(text) == "en"
            cache[text] = is_eng
            yield is_eng
        except LangDetectException:
            # On language detection failure, use heuristic: check for common English words
            common_words = {"the", "is", "at", "good", "bad", "great", "like", "love", "hate"}
            text_lower = text.lower().split()
            is_eng = any(word in common_words for word in text_lower)
            cache[text] = is_eng
            yield is_eng
        except Exception as e:
            logger.warning(f"⚠️ Error detecting language for text: {e}")
            yield False


def main():
    """Main cleaning pipeline."""
    logger.info("=" * 70)
    logger.info("🧹 Starting Data Cleaning Pipeline")
    logger.info("=" * 70)
    
    # Load raw data
    logger.info(f"📂 Loading raw data from: {RAW_CSV_FILE}")
    try:
        df = pd.read_csv(RAW_CSV_FILE)
        logger.info(f"✅ Loaded {len(df)} rows")
    except FileNotFoundError:
        logger.error(f"❌ File not found: {RAW_CSV_FILE}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error loading CSV: {e}")
        sys.exit(1)
    
    initial_count = len(df)
    
    # Step 1: Basic text cleaning
    logger.info("\n📝 Step 1: Basic text cleaning...")
    df["Clean_Text"] = df["Comment"].apply(basic_clean)
    logger.info(f"   ✅ Text cleaned")
    
    # Step 2: Remove short comments
    logger.info(f"\n📏 Step 2: Filtering short comments (min length: {MIN_COMMENT_LENGTH})...")
    before = len(df)
    df = df[df["Clean_Text"].str.len() > MIN_COMMENT_LENGTH]
    removed = before - len(df)
    logger.info(f"   ✅ Removed {removed} short comments ({len(df)} remaining)")
    
    # Step 3: Remove duplicates (exact match)
    logger.info("\n🔄 Step 3: Removing duplicate comments...")
    before = len(df)
    df = df.drop_duplicates(subset=["Clean_Text"], keep="first")
    removed = before - len(df)
    logger.info(f"   ✅ Removed {removed} duplicate comments ({len(df)} remaining)")
    
    # Step 4: Language detection with batching
    logger.info("\n🌍 Step 4: Filtering non-English comments...")
    logger.info("   (This may take a minute - using optimized batch processing)")
    
    # Process in batches to show progress
    batch_size = 100
    language_results = []
    
    for i in tqdm(range(0, len(df), batch_size), desc="   Processing", unit="batch"):
        batch = df.iloc[i:i+batch_size]["Clean_Text"].tolist()
        results = list(is_english_batch(batch))
        language_results.extend(results)
    
    df["is_english"] = language_results
    before = len(df)
    df = df[df["is_english"]]
    removed = before - len(df)
    logger.info(f"   ✅ Kept {len(df)} English comments (removed {removed} non-English)")
    
    # Drop helper columns
    df = df.drop(columns=["is_english", "Comment"], errors="ignore")
    
    # Step 5: Final data quality checks
    logger.info("\n✨ Step 5: Final quality checks...")
    
    # Remove any remaining NaN values
    before = len(df)
    df = df.dropna(subset=["Clean_Text"])
    removed = before - len(df)
    if removed > 0:
        logger.info(f"   ✅ Removed {removed} rows with NaN values")
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Save cleaned data
    logger.info(f"\n💾 Saving cleaned data to: {CLEAN_STAGE_1_FILE}")
    try:
        df.to_csv(CLEAN_STAGE_1_FILE, index=False)
        logger.info(f"   ✅ Saved successfully")
    except Exception as e:
        logger.error(f"   ❌ Error saving file: {e}")
        sys.exit(1)
    
    # Summary statistics
    logger.info("\n" + "=" * 70)
    logger.info("📊 Cleaning Pipeline Summary")
    logger.info("=" * 70)
    logger.info(f"Initial records:        {initial_count:,}")
    logger.info(f"Final records:          {len(df):,}")
    logger.info(f"Total removed:          {initial_count - len(df):,} ({100*(initial_count-len(df))/initial_count:.1f}%)")
    logger.info(f"Data quality score:     {100*len(df)/initial_count:.1f}%")
    logger.info(f"Output file:            {CLEAN_STAGE_1_FILE}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()


