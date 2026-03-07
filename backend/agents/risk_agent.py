from pathlib import Path

import joblib
import pandas as pd


ROOT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "credit_model.pkl"
BACKEND_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "credit_model.pkl"
MODEL_PATH = ROOT_MODEL_PATH if ROOT_MODEL_PATH.exists() else BACKEND_MODEL_PATH
model = joblib.load(MODEL_PATH)


def _build_model_features(financials):
    revenue = float(financials.get("revenue", 0.0))
    profit = float(financials.get("profit", 0.0))
    debt = float(financials.get("debt", 0.0))

    debt_ratio = financials.get("debt_ratio")
    if debt_ratio is None:
        debt_ratio = (debt / revenue) if revenue else 0.0

    return {
        "revenue": revenue,
        "profit": profit,
        "debt": debt,
        "debt_ratio": float(debt_ratio),
        "industry_type": financials.get("industry_type", "General"),
        "location_zone": financials.get("location_zone", "Central Economic Zone"),
        "market_trend": financials.get("market_trend", "Stable"),
    }


def build_risk_explanation(risk_level, feature_row):
    trend_note = {
        "Growth": "has shown sustained demand expansion",
        "Stable": "has shown stable growth",
        "Declining": "is facing weaker near-term momentum",
        "Volatile": "is showing higher earnings volatility",
    }.get(feature_row["market_trend"], "is currently mixed")

    leverage_note = (
        "low leverage profile"
        if feature_row["debt_ratio"] < 0.35
        else "elevated leverage profile"
    )

    return (
        f"The applicant operates in the {feature_row['location_zone']}, "
        f"which {trend_note} in the {feature_row['industry_type']} sector. "
        f"Debt ratio is {feature_row['debt_ratio']:.2f}, indicating a {leverage_note}. "
        f"Overall model assessment: {risk_level}."
    )


def calculate_risk(financials, news):
    features = _build_model_features(financials)
    frame = pd.DataFrame([features])

    try:
        # Preferred path: retrained pipeline model with categorical + numeric features.
        probability = model.predict_proba(frame)[0][1]
    except Exception:
        # Backward-compatible path: legacy model trained on only 3 numeric fields.
        legacy_data = [[features["revenue"], features["profit"], features["debt"]]
        ]
        probability = model.predict_proba(legacy_data)[0][1]

    risk_percentage = round(probability * 100, 2)

    if risk_percentage < 30:
        risk_level = "Low Risk"
    elif risk_percentage < 60:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    explanation = build_risk_explanation(risk_level, features)
    return risk_percentage, risk_level, explanation
