import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import pandas as pd
import numpy as np

# Path to pre-trained stage 2 retry model bundle
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[3] / "ml" / "models" / "stage2_retry_model.pkl"

# Hard architectural / regulatory constraints
RBI_MIN_NOTICE_HOURS = 24
MAX_RETRIES_PER_30_DAYS = 4
DEFAULT_CANDIDATE_WINDOWS = [24, 48, 72, 168]  # 24h, 48h, 3 days, 7 days

_model_bundle: Optional[Dict[str, Any]] = None


def load_stage2_model(model_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads and caches the Stage 2 retry model bundle."""
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    path = model_path or DEFAULT_MODEL_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Stage 2 model file not found at {path}. "
            "Ensure ml/models/stage2_retry_model.pkl exists."
        )

    _model_bundle = joblib.load(path)
    return _model_bundle


def sequence_retry(
    payment_features: Dict[str, Any],
    retry_count_in_30_days: int = 0,
    model_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Evaluates candidate retry windows and selects the optimal window using the trained ML model.

    Enforces hard constraints:
      1. Max 4 retries in 30 days (Stopping Rule).
      2. No retry within the 24-hour RBI pre-debit notice window.

    Input features expected:
      - amount (float)
      - hour_of_day (int 0-23)
      - day_of_week (int 0-6)
      - past_failure_count (int)
      - is_soft_decline_true (int/bool 1 or 0)
    """
    # 1. HARD STOPPING RULE CHECK: Max 4 retries per rolling 30-day period
    if retry_count_in_30_days >= MAX_RETRIES_PER_30_DAYS:
        return {
            "can_retry": False,
            "status": "STOPPED",
            "stopping_rule_triggered": "MAX_RETRIES_EXCEEDED",
            "message": f"Hard stopping rule reached: {retry_count_in_30_days} retries in 30 days (cap is {MAX_RETRIES_PER_30_DAYS}). Escalate to Stage 3.",
            "best_window_hours": None,
            "predicted_success_prob": 0.0,
            "candidate_evaluations": []
        }

    bundle = load_stage2_model(model_path)
    model = bundle["model"]
    feature_cols: List[str] = bundle.get(
        "feature_cols",
        ["amount", "hour_of_day", "day_of_week", "past_failure_count", "is_soft_decline_true", "window_hours"]
    )
    raw_candidates: List[int] = bundle.get("candidate_windows_hours", DEFAULT_CANDIDATE_WINDOWS)

    # 2. HARD REGULATORY CONSTRAINT: Filter candidate windows against RBI 24-hour notice minimum
    valid_candidates = [w for w in raw_candidates if w >= RBI_MIN_NOTICE_HOURS]

    if not valid_candidates:
        return {
            "can_retry": False,
            "status": "STOPPED",
            "stopping_rule_triggered": "RBI_COMPLIANCE_VIOLATION",
            "message": "No candidate window satisfies the mandatory 24-hour RBI pre-debit notice window.",
            "best_window_hours": None,
            "predicted_success_prob": 0.0,
            "candidate_evaluations": []
        }

    # Construct evaluation rows for all valid windows
    candidate_rows = []
    for window in valid_candidates:
        row = {
            "amount": payment_features.get("amount", 0.0),
            "hour_of_day": payment_features.get("hour_of_day", 12),
            "day_of_week": payment_features.get("day_of_week", 0),
            "past_failure_count": payment_features.get("past_failure_count", 0),
            "is_soft_decline_true": int(bool(payment_features.get("is_soft_decline_true", 1))),
            "window_hours": window
        }
        candidate_rows.append(row)

    df_candidates = pd.DataFrame(candidate_rows)[feature_cols]
    probs = model.predict_proba(df_candidates)[:, 1]

    candidate_evaluations = []
    for idx, window in enumerate(valid_candidates):
        prob = float(probs[idx])
        candidate_evaluations.append({
            "window_hours": window,
            "success_probability": round(prob, 4)
        })

    # Pick the window with highest predicted success probability
    best_idx = int(np.argmax(probs))
    best_window = valid_candidates[best_idx]
    best_prob = float(probs[best_idx])

    return {
        "can_retry": True,
        "status": "SCHEDULED",
        "stopping_rule_triggered": None,
        "best_window_hours": best_window,
        "predicted_success_prob": round(best_prob, 4),
        "rbi_notice_compliant": True,
        "retry_attempt_number": retry_count_in_30_days + 1,
        "candidate_evaluations": candidate_evaluations
    }
