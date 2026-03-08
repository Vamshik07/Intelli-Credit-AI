from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data" / "credit_training.csv"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "models" / "credit_model.pkl"


def add_supplementary_features(df):
    """Add broad, low-granularity features if they are not present in the CSV."""
    enriched = df.copy()

    if "debt_ratio" not in enriched.columns:
        enriched["debt_ratio"] = (enriched["debt"] / enriched["revenue"]).fillna(0.0)

    if "location_zone" not in enriched.columns:
        enriched["location_zone"] = enriched["revenue"].apply(
            lambda x: "Northern Economic Zone" if x >= 250000000 else "Emerging Growth Zone"
        )

    if "industry_type" not in enriched.columns:
        enriched["industry_type"] = enriched["debt_ratio"].apply(
            lambda x: "Manufacturing" if x < 0.35 else "Retail"
        )

    if "market_trend" not in enriched.columns:
        enriched["market_trend"] = enriched["profit"].apply(
            lambda x: "Stable" if x >= 10000000 else "Volatile"
        )

    if "litigation_risk_score" not in enriched.columns:
        enriched["litigation_risk_score"] = enriched["market_trend"].apply(
            lambda x: 0.15 if x == "Stable" else 0.35
        )

    if "sector_risk_score" not in enriched.columns:
        enriched["sector_risk_score"] = enriched["debt_ratio"].apply(
            lambda x: 0.2 if x < 0.4 else 0.45
        )

    if "promoter_risk_score" not in enriched.columns:
        enriched["promoter_risk_score"] = enriched["profit"].apply(
            lambda x: 0.2 if x > 5000000 else 0.4
        )

    if "document_risk_score" not in enriched.columns:
        enriched["document_risk_score"] = enriched["debt_ratio"].apply(
            lambda x: 0.2 if x < 0.35 else 0.5
        )

    return enriched


def train_and_save_model():
    data = pd.read_csv(DATASET_PATH)
    data = add_supplementary_features(data)

    feature_columns = [
        "revenue",
        "profit",
        "debt",
        "debt_ratio",
        "industry_type",
        "location_zone",
        "market_trend",
        "litigation_risk_score",
        "sector_risk_score",
        "promoter_risk_score",
        "document_risk_score",
    ]

    X = data[feature_columns]
    y = data["risk"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_features = ["industry_type", "location_zone", "market_trend"]
    numeric_features = [
        "revenue",
        "profit",
        "debt",
        "debt_ratio",
        "litigation_risk_score",
        "sector_risk_score",
        "promoter_risk_score",
        "document_risk_score",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=200, random_state=42)),
        ]
    )

    model.fit(X_train, y_train)

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)

    return {
        "rows": len(data),
        "model_output": str(MODEL_OUTPUT_PATH),
    }


def main():
    result = train_and_save_model()
    print(f"Model training completed. Rows: {result['rows']}")
    print(f"Saved model to: {result['model_output']}")


if __name__ == "__main__":
    main()
