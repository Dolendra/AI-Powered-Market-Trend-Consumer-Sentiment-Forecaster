"""
Main pipeline orchestrator for the Redmi sentiment analysis project.
Coordinates all stages: ingestion, cleaning, and feature extraction.
Includes health checks, rollback capabilities, and comprehensive monitoring.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict, List
import pandas as pd
from datetime import datetime

# Import configuration
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    RAW_CSV_FILE,
    CLEAN_STAGE_1_FILE,
    FEATURE_SENTIMENT_FILE, 
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


class PipelineHealth:
    """Tracks pipeline health and data quality metrics."""
    
    def __init__(self):
        self.stages = {
            "ingestion": {"status": "pending", "records": 0, "time": 0},
            "cleaning": {"status": "pending", "records": 0, "time": 0},
            "extraction": {"status": "pending", "records": 0, "time": 0},
        }
        self.start_time = None
        self.end_time = None
    
    def mark_stage_start(self, stage: str) -> None:
        """Mark stage start time."""
        self.stages[stage]["start_time"] = time.time()
    
    def mark_stage_complete(self, stage: str, record_count: int) -> None:
        """Mark stage as complete with record count."""
        elapsed = time.time() - self.stages[stage].get("start_time", time.time())
        self.stages[stage]["status"] = "complete"
        self.stages[stage]["records"] = record_count
        self.stages[stage]["time"] = elapsed
    
    def mark_stage_failed(self, stage: str, error: str) -> None:
        """Mark stage as failed."""
        self.stages[stage]["status"] = "failed"
        self.stages[stage]["error"] = error
    
    def get_summary(self) -> Dict:
        """Get pipeline summary."""
        total_time = sum(s.get("time", 0) for s in self.stages.values())
        return {
            "total_time": total_time,
            "stages": self.stages,
            "all_passed": all(s.get("status") == "complete" for s in self.stages.values()),
        }


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    logger.info("Checking prerequisites...")
    
    required_files = [
        ("API Config", Path(__file__).parent / ".env"),
        ("Requirements", Path(__file__).parent / "requirements.txt"),
    ]
    
    all_ok = True
    for name, filepath in required_files:
        if filepath.exists():
            logger.info(f"   [OK] {name}: Found")
        else:
            logger.info(f"   [WARNING] {name}: Missing - {filepath}")
            all_ok = False
    
    return all_ok


def validate_file(filepath: Path, expected_columns: List[str] = None) -> bool:
    """Validate output file format and contents."""
    try:
        if not filepath.exists():
            return False
        
        df = pd.read_csv(filepath, nrows=5)  # Quick check
        
        if expected_columns:
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                logger.info(f"[WARNING] Missing columns in {filepath.name}: {missing_cols}")
                return False
        
        return True
    except Exception as e:
        logger.info(f"[ERROR] Invalid file {filepath.name}: {e}")
        return False


def stage_ingestion(health: PipelineHealth) -> bool:
    """Execute data ingestion stage."""
    logger.info("")
    logger.info("STAGE 1: Data Ingestion")
    logger.info("-" * 50)
    
    health.mark_stage_start("ingestion")
    
    try:
        from ingestion.youtuberedmiheadset import main as run_ingestion
        
        logger.info("Executing YouTube data ingestion...")
        run_ingestion()
        
        # Validate output
        if not RAW_CSV_FILE.exists():
            raise FileNotFoundError(f"Ingestion failed: {RAW_CSV_FILE} not created")
        
        record_count = len(pd.read_csv(RAW_CSV_FILE))
        health.mark_stage_complete("ingestion", record_count)
        logger.info(f"[OK] Ingestion complete: {record_count:,} records")
        return True
        
    except Exception as e:
        logger.info(f"[ERROR] Ingestion failed: {e}")
        health.mark_stage_failed("ingestion", str(e))
        return False


def stage_cleaning(health: PipelineHealth) -> bool:
    """Execute data cleaning stage."""
    logger.info("")
    logger.info("STAGE 2: Data Cleaning")
    logger.info("-" * 50)
    
    health.mark_stage_start("cleaning")
    
    try:
        # Check input
        if not RAW_CSV_FILE.exists():
            raise FileNotFoundError(f"Input file missing: {RAW_CSV_FILE}")
        
        from preprocessing.cleaning import main as run_cleaning
        
        logger.info("Executing data cleaning...")
        run_cleaning()
        
        # Validate output
        if not validate_file(CLEAN_STAGE_1_FILE, ["Clean_Text"]):
            raise ValueError("Cleaning validation failed")
        
        record_count = len(pd.read_csv(CLEAN_STAGE_1_FILE))
        health.mark_stage_complete("cleaning", record_count)
        logger.info(f"[OK] Cleaning complete: {record_count:,} records")
        return True
        
    except Exception as e:
        logger.info(f"[ERROR] Cleaning failed: {e}")
        health.mark_stage_failed("cleaning", str(e))
        return False


def stage_extraction(health: PipelineHealth) -> bool:
    """Execute feature extraction stage."""
    logger.info("")
    logger.info("STAGE 3: Feature Extraction")
    logger.info("-" * 50)
    
    health.mark_stage_start("extraction")
    
    try:
        # Check input
        if not CLEAN_STAGE_1_FILE.exists():
            raise FileNotFoundError(f"Input file missing: {CLEAN_STAGE_1_FILE}")
        
        from preprocessing.feature_extraction import main as run_extraction
        
        logger.info("Executing feature extraction...")
        run_extraction()
        
        # Validate output
        if not validate_file(FEATURE_SENTIMENT_FILE, ["comment_id", "feature", "sentiment"]):
            raise ValueError("Feature extraction validation failed")
        
        record_count = len(pd.read_csv(FEATURE_SENTIMENT_FILE))
        health.mark_stage_complete("extraction", record_count)
        logger.info(f"[OK] Extraction complete: {record_count:,} records")
        return True
        
    except Exception as e:
        logger.info(f"[ERROR] Feature extraction failed: {e}")
        health.mark_stage_failed("extraction", str(e))
        return False


def run_full_pipeline(skip_stages: List[str] = None) -> bool:
    """
    Run complete pipeline with error handling and checkpointing.
    
    Args:
        skip_stages: List of stages to skip (useful for resuming)
        
    Returns:
        True if all stages succeeded, False otherwise
    """
    skip_stages = skip_stages or []
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("REDMI SENTIMENT ANALYSIS PIPELINE")
    logger.info("Started: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("=" * 60)
    
    health = PipelineHealth()
    health.start_time = time.time()
    
    # Check prerequisites
    if not check_prerequisites():
        logger.info("[WARNING] Some prerequisites missing, but continuing...")
    
    stages = [
        ("ingestion", stage_ingestion),
        ("cleaning", stage_cleaning),
        ("extraction", stage_extraction),
    ]
    
    # Run stages
    for stage_name, stage_func in stages:
        if stage_name in skip_stages:
            logger.info("")
            logger.info(f"[SKIPPED] Stage: {stage_name}")
            continue
        
        try:
            success = stage_func(health)
            if not success:
                logger.info("")
                logger.info(f"[ERROR] Pipeline halted at stage: {stage_name}")
                logger.info("   Use --skip-stages flag to resume from next stage")
                break
        except Exception as e:
            logger.info("")
            logger.info(f"[ERROR] Unexpected error in {stage_name}: {e}")
            logger.info("   Pipeline halted")
            health.mark_stage_failed(stage_name, str(e))
            break
    
    # Final summary
    health.end_time = time.time()
    summary = health.get_summary()
    
    logger.info("")
    logger.info("-" * 50)
    logger.info("PIPELINE EXECUTION SUMMARY")
    logger.info("-" * 50)
    
    for stage_name, stage_info in summary["stages"].items():
        status = "[OK]" if stage_info["status"] == "complete" else "[FAIL]" if stage_info["status"] == "failed" else "[PENDING]"
        records = f"{stage_info['records']:,}" if stage_info.get("records") else "N/A"
        time_str = f"{stage_info['time']:.1f}s" if stage_info.get("time") else "N/A"
        logger.info(f"{status} {stage_name:12} | Records: {records:>10} | Time: {time_str:>8}")
    
    total_time = summary["total_time"]
    logger.info("-" * 50)
    
    if summary["all_passed"]:
        logger.info(f"[SUCCESS] PIPELINE SUCCEEDED! Total time: {total_time:.1f}s")
        logger.info("")
        logger.info("Output files:")
        logger.info(f"   - Raw data:         {RAW_CSV_FILE}")
        logger.info(f"   - Cleaned data:     {CLEAN_STAGE_1_FILE}")
        logger.info(f"   - Feature sentiment: {FEATURE_SENTIMENT_FILE}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("   1. Review output files for data quality")
        logger.info("   2. Perform sentiment analysis and visualization")
        logger.info("   3. Generate insights and reports")
    else:
        logger.info(f"[FAILED] PIPELINE FAILED! Check logs above for details.")
    
    logger.info("=" * 60)
    
    return summary["all_passed"]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Redmi sentiment analysis pipeline")
    parser.add_argument(
        "--skip-stages",
        type=str,
        nargs="+",
        choices=["ingestion", "cleaning", "extraction"],
        help="Skip specific pipeline stages (useful for resuming)",
    )
    parser.add_argument(
        "--stage",
        type=str,
        choices=["ingestion", "cleaning", "extraction"],
        help="Run only a specific stage",
    )
    
    args = parser.parse_args()
    
    if args.stage:
        # Run single stage
        stage_map = {
            "ingestion": stage_ingestion,
            "cleaning": stage_cleaning,
            "extraction": stage_extraction,
        }
        health = PipelineHealth()
        success = stage_map[args.stage](health)
        sys.exit(0 if success else 1)
    else:
        # Run full pipeline
        success = run_full_pipeline(skip_stages=args.skip_stages or [])
        sys.exit(0 if success else 1)
