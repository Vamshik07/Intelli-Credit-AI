import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("data/credit_training.csv")


def add_supplementary_features(df):
    """Add broad, low-granularity features if they are not present in the CSV."""
    enriched = df.copy()

    if "debt_ratio" not in enriched.columns:
        # Debt ratio captures leverage more robustly than raw debt alone.
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

    return enriched


data = add_supplementary_features(data)

print("Dataset Loaded Successfully\n")
print(data)

# Features (inputs)
feature_columns = [
    "revenue",
    "profit",
    "debt",
    "debt_ratio",
    "industry_type",
    "location_zone",
    "market_trend",
]
X = data[feature_columns]

# Target (output)
y = data["risk"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\nTraining ML Model...")

# Preprocess categorical fields before fitting classifier
categorical_features = ["industry_type", "location_zone", "market_trend"]
numeric_features = ["revenue", "profit", "debt", "debt_ratio"]

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

# Train model
model.fit(X_train, y_train)

print("Model Training Completed")

# Save model
joblib.dump(model, "models/credit_model.pkl")

print("Model Saved Successfully in models/credit_model.pkl")