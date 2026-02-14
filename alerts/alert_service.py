"""
Alert service: detects sentiment spikes and trend shifts, sends email alerts via yagmail.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

sys_path = Path(__file__).resolve().parent.parent
if str(sys_path) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(sys_path))

import os
from config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)

# Default baseline path (stores last run metrics for comparison)
BASELINE_FILE = PROCESSED_DATA_DIR / "reports" / "sentiment_baseline.json"

# Optional config-based thresholds
def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


class AlertService:
    """Detect sentiment spikes/trend shifts and send email alerts using yagmail."""

    def __init__(
        self,
        baseline_path: Path = None,
        spike_threshold: float = None,
        trend_shift_threshold: float = None,
        min_feature_mentions: int = 20,
    ):
        self.baseline_path = baseline_path or BASELINE_FILE
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        self.spike_threshold = spike_threshold if spike_threshold is not None else _float_env("SENTIMENT_SPIKE_THRESHOLD", 0.15)
        self.trend_shift_threshold = trend_shift_threshold if trend_shift_threshold is not None else _float_env("TREND_SHIFT_THRESHOLD", 0.12)
        self.min_feature_mentions = min_feature_mentions
        self._yag = None

    def _get_yagmail(self):
        """Lazy-init yagmail SMTP. Requires YAGMAIL_USER and YAGMAIL_APP_PASSWORD in env."""
        if self._yag is not None:
            return self._yag
        try:
            import os
            import yagmail
            user = os.getenv("YAGMAIL_USER")
            password = os.getenv("YAGMAIL_APP_PASSWORD") or os.getenv("YAGMAIL_PASSWORD")
            if not user or not password:
                logger.warning("YAGMAIL_USER or YAGMAIL_APP_PASSWORD not set; alerts will be logged only.")
                return None
            self._yag = yagmail.SMTP(user=user, password=password)
            return self._yag
        except Exception as e:
            logger.warning(f"yagmail not available: {e}")
            return None

    def _load_baseline(self) -> Optional[Dict]:
        """Load previous sentiment baseline from disk."""
        if not self.baseline_path.exists():
            return None
        try:
            with open(self.baseline_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load baseline: {e}")
            return None

    def _save_baseline(self, data: Dict) -> None:
        """Save current metrics as new baseline."""
        try:
            with open(self.baseline_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save baseline: {e}")

    def get_current_metrics(self, overall: Dict, feature_sentiments: Dict) -> Dict:
        """Build current metrics dict for comparison."""
        return {
            "overall_score": overall.get("sentiment_score", 0),
            "overall_positive": overall.get("positive", 0),
            "overall_negative": overall.get("negative", 0),
            "overall_total": overall.get("total", 0),
            "feature_scores": {
                k: v.get("sentiment_score", 0)
                for k, v in feature_sentiments.items()
                if v.get("total", 0) >= self.min_feature_mentions
            },
        }

    def check_sentiment_spike(self, current: Dict, baseline: Dict) -> List[Dict]:
        """Detect significant change in overall sentiment score."""
        alerts = []
        curr_score = current.get("overall_score", 0)
        base_score = baseline.get("overall_score", curr_score)
        delta = curr_score - base_score
        if abs(delta) >= self.spike_threshold:
            alerts.append({
                "type": "sentiment_spike",
                "severity": "high" if abs(delta) >= 0.25 else "medium",
                "message": f"Overall sentiment moved from {base_score:.3f} to {curr_score:.3f} (Δ {delta:+.3f})",
                "previous_score": base_score,
                "current_score": curr_score,
                "delta": delta,
            })
        return alerts

    def check_trend_shifts(self, current: Dict, baseline: Dict) -> List[Dict]:
        """Detect significant feature-level sentiment trend shifts."""
        alerts = []
        base_scores = baseline.get("feature_scores") or {}
        curr_scores = current.get("feature_scores") or {}
        for feature, curr_score in curr_scores.items():
            base_score = base_scores.get(feature)
            if base_score is None:
                continue
            delta = curr_score - base_score
            if abs(delta) >= self.trend_shift_threshold:
                alerts.append({
                    "type": "trend_shift",
                    "feature": feature,
                    "severity": "high" if abs(delta) >= 0.2 else "medium",
                    "message": f"Feature '{feature}' sentiment: {base_score:.3f} → {curr_score:.3f} (Δ {delta:+.3f})",
                    "previous_score": base_score,
                    "current_score": curr_score,
                    "delta": delta,
                })
        return alerts

    def run_checks(
        self,
        overall_sentiment: Dict,
        feature_sentiments: Dict,
        save_baseline_after: bool = True,
    ) -> List[Dict]:
        """
        Run spike and trend-shift checks. Returns list of alert dicts.
        If save_baseline_after is True, updates baseline file with current metrics.
        """
        current = self.get_current_metrics(overall_sentiment, feature_sentiments)
        baseline = self._load_baseline()

        all_alerts: List[Dict] = []
        if baseline is not None:
            all_alerts.extend(self.check_sentiment_spike(current, baseline))
            all_alerts.extend(self.check_trend_shifts(current, baseline))
        else:
            logger.info("No baseline found; saving current metrics as baseline (no alerts this run).")

        if save_baseline_after:
            self._save_baseline(current)

        return all_alerts

    def send_alert_email(
        self,
        alerts: List[Dict],
        to_emails: Optional[List[str]] = None,
        subject_prefix: str = "[Sentiment Alerts]",
    ) -> bool:
        """Send alert summary via yagmail. to_emails from env ALERT_EMAIL_TO if not provided."""
        if not alerts:
            return True
        import os
        to_emails = to_emails or [
            e.strip() for e in os.getenv("ALERT_EMAIL_TO", "").split(",") if e.strip()
        ]
        if not to_emails:
            logger.warning("No ALERT_EMAIL_TO configured; skipping email send.")
            for a in alerts:
                logger.info("Alert: %s", a.get("message", a))
            return False

        body_lines = [
            "Sentiment Alerts - Redmi Dashboard",
            "-" * 50,
            "",
        ]
        for a in alerts:
            body_lines.append(f"[{a.get('type', 'alert')}] {a.get('message', '')}")
            body_lines.append("")
        body = "\n".join(body_lines)
        subject = f"{subject_prefix} {len(alerts)} alert(s)"

        yag = self._get_yagmail()
        if yag is None:
            logger.info("Alerts (email disabled):\n%s", body)
            return False
        try:
            yag.send(to=to_emails, subject=subject, contents=body)
            logger.info("Alert email sent to %s", to_emails)
            return True
        except Exception as e:
            logger.error("Failed to send alert email: %s", e)
            return False

    def check_and_alert(
        self,
        overall_sentiment: Dict,
        feature_sentiments: Dict,
        send_email: bool = True,
        to_emails: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Run checks and optionally send email. Returns list of alerts (may be empty).
        """
        alerts = self.run_checks(overall_sentiment, feature_sentiments)
        if alerts and send_email:
            self.send_alert_email(alerts, to_emails=to_emails)
        return alerts
