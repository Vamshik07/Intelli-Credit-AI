"""Databricks feature engineering placeholder for INTELLI-CREDIT.

Transforms curated company records into model-ready risk features.
"""

from __future__ import annotations


def compute_debt_to_income(total_debt: float, revenue: float) -> float:
    if revenue <= 0:
        return 1.0
    return round(total_debt / revenue, 4)


def build_feature_row(raw: dict) -> dict:
    debt = float(raw.get("total_debt", 0.0))
    revenue = float(raw.get("revenue", 0.0))
    return {
        "company_id": raw.get("company_id"),
        "industry": raw.get("industry", "Unknown"),
        "location": raw.get("location", "Unknown"),
        "debt_to_income": compute_debt_to_income(debt, revenue),
        "market_trend": raw.get("market_trend", "Stable"),
    }


if __name__ == "__main__":
    print(build_feature_row({"company_id": "demo", "total_debt": 50, "revenue": 100}))
