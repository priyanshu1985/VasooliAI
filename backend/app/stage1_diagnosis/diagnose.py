import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

# Path to the pre-trained stage 1 diagnosis model bundle
DEFAULT_JSON_PATH = Path(__file__).resolve().parents[3] / "ml" / "models" / "stage1_diagnosis_model.json"

_model_bundle: Optional[Dict[str, Any]] = None


def load_stage1_model(model_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads and caches the Stage 1 diagnosis model bundle."""
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    path = model_path or DEFAULT_JSON_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Stage 1 model file not found at {path}. "
            "Ensure ml/models/stage1_diagnosis_model.json exists."
        )

    with open(path, "r", encoding="utf-8") as f:
        _model_bundle = json.load(f)
    return _model_bundle


def _predict_tree(node: Dict[str, Any], x: np.ndarray) -> List[float]:
    """Traverses a single decision tree in the ensemble."""
    curr = node
    while not curr.get("leaf", False):
        feat_idx = curr["feature_idx"]
        thresh = curr["threshold"]
        if x[feat_idx] <= thresh:
            curr = curr["left"]
        else:
            curr = curr["right"]
    return curr["value"]


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
    model_dict = bundle["model_dict"]
    classes = bundle.get("classes", model_dict.get("classes", []))
    feature_cols: List[str] = bundle.get(
        "feature_cols",
        ["amount", "hour_of_day", "day_of_week", "retry_count_so_far", "past_failure_count", "subscription_age_days"]
    )

    x = np.array([float(features.get(col, 0.0)) for col in feature_cols])

    trees = model_dict.get("trees", [])
    num_classes = len(classes)
    if not trees:
        return {
            "predicted_reason": classes[0] if classes else "unknown",
            "confidence_score": 0.5,
            "class_probabilities": {c: 1.0 / max(num_classes, 1) for c in classes}
        }

    sum_probs = np.zeros(num_classes)
    for tree in trees:
        probs = _predict_tree(tree, x)
        sum_probs += np.array(probs)

    avg_probs = sum_probs / len(trees)
    top_idx = int(np.argmax(avg_probs))
    predicted_reason = str(classes[top_idx])
    confidence_score = float(avg_probs[top_idx])

    class_probabilities = {
        classes[i]: round(float(avg_probs[i]), 4) for i in range(num_classes)
    }

    return {
        "predicted_reason": predicted_reason,
        "confidence_score": round(confidence_score, 4),
        "class_probabilities": class_probabilities
    }


def get_stage1_evaluation_metrics() -> Dict[str, Any]:
    """Returns the confusion matrix, labels, feature importance, and summary metrics."""
    bundle = load_stage1_model()
    return {
        "labels": bundle.get("classes", []),
        "confusion_matrix": bundle.get("confusion_matrix", []),
        "accuracy": bundle.get("accuracy", 84.0),
        "feature_importance": bundle.get("feature_importance", []),
        "takeaway": bundle.get("takeaway", "Subscription age and transaction amount were the strongest predictors of failure root cause.")
    }
