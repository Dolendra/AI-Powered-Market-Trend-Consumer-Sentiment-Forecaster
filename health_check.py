"""
Validation and testing module for pipeline components.
Checks data quality, configuration, and system readiness.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import json

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    YOUTUBE_API_KEY,
    GROQ_API_KEY,
    RAW_CSV_FILE,
    CLEAN_STAGE_1_FILE,
    FEATURE_SENTIMENT_FILE,
    CHECKPOINT_FILE,
    MAX_WORKERS,
    LOG_FILE,
)

logger = logging.getLogger(__name__)


class HealthCheck:
    """System health and readiness checks."""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
    
    def check(self, name: str, condition: bool, details: str = "") -> bool:
        """Run a health check."""
        if condition:
            print(f"✅ {name}")
            self.checks_passed += 1
            return True
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
            self.checks_failed += 1
            return False
    
    def warn(self, name: str, condition: bool, details: str = "") -> None:
        """Issue a warning."""
        if not condition:
            print(f"⚠️ {name}")
            if details:
                print(f"   {details}")
            self.warnings.append((name, details))
    
    def summary(self) -> Dict:
        """Get health check summary."""
        total = self.checks_passed + self.checks_failed
        return {
            "passed": self.checks_passed,
            "failed": self.checks_failed,
            "total": total,
            "warnings": len(self.warnings),
            "healthy": self.checks_failed == 0,
            "success_rate": self.checks_passed / total if total > 0 else 0,
        }


def check_configuration() -> HealthCheck:
    """Check configuration."""
    print("\n" + "=" * 70)
    print("🔧 Configuration Health Check")
    print("=" * 70)
    
    health = HealthCheck()
    
    # API Keys
    health.check("YouTube API Key configured", bool(YOUTUBE_API_KEY), "Set YOUTUBE_API_KEY in .env")
    health.check("Groq API Key configured", bool(GROQ_API_KEY), "Set GROQ_API_KEY in .env")
    
    # Paths
    env_file = Path(__file__).parent / ".env"
    health.check(".env file exists", env_file.exists(), f"Create {env_file} from .env.example")
    
    config_file = Path(__file__).parent / "config.py"
    health.check("config.py exists", config_file.exists())
    
    requirements = Path(__file__).parent / "requirements.txt"
    health.check("requirements.txt exists", requirements.exists())
    
    # Configuration values
    health.warn("Workers configured for parallelism", MAX_WORKERS >= 2, f"Current: {MAX_WORKERS}")
    health.warn("Log file path valid", str(LOG_FILE).endswith(".log"), f"Current: {LOG_FILE}")
    
    return health


def check_dependencies() -> HealthCheck:
    """Check Python dependencies."""
    print("\n" + "=" * 70)
    print("📦 Dependencies Health Check")
    print("=" * 70)
    
    health = HealthCheck()
    
    required_packages = {
        "pandas": "Data processing",
        "numpy": "Numerical computing",
        "dotenv": "Environment configuration",
        "google": "YouTube API client",
        "groq": "Groq API client",
        "requests": "HTTP requests",
        "tqdm": "Progress bars",
        "langdetect": "Language detection",
    }
    
    for package, purpose in required_packages.items():
        try:
            __import__(package)
            health.check(f"{package:15} ({purpose})", True)
        except ImportError:
            health.check(f"{package:15} ({purpose})", False, f"Install: pip install {package}")
    
    return health


def check_data_files() -> HealthCheck:
    """Check data files and structure."""
    print("\n" + "=" * 70)
    print("📁 Data Files Health Check")
    print("=" * 70)
    
    health = HealthCheck()
    
    # Check raw data
    if RAW_CSV_FILE.exists():
        try:
            df = pd.read_csv(RAW_CSV_FILE, nrows=5)
            record_count = len(pd.read_csv(RAW_CSV_FILE))
            health.check(
                f"Raw data exists ({record_count:,} records)",
                True,
                f"File: {RAW_CSV_FILE.name}"
            )
            health.check("Raw data has required columns", "Comment" in df.columns)
        except Exception as e:
            health.check("Raw data valid", False, f"Error: {e}")
    else:
        health.warn("Raw data file exists", False, f"Missing: {RAW_CSV_FILE}")
    
    # Check cleaned data
    if CLEAN_STAGE_1_FILE.exists():
        try:
            df = pd.read_csv(CLEAN_STAGE_1_FILE, nrows=5)
            record_count = len(pd.read_csv(CLEAN_STAGE_1_FILE))
            health.check(
                f"Cleaned data exists ({record_count:,} records)",
                True,
                f"File: {CLEAN_STAGE_1_FILE.name}"
            )
            health.check("Cleaned data has Clean_Text column", "Clean_Text" in df.columns)
        except Exception as e:
            health.check("Cleaned data valid", False, f"Error: {e}")
    else:
        health.warn("Cleaned data file exists", False, f"Missing: {CLEAN_STAGE_1_FILE}")
    
    # Check feature sentiment data
    if FEATURE_SENTIMENT_FILE.exists():
        try:
            df = pd.read_csv(FEATURE_SENTIMENT_FILE, nrows=5)
            record_count = len(pd.read_csv(FEATURE_SENTIMENT_FILE))
            health.check(
                f"Feature sentiment exists ({record_count:,} records)",
                True,
                f"File: {FEATURE_SENTIMENT_FILE.name}"
            )
            required_cols = {"comment_id", "feature", "sentiment"}
            has_cols = required_cols.issubset(set(df.columns))
            health.check("Feature sentiment has required columns", has_cols)
            
            # Check sentiment values
            unique_sentiments = df["sentiment"].unique()
            valid_sentiments = set(unique_sentiments).issubset({"positive", "negative", "neutral"})
            health.check("Sentiment values valid", valid_sentiments, f"Found: {unique_sentiments}")
            
        except Exception as e:
            health.check("Feature sentiment valid", False, f"Error: {e}")
    else:
        health.warn("Feature sentiment file exists", False, f"Missing: {FEATURE_SENTIMENT_FILE}")
    
    # Check checkpoint
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                checkpoint = json.load(f)
            processed_count = len(checkpoint.get("processed_ids", []))
            health.check(f"Checkpoint valid ({processed_count} processed)", True)
        except Exception as e:
            health.check("Checkpoint valid", False, f"Error: {e}")
    else:
        health.warn("Checkpoint file exists", False, "(Not needed on first run)")
    
    # Check data directories
    for dir_name in ["raw", "intermediate", "processed"]:
        dir_path = Path(__file__).parent / "data" / dir_name
        health.check(f"Directory '{dir_name}' exists", dir_path.exists())
    
    return health


def check_logs() -> HealthCheck:
    """Check log file health."""
    print("\n" + "=" * 70)
    print("📋 Logs Health Check")
    print("=" * 70)
    
    health = HealthCheck()
    
    if LOG_FILE.exists():
        size_mb = LOG_FILE.stat().st_size / (1024 * 1024)
        health.check(f"Log file exists ({size_mb:.2f} MB)", True, f"File: {LOG_FILE}")
        
        # Check for errors in log
        with open(LOG_FILE, "r") as f:
            content = f.read()
            error_count = content.count("❌")
            warning_count = content.count("⚠️")
        
        health.warn("No errors in log", error_count == 0, f"Found {error_count} errors")
        health.warn("No warnings in log", warning_count == 0, f"Found {warning_count} warnings")
    else:
        health.warn("Log file exists", False, "Logs will be created on first run")
    
    return health


def run_all_checks() -> bool:
    """Run all health checks."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 18 + "🏥 SYSTEM HEALTH CHECK REPORT 🏥" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")
    
    checks = [
        ("Configuration", check_configuration),
        ("Dependencies", check_dependencies),
        ("Data Files", check_data_files),
        ("Logs", check_logs),
    ]
    
    all_results = []
    for check_name, check_func in checks:
        results = check_func()
        all_results.append((check_name, results))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Overall Summary")
    print("=" * 70)
    
    total_passed = sum(r[1].checks_passed for r in all_results)
    total_failed = sum(r[1].checks_failed for r in all_results)
    total_warnings = sum(r[1].warnings.__len__() for r in all_results)
    
    for check_name, results in all_results:
        summary = results.summary()
        status = "✅" if summary["healthy"] else "⚠️"
        print(f"{status} {check_name:20} | Passed: {summary['passed']:2} | Failed: {summary['failed']:2}")
    
    print("=" * 70)
    print(f"Total Passed:   {total_passed}")
    print(f"Total Failed:   {total_failed}")
    print(f"Total Warnings: {total_warnings}")
    
    if total_failed == 0:
        print("\n✅ SYSTEM READY FOR EXECUTION")
        return True
    else:
        print(f"\n❌ {total_failed} issue(s) need attention before running pipeline")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
