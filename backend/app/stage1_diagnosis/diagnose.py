import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import pandas as pd
import numpy as np

# Path to the pre-trained stage 1 diagnosis model bundle
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[3] / "ml" / "models" / "stage1_diagnosis_model.pkl"

_model_bundle: Optional[Dict[str, Any]] = None


def load_stage1_model(model_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads and caches the Stage 1 diagnosis model bundle."""
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    path = model_path or DEFAULT_MODEL_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Stage 1 model file not found at {path}. "
            "Ensure ml/models/stage1_diagnosis_model.pkl exists."
        )

    _model_bundle = joblib.load(path)
    return _model_bundle


def predict_diagnosis(features: Dict[str, Any], model_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Predicts the root cause failure reason and confidence score for a failed payment.

    Required features in dict:
      - amount (float)
      - hour_of_day (int 0-23)
      - day_of_week (int 0-6)
      - retry_count_so_far (int)
      - past_failure_count (int)
      - subscription_age_days (int)

    Returns:
      {
        "predicted_reason": str,
        "confidence_score": float,
        "class_probabilities": {reason_name: float}
      }
    """
    bundle = load_stage1_model(model_path)
    model = bundle["model"]
    label_enc = bundle.get("label_encoder")
    feature_cols: List[str] = bundle.get(
        "feature_cols",
        ["amount", "hour_of_day", "day_of_week", "retry_count_so_far", "past_failure_count", "subscription_age_days"]
    )

    # Build single-row DataFrame matching training feature columns
    row = {col: [features.get(col, 0)] for col in feature_cols}
    df = pd.DataFrame(row)

    probs = model.predict_proba(df)[0]
    top_idx = int(np.argmax(probs))
    confidence_score = float(probs[top_idx])

    if label_enc is not None:
        predicted_reason = str(label_enc.inverse_transform([top_idx])[0])
        class_names = [str(c) for c in label_enc.classes_]
    else:
        classes = getattr(model, "classes_", [str(i) for i in range(len(probs))])
        predicted_reason = str(classes[top_idx])
        class_names = [str(c) for c in classes]

    class_probabilities = {
        class_names[i]: float(probs[i]) for i in range(len(probs))
    }

    return {
        "predicted_reason": predicted_reason,
        "confidence_score": round(confidence_score, 4),
        "class_probabilities": class_probabilities
    }
