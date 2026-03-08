from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data" / "credit_training.csv"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "models" / "credit_model.pkl"

FEATURE_COLUMNS = [
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
]

NUMERIC_FEATURES = [
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
]

CATEGORICAL_FEATURES = ["industry_type"]


def _safe_div(numerator: pd.Series, denominator: pd.Series, default: float = 0.0) -> pd.Series:
    denom = denominator.replace(0, np.nan)
    result = numerator / denom
    return result.replace([np.inf, -np.inf], np.nan).fillna(default)


def add_credit_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()

    if "industry_type" not in enriched.columns:
        enriched["industry_type"] = enriched["revenue"].apply(
            lambda x: "Manufacturing" if float(x) >= 200_000_000 else "Retail"
        )

    if "revenue_growth" not in enriched.columns:
        enriched["revenue_growth"] = (enriched["profit"] / enriched["revenue"].replace(0, np.nan)).fillna(0.0) * 120

    if "debt_to_equity_ratio" not in enriched.columns:
        equity_proxy = (enriched["revenue"] - enriched["debt"]).clip(lower=1.0)
        enriched["debt_to_equity_ratio"] = _safe_div(enriched["debt"], equity_proxy, default=1.0)

    if "liquidity_ratio" not in enriched.columns:
        current_assets_proxy = enriched["revenue"] * 0.35
        current_liabilities_proxy = enriched["debt"] * 0.55 + 1.0
        enriched["liquidity_ratio"] = _safe_div(current_assets_proxy, current_liabilities_proxy, default=1.0)

    if "profit_margin" not in enriched.columns:
        enriched["profit_margin"] = _safe_div(enriched["profit"], enriched["revenue"], default=0.0) * 100

    if "cash_flow_stability" not in enriched.columns:
        enriched["cash_flow_stability"] = (enriched["profit_margin"] * 1.3).clip(lower=0.0, upper=100.0)

    if "industry_risk_score" not in enriched.columns:
        enriched["industry_risk_score"] = enriched["industry_type"].map(
            {
                "Manufacturing": 42.0,
                "Retail": 56.0,
                "Services": 38.0,
                "Infrastructure": 48.0,
            }
        ).fillna(50.0)

    if "legal_risk_indicators" not in enriched.columns:
        enriched["legal_risk_indicators"] = (enriched["debt_to_equity_ratio"] * 22.0).clip(lower=0.0, upper=100.0)

    if "market_sentiment_score" not in enriched.columns:
        base = 62.0 - (enriched["industry_risk_score"] * 0.25)
        enriched["market_sentiment_score"] = base.clip(lower=0.0, upper=100.0)

    if "payment_history_signals" not in enriched.columns:
        payment_score = 82.0 - (enriched["debt_to_equity_ratio"] * 18.0)
        enriched["payment_history_signals"] = payment_score.clip(lower=0.0, upper=100.0)

    return enriched


def remove_extreme_outliers(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    filtered = df.copy()
    for col in numeric_cols:
        series = filtered[col].astype(float)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            continue
        lower = q1 - 3.0 * iqr
        upper = q3 + 3.0 * iqr
        filtered = filtered[(filtered[col] >= lower) & (filtered[col] <= upper)]

    return filtered.reset_index(drop=True)


def _build_preprocessor() -> ColumnTransformer:
    num_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERIC_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def _build_candidate_models() -> dict[str, object]:
    return {
        "random_forest": RandomForestClassifier(
            n_estimators=450,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
            class_weight="balanced",
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=220,
            learning_rate=0.04,
            max_depth=3,
            random_state=42,
        ),
    }


def _choose_model(X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame, y_val: pd.Series):
    preprocessor = _build_preprocessor()
    candidates = _build_candidate_models()

    best_name = ""
    best_pipeline = None
    best_score = -1.0
    scoreboard: dict[str, dict[str, float]] = {}

    for name, classifier in candidates.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", classifier),
            ]
        )
        pipeline.fit(X_train, y_train)

        probabilities = pipeline.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, probabilities) if len(set(y_val)) > 1 else 0.5
        brier = brier_score_loss(y_val, probabilities)
        combined = auc - brier

        scoreboard[name] = {
            "auc": round(float(auc), 4),
            "brier": round(float(brier), 4),
            "selection_score": round(float(combined), 4),
        }

        if combined > best_score:
            best_score = combined
            best_name = name
            best_pipeline = pipeline

    return best_name, best_pipeline, scoreboard


def _build_calibrated_model(
    base_pipeline: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_full: pd.DataFrame,
    y_full: pd.Series,
):
    class_counts = y_train.value_counts().to_dict()
    min_class_count = min(class_counts.values()) if class_counts else 0

    if min_class_count >= 2:
        cv_folds = min(3, min_class_count)
        calibrated = CalibratedClassifierCV(estimator=base_pipeline, method="sigmoid", cv=cv_folds)
        calibrated.fit(X_train, y_train)
        return calibrated, {"calibrated": True, "method": "sigmoid", "cv": cv_folds, "scope": "train_split"}

    full_counts = y_full.value_counts().to_dict()
    min_full_class_count = min(full_counts.values()) if full_counts else 0
    if min_full_class_count >= 2:
        cv_folds = min(3, min_full_class_count)
        calibrated = CalibratedClassifierCV(estimator=base_pipeline, method="sigmoid", cv=cv_folds)
        calibrated.fit(X_full, y_full)
        return calibrated, {"calibrated": True, "method": "sigmoid", "cv": cv_folds, "scope": "full_dataset"}

    base_pipeline.fit(X_full, y_full)
    return base_pipeline, {"calibrated": False, "method": "none", "cv": 0, "scope": "fallback"}


def train_and_save_model():
    raw = pd.read_csv(DATASET_PATH)
    enriched = add_credit_features(raw)
    cleaned = remove_extreme_outliers(enriched, NUMERIC_FEATURES)

    X = cleaned[FEATURE_COLUMNS].copy()
    y = cleaned["risk"].astype(int)

    stratify = y if y.nunique() > 1 and y.value_counts().min() >= 2 else None
    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=stratify,
    )

    inner_stratify = y_train if y_train.nunique() > 1 and y_train.value_counts().min() >= 2 else None
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.30,
        random_state=7,
        stratify=inner_stratify,
    )

    selected_name, selected_pipeline, model_scores = _choose_model(X_fit, y_fit, X_val, y_val)

    calibrated_model, calibration_info = _build_calibrated_model(selected_pipeline, X_train, y_train, X, y)

    holdout_probabilities = calibrated_model.predict_proba(X_holdout)[:, 1]
    holdout_auc = roc_auc_score(y_holdout, holdout_probabilities) if len(set(y_holdout)) > 1 else 0.5
    holdout_brier = brier_score_loss(y_holdout, holdout_probabilities)

    bundle = {
        "model": calibrated_model,
        "feature_columns": FEATURE_COLUMNS,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "selected_model": selected_name,
        "model_scores": model_scores,
        "calibration": calibration_info,
        "holdout_metrics": {
            "auc": round(float(holdout_auc), 4),
            "brier": round(float(holdout_brier), 4),
        },
        "data_rows": int(len(cleaned)),
    }

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_OUTPUT_PATH)

    return {
        "rows": len(cleaned),
        "model_output": str(MODEL_OUTPUT_PATH),
        "selected_model": selected_name,
        "calibration": calibration_info,
        "holdout_metrics": bundle["holdout_metrics"],
    }


def main():
    result = train_and_save_model()
    print(f"Model training completed. Rows: {result['rows']}")
    print(f"Selected model: {result['selected_model']}")
    print(f"Calibration: {result['calibration']}")
    print(f"Holdout metrics: {result['holdout_metrics']}")
    print(f"Saved model to: {result['model_output']}")


if __name__ == "__main__":
    main()
