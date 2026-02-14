"""
Analytics and reporting module for sentiment analysis results.
Generates visualizations, statistics, and insights from feature sentiment data.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import json
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    FEATURE_SENTIMENT_FILE,
    FEATURE_SENTIMENT_CLEANED_FILE,
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


class SentimentAnalyzer:
    """Comprehensive sentiment analysis and reporting."""
    
    def __init__(self, feature_file: Path = None):
        """Initialize analyzer with feature sentiment data."""
        # Use cleaned file if available, otherwise fall back to original
        if feature_file is None:
            if FEATURE_SENTIMENT_CLEANED_FILE.exists():
                self.feature_file = FEATURE_SENTIMENT_CLEANED_FILE
            else:
                self.feature_file = FEATURE_SENTIMENT_FILE
        else:
            self.feature_file = feature_file
        self.df = None
        self.load_data()
    
    def load_data(self) -> None:
        """Load feature sentiment data."""
        try:
            self.df = pd.read_csv(self.feature_file)
            logger.info(f"[OK] Loaded {len(self.df)} feature records")
        except FileNotFoundError:
            logger.error(f"[ERROR] File not found: {self.feature_file}")
            sys.exit(1)
    
    def get_overall_sentiment_score(self) -> Dict:
        """Calculate overall sentiment score."""
        sentiment_counts = self.df["sentiment"].value_counts()
        total = len(self.df)
        
        positive = sentiment_counts.get("positive", 0)
        negative = sentiment_counts.get("negative", 0)
        neutral = sentiment_counts.get("neutral", 0)
        
        # Simple sentiment score: (positive - negative) / total
        score = (positive - negative) / total if total > 0 else 0
        
        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "total": total,
            "sentiment_score": round(score, 3),  # Range: -1 to 1
            "positive_ratio": round(positive / total, 3) if total > 0 else 0,
            "negative_ratio": round(negative / total, 3) if total > 0 else 0,
        }
    
    def get_feature_sentiments(self) -> Dict:
        """Get sentiment breakdown by feature."""
        feature_analysis = defaultdict(lambda: {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "total": 0,
        })
        
        for _, row in self.df.iterrows():
            feature = row["feature"]
            sentiment = row["sentiment"]
            
            feature_analysis[feature]["total"] += 1
            feature_analysis[feature][sentiment] += 1
        
        # Calculate sentiment scores for each feature
        result = {}
        for feature, counts in sorted(feature_analysis.items()):
            total = counts["total"]
            positive = counts["positive"]
            negative = counts["negative"]
            
            sentiment_score = (positive - negative) / total if total > 0 else 0
            
            result[feature] = {
                "positive": int(positive),  # Convert numpy types
                "negative": int(negative),
                "neutral": int(counts["neutral"]),
                "total": int(total),
                "sentiment_score": float(round(sentiment_score, 3)),
                "positive_ratio": float(round(positive / total, 3) if total > 0 else 0),
            }
        
        return result
    
    def get_model_sentiments(self) -> Dict:
        """Get sentiment breakdown by product model."""
        model_analysis = defaultdict(lambda: {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "total": 0,
        })
        
        for _, row in self.df.iterrows():
            model = row["model"]
            sentiment = row["sentiment"]
            
            model_analysis[model]["total"] += 1
            model_analysis[model][sentiment] += 1
        
        # Calculate sentiment scores
        result = {}
        for model, counts in sorted(model_analysis.items()):
            total = counts["total"]
            positive = counts["positive"]
            negative = counts["negative"]
            
            sentiment_score = (positive - negative) / total if total > 0 else 0
            
            result[model] = {
                "positive": int(positive),  # Convert numpy types
                "negative": int(negative),
                "neutral": int(counts["neutral"]),
                "total": int(total),
                "sentiment_score": float(round(sentiment_score, 3)),
                "positive_ratio": float(round(positive / total, 3) if total > 0 else 0),
            }
        
        return result
    
    def get_top_features(self, n: int = 10, sentiment: str = None) -> Dict:
        """Get top features by mention frequency or sentiment."""
        features = self.df["feature"].value_counts()
        
        if sentiment:
            features = self.df[self.df["sentiment"] == sentiment]["feature"].value_counts()
        
        # Convert to dict and convert numpy types to native Python types
        result = {}
        for feature, count in features.head(n).items():
            result[str(feature)] = int(count)  # Convert numpy.int64 to Python int
        
        return result
    
    def get_top_comments_by_feature(self, feature: str, sentiment: str = "positive", n: int = 5) -> List[Dict]:
        """Get top comments for a feature with specific sentiment."""
        filtered = self.df[
            (self.df["feature"] == feature) &
            (self.df["sentiment"] == sentiment)
        ].sort_values("likes", ascending=False)
        
        results = []
        for _, row in filtered.head(n).iterrows():
            results.append({
                "feature": str(row["feature"]),
                "sentiment": str(row["sentiment"]),
                "evidence": str(row["evidence"]),
                "likes": int(row["likes"]) if pd.notna(row["likes"]) else 0,  # Convert numpy types
                "model": str(row["model"]),
            })
        
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive analysis report."""
        logger.info("")
        logger.info("GENERATING SENTIMENT ANALYSIS REPORT")
        logger.info("-" * 50)
        
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "total_records": len(self.df),
            "overall_sentiment": self.get_overall_sentiment_score(),
            "feature_sentiments": self.get_feature_sentiments(),
            "model_sentiments": self.get_model_sentiments(),
            "top_features": self.get_top_features(n=15),
        }
        
        # Log summary
        overall = report["overall_sentiment"]
        logger.info("")
        logger.info(f"Overall Sentiment Score: {overall['sentiment_score']:.3f}")
        logger.info(f"   Positive: {overall['positive']:,} ({overall['positive_ratio']:.1%})")
        logger.info(f"   Negative: {overall['negative']:,} ({overall['negative_ratio']:.1%})")
        logger.info(f"   Neutral:  {overall['neutral']:,}")
        
        logger.info("")
        logger.info("Top Features by Mentions:")
        for feature, count in list(report["top_features"].items())[:5]:
            logger.info(f"   {feature:20} : {count:,} mentions")
        
        logger.info("")
        logger.info("Feature Sentiment Scores (Top 5 Positive):")
        features = report["feature_sentiments"]
        top_features = sorted(features.items(), key=lambda x: x[1]["sentiment_score"], reverse=True)[:5]
        for feature, stats in top_features:
            logger.info(f"   {feature:20} : {stats['sentiment_score']:>6.3f} ({stats['positive']:,}+, {stats['negative']:,}-)")
        
        return report
    
    def export_report(self, output_dir: Path = None) -> None:
        """Export report to JSON file."""
        report = self.generate_report()
        
        output_dir = output_dir or Path(__file__).parent / "data" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"sentiment_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"\n[OK] Report exported to: {output_file}")


def main():
    """Generate and display analysis report."""
    analyzer = SentimentAnalyzer()
    analyzer.export_report()


if __name__ == "__main__":
    main()
