"""
Optimized feature-level sentiment extraction using Groq API with concurrent processing.
Implements parallel API calls, intelligent error handling, and automatic checkpointing.
"""

import logging
import json
import os
import sys
import csv
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import pandas as pd
from groq import Groq
from tqdm import tqdm

# Import configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    CLEAN_STAGE_1_FILE,
    FEATURE_SENTIMENT_FILE,
    CHECKPOINT_FILE,
    MAX_WORKERS,
    BATCH_SIZE,
    API_RATE_LIMIT,
    MAX_RETRIES,
    LOG_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
    PRODUCT_FEATURES,
)

# Configure logging
import sys
import io

# Create handlers
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
# Reconfigure stderr to use UTF-8 for StreamHandler on Windows
if sys.platform == 'win32':
    # Use UTF-8 for console output on Windows
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
stream_handler = logging.StreamHandler(sys.stderr)

# Create formatter and add to handlers
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Initialize Groq client
try:
    client = Groq(api_key=GROQ_API_KEY)
    logger.info("[OK] Groq API client initialized")
except Exception as e:
    logger.error(f"[ERROR] Failed to initialize Groq API: {e}")
    sys.exit(1)

# ============================================================
# SYSTEM PROMPT FOR FEATURE EXTRACTION
# ============================================================
SYSTEM_PROMPT = """
You are an expert consumer sentiment analyst specializing in audio products.

Task: Analyze user comments about Redmi earbuds and extract feature-level sentiment.

Steps:
1. Identify which Redmi earbud model(s) are mentioned (or "unknown")
2. Extract sentiment for EACH product feature discussed
3. Provide brief evidence from the comment

Sentiment labels: positive | negative | neutral

Important rules:
- Only include features explicitly mentioned in the comment
- Base sentiment strictly on the text
- Do NOT invent features or opinions
- Evidence must be a direct quote or paraphrase from the comment

Available features:
sound_quality, bass, mic_quality, call_quality, battery, charging, build_quality, 
comfort, fit, connectivity, latency, anc, price, value_for_money, design, durability

Respond with ONLY valid JSON in this format:
{
  "model": ["model_name"],
  "features": {
    "feature_name": {
      "sentiment": "positive|negative|neutral",
      "evidence": "quote or paraphrase"
    }
  }
}
"""


def load_checkpoint() -> Dict:
    """Load processing checkpoint to resume from interruption."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                checkpoint = json.load(f)
                logger.info(f"📍 Checkpoint found: {len(checkpoint.get('processed_ids', []))} comments already processed")
                return checkpoint
        except Exception as e:
            logger.warning(f"⚠️ Error loading checkpoint: {e}")
    
    return {"processed_ids": [], "failed_ids": [], "last_processed_time": 0}


def save_checkpoint(checkpoint: Dict) -> None:
    """Save current processing state."""
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(checkpoint, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Error saving checkpoint: {e}")


def extract_features(comment: str, comment_id: int, max_retries: int = MAX_RETRIES) -> Optional[Dict]:
    """
    Extract feature sentiments from a comment with retry logic.
    
    Args:
        comment: Text to analyze
        comment_id: Unique comment identifier
        max_retries: Number of retries on failure
        
    Returns:
        Parsed JSON response or None on failure
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": comment},
                ],
                temperature=0,
                response_format={"type": "json_object"},
                timeout=30,
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Comment {comment_id}: Invalid JSON response (attempt {attempt + 1})")
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️ Comment {comment_id}: API error (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"❌ Comment {comment_id}: Failed after {max_retries} retries")
    
    return None


def process_comment(args: tuple) -> Optional[List[Dict]]:
    """
    Process single comment and generate feature-sentiment records.
    
    Args:
        args: Tuple of (index, row_data, comment_id)
        
    Returns:
        List of feature records or None on failure
    """
    try:
        comment_id, comment_text, likes = args
        
        # Rate limiting
        time.sleep(API_RATE_LIMIT)
        
        # Extract features
        result = extract_features(comment_text, comment_id)
        
        if not result or not result.get("features"):
            # Failed extraction - return neutral placeholder
            return [{
                "comment_id": comment_id,
                "model": "unknown",
                "feature": "none",
                "sentiment": "neutral",
                "evidence": "extraction_failed",
                "likes": likes,
            }]
        
        # Generate records for each feature
        records = []
        models = result.get("model", ["unknown"])
        features = result.get("features", {})
        
        for model in models:
            for feature, data in features.items():
                records.append({
                    "comment_id": comment_id,
                    "model": model,
                    "feature": feature,
                    "sentiment": data.get("sentiment", "neutral"),
                    "evidence": data.get("evidence", "")[:200],  # Truncate evidence
                    "likes": likes,
                })
        
        return records if records else None
        
    except Exception as e:
        logger.error(f"❌ Error processing comment {comment_id}: {e}")
        return None


def main():
    """Main feature extraction pipeline with parallel processing."""
    logger.info("=" * 70)
    logger.info("[START] Starting Feature-Level Sentiment Extraction")
    logger.info("=" * 70)
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    processed_ids = set(checkpoint.get("processed_ids", []))
    
    # Load input data
    logger.info(f"\n[FILE] Loading cleaned data from: {CLEAN_STAGE_1_FILE}")
    try:
        df = pd.read_csv(CLEAN_STAGE_1_FILE)
        logger.info(f"   [OK] Loaded {len(df)} comments")
    except FileNotFoundError:
        logger.error(f"[ERROR] File not found: {CLEAN_STAGE_1_FILE}")
        logger.error("   Please run cleaning.py first")
        sys.exit(1)
    
    # Create output file if doesn't exist
    if not FEATURE_SENTIMENT_FILE.exists():
        logger.info(f"\n📄 Creating output file: {FEATURE_SENTIMENT_FILE}")
        pd.DataFrame(columns=[
            "comment_id", "model", "feature", "sentiment", "evidence", "likes"
        ]).to_csv(FEATURE_SENTIMENT_FILE, index=False, quoting=csv.QUOTE_ALL)
    
    # Filter unprocessed comments
    df["comment_id"] = range(len(df))
    unprocessed = df[~df["comment_id"].isin(processed_ids)].copy()
    
    if len(unprocessed) == 0:
        logger.info("[OK] All comments already processed!")
        return
    
    logger.info(f"\n[TIME] Processing {len(unprocessed)} unprocessed comments ({len(processed_ids)} already done)")
    logger.info(f"   Using {MAX_WORKERS} concurrent workers, batch size: {BATCH_SIZE}")
    
    # Prepare data for processing
    tasks = [
        (row["comment_id"], row["Clean_Text"], row.get("Likes", 0))
        for _, row in unprocessed.iterrows()
    ]
    
    # Process with ThreadPoolExecutor for parallel API calls
    all_records = []
    failed_ids = []
    batch_counter = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_comment, task): task[0] for task in tasks}
        
        with tqdm(total=len(tasks), desc="   Processing", unit="comment") as pbar:
            for future in as_completed(futures):
                comment_id = futures[future]
                try:
                    records = future.result()
                    if records:
                        all_records.extend(records)
                    else:
                        failed_ids.append(comment_id)
                except Exception as e:
                    logger.error(f"[ERROR] Thread error for comment {comment_id}: {e}")
                    failed_ids.append(comment_id)
                finally:
                    pbar.update(1)
                
                # Save every BATCH_SIZE comments to avoid data loss
                batch_counter += 1
                if batch_counter % BATCH_SIZE == 0:
                    if all_records:
                        logger.info(f"\n[SAVE] Saving batch of {len(all_records)} records at comment {batch_counter}...")
                        try:
                            result_df = pd.DataFrame(all_records)
                            result_df.to_csv(
                                FEATURE_SENTIMENT_FILE,
                                mode="a",
                                header=False,
                                index=False,
                                quoting=csv.QUOTE_ALL,
                            )
                            logger.info(f"   [OK] Batch saved to {FEATURE_SENTIMENT_FILE}")
                            # Update checkpoint after successful save
                            checkpoint["processed_ids"].extend([t[0] for t in tasks[:batch_counter]])
                            save_checkpoint(checkpoint)
                            all_records = []  # Clear batch after saving
                        except Exception as e:
                            logger.error(f"   [ERROR] Error saving results: {e}")
                    else:
                        logger.warning(f"   [WARN] No records to save at batch {batch_counter // BATCH_SIZE}")
    
    # Save any remaining records
    if all_records:
        logger.info(f"\n[SAVE] Saving final batch of {len(all_records)} feature records...")
        try:
            result_df = pd.DataFrame(all_records)
            result_df.to_csv(
                FEATURE_SENTIMENT_FILE,
                mode="a",
                header=False,
                index=False,
                quoting=csv.QUOTE_ALL,
            )
            logger.info(f"   [OK] Saved successfully")
        except Exception as e:
            logger.error(f"   [ERROR] Error saving results: {e}")
    
    # Update checkpoint every 20 comments during processing too
    # (already done in main loop above)
    
    # Final checkpoint update
    final_processed = set(checkpoint.get("processed_ids", []))
    final_processed.update([t[0] for t in tasks])
    checkpoint["processed_ids"] = list(final_processed)
    checkpoint["failed_ids"].extend(failed_ids)
    checkpoint["last_processed_time"] = time.time()
    save_checkpoint(checkpoint)
    
    # Summary statistics
    logger.info("\n" + "=" * 70)
    logger.info("📊 Extraction Summary")
    logger.info("=" * 70)
    logger.info(f"Comments processed:     {len(tasks):,}")
    logger.info(f"Feature records generated: {len(all_records):,}")
    logger.info(f"Failed extractions:     {len(failed_ids)}")
    logger.info(f"Success rate:           {100*(len(tasks)-len(failed_ids))/len(tasks):.1f}%")
    logger.info(f"Output file:            {FEATURE_SENTIMENT_FILE}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
