from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "credit_model.pkl"


@lru_cache(maxsize=1)
def load_model_bundle() -> dict | None:
    if not MODEL_PATH.exists():
        return None

    try:
        bundle = joblib.load(MODEL_PATH)
    except Exception:
        return None

    if isinstance(bundle, dict) and "model" in bundle and "feature_columns" in bundle:
        return bundle

    # Backward compatibility for legacy model files containing a raw estimator only.
    return {
        "model": bundle,
        "feature_columns": [
            "revenue",
            "profit",
            "debt",
            "revenue_growth",
            "debt_to_equity_ratio",
            "liquidity_ratio",
            "profit_margin",
            "cash_flow_stability",
            "industry_risk_score",
            "legal_risk_indicators",
            "market_sentiment_score",
            "payment_history_signals",
            "industry_type",
        ],
        "selected_model": "legacy_model",
        "calibration": {"calibrated": False, "method": "unknown", "cv": 0},
    }


def predict_default_probability(feature_payload: dict) -> dict | None:
    bundle = load_model_bundle()
    if not bundle:
        return None

    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    row = {column: feature_payload.get(column) for column in feature_columns}
    frame = pd.DataFrame([row])

    try:
        probabilities = model.predict_proba(frame)[0]
    except Exception:
        return None

    # Convention: class 1 represents risky/default class in our training data.
    probability_of_default = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
    probability_of_non_default = 1.0 - probability_of_default

    return {
        "probability_of_default": probability_of_default,
        "probability_of_non_default": probability_of_non_default,
        "selected_model": bundle.get("selected_model", "unknown"),
        "calibration": bundle.get("calibration", {}),
        "holdout_metrics": bundle.get("holdout_metrics", {}),
    }
