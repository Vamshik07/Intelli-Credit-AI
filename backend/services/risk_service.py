from backend.services.ml_model_service import predict_default_probability


def _normalize_score(value: float, min_value: float, max_value: float) -> float:
    if max_value <= min_value:
        return 0.0
    clipped = max(min(value, max_value), min_value)
    return ((clipped - min_value) / (max_value - min_value)) * 100.0


NEGATIVE_PRIMARY_KEYWORDS = [
    "40% capacity",
    "capacity 40",
    "shutdown",
    "strike",
    "plant issue",
    "delay",
    "cash flow stress",
    "overdue",
    "wilful default",
]

POSITIVE_SENTIMENT_KEYWORDS = [
    "growth",
    "expansion",
    "profit",
    "strong demand",
    "upgrade",
    "record order",
]

NEGATIVE_SENTIMENT_KEYWORDS = [
    "decline",
    "loss",
    "downgrade",
    "default",
    "fraud",
    "bankruptcy",
    "slowdown",
]

PAYMENT_POSITIVE_KEYWORDS = [
    "on-time",
    "timely",
    "regular",
    "no overdue",
    "clean repayment",
]

PAYMENT_NEGATIVE_KEYWORDS = [
    "overdue",
    "delay",
    "dpd",
    "default",
    "cheque bounce",
    "npa",
]


def _primary_insight_penalty(primary_insights: list[str], observations: str) -> tuple[float, list[str]]:
    combined = " ".join(primary_insights + [observations]).lower()
    matched = [keyword for keyword in NEGATIVE_PRIMARY_KEYWORDS if keyword in combined]
    penalty = min(float(len(matched)) * 4.0, 18.0)
    return penalty, matched


def _market_sentiment_score(research: dict) -> float:
    text = f"{research.get('analysis', '')} {' '.join(research.get('headlines', []))}".lower()
    positive_hits = sum(text.count(keyword) for keyword in POSITIVE_SENTIMENT_KEYWORDS)
    negative_hits = sum(text.count(keyword) for keyword in NEGATIVE_SENTIMENT_KEYWORDS)

    raw = 50 + (positive_hits * 10) - (negative_hits * 12)
    return max(min(float(raw), 100.0), 0.0)


def _payment_history_signal(primary_insights: list[str], observations: str) -> float:
    text = " ".join(primary_insights + [observations]).lower()
    positive_hits = sum(text.count(keyword) for keyword in PAYMENT_POSITIVE_KEYWORDS)
    negative_hits = sum(text.count(keyword) for keyword in PAYMENT_NEGATIVE_KEYWORDS)

    raw = 70 + (positive_hits * 8) - (negative_hits * 14)
    return max(min(float(raw), 100.0), 0.0)


def _infer_industry_type(research: dict) -> str:
    text = f"{research.get('analysis', '')} {' '.join(research.get('headlines', []))}".lower()
    if any(token in text for token in ["auto", "manufacturing", "plant", "factory"]):
        return "Manufacturing"
    if any(token in text for token in ["infra", "construction", "road", "power"]):
        return "Infrastructure"
    if any(token in text for token in ["it", "software", "tech", "services"]):
        return "Services"
    return "Retail"


def _estimate_revenue_growth(financial: dict) -> float:
    revenue = float(financial.get("revenue", 0.0))
    net_profit = float(financial.get("net_profit", 0.0))
    total_assets = float(financial.get("total_assets", 0.0))
    ebitda = float(financial.get("ebitda", 0.0))

    if revenue <= 0:
        return 0.0

    profitability_component = (net_profit / revenue) * 80.0
    operational_component = (ebitda / revenue) * 35.0
    balance_sheet_component = (net_profit / max(total_assets, 1.0)) * 60.0
    estimated = profitability_component + operational_component + balance_sheet_component
    return max(min(estimated, 60.0), -30.0)


def _build_model_features(
    financial: dict,
    research: dict,
    litigation: dict | None,
    primary_insights: list[str],
    observations: str,
) -> dict:
    revenue = float(financial.get("revenue", 0.0))
    debt = float(financial.get("total_debt", 0.0))
    net_profit = float(financial.get("net_profit", 0.0))
    assets = float(financial.get("total_assets", 0.0))
    ebitda = float(financial.get("ebitda", 0.0))

    equity = max(assets - debt, 1.0)
    debt_to_equity_ratio = debt / equity
    liquidity_ratio = assets / max(debt, 1.0)
    profit_margin = (net_profit / revenue * 100.0) if revenue else 0.0
    cash_flow_stability = (ebitda / revenue * 100.0) if revenue else 0.0
    industry_risk_score = float(research.get("industry_risk", 50.0))
    legal_signals = float(len((litigation or {}).get("signals", [])))
    legal_risk_indicators = min((legal_signals * 20.0) + float((litigation or {}).get("legal_risk_raw", 0.0)) * 0.4, 100.0)

    return {
        "revenue": revenue,
        "profit": net_profit,
        "debt": debt,
        "revenue_growth": _estimate_revenue_growth(financial),
        "debt_to_equity_ratio": debt_to_equity_ratio,
        "liquidity_ratio": liquidity_ratio,
        "profit_margin": profit_margin,
        "cash_flow_stability": max(min(cash_flow_stability, 100.0), 0.0),
        "industry_risk_score": industry_risk_score,
        "legal_risk_indicators": legal_risk_indicators,
        "market_sentiment_score": _market_sentiment_score(research),
        "payment_history_signals": _payment_history_signal(primary_insights, observations),
        "industry_type": _infer_industry_type(research),
    }


def _model_confidence(probability_of_default: float, model_features: dict) -> float:
    signal_clarity = abs(probability_of_default - 0.5) * 2.0
    feature_coverage = sum(1 for value in model_features.values() if value not in (None, "", [])) / max(len(model_features), 1)
    confidence = 45.0 + (signal_clarity * 35.0) + (feature_coverage * 20.0)
    return max(min(confidence, 95.0), 35.0)


def compute_risk(
    financial: dict,
    research: dict,
    primary_insights: list[str],
    litigation: dict | None = None,
    observations: str = "",
    structured_synthesis: dict | None = None,
) -> dict:
    revenue = financial.get("revenue", 0.0)
    debt = financial.get("total_debt", 0.0)
    net_profit = financial.get("net_profit", 0.0)
    ebitda = financial.get("ebitda", 0.0)

    debt_ratio = (debt / revenue) if revenue else 1.0
    profit_margin = (net_profit / revenue) if revenue else 0.0

    financial_strength = (100 - min(debt_ratio * 100, 100)) * 0.6 + max(min(profit_margin * 200, 100), 0) * 0.4
    litigation_raw = float((litigation or {}).get("legal_risk_raw", 0.0))
    legal_risk = max(float(research.get("litigation_risk", 30.0)), litigation_raw)
    promoter_risk = float(research.get("promoter_risk", 30.0))
    operational_capacity = _normalize_score(ebitda, 0, max(revenue * 0.3, 1.0))
    industry_risk = float(research.get("industry_risk", 30.0))
    insight_penalty, matched_primary_signals = _primary_insight_penalty(primary_insights, observations)
    synthesis = structured_synthesis or {}
    synthesis_penalty = float(synthesis.get("risk_penalty", 0.0) or 0.0)

    model_features = _build_model_features(financial, research, litigation, primary_insights, observations)
    ml_prediction = predict_default_probability(model_features)

    # Convert risk-like scores to strength-like contribution where needed.
    legal_strength = 100 - legal_risk
    promoter_strength = 100 - promoter_risk
    industry_strength = 100 - industry_risk

    weighted_score = (
        financial_strength * 0.30
        + legal_strength * 0.20
        + promoter_strength * 0.20
        + operational_capacity * 0.15
        + industry_strength * 0.15
    )

    probability_of_default = None
    model_confidence = None
    if ml_prediction:
        probability_of_default = max(min(float(ml_prediction.get("probability_of_default", 0.0)), 1.0), 0.0)
        model_confidence = _model_confidence(probability_of_default, model_features)

        # Blend calibrated ML PD with transparent rule-based weighted score.
        model_based_score = (1.0 - probability_of_default) * 100.0
        final_score = max((weighted_score * 0.5) + (model_based_score * 0.5) - insight_penalty - synthesis_penalty, 0.0)
    else:
        final_score = max(weighted_score - insight_penalty - synthesis_penalty, 0.0)
        probability_of_default = max(min((100.0 - final_score) / 100.0, 1.0), 0.0)
        model_confidence = _model_confidence(probability_of_default, model_features)

    if final_score > 80:
        recommendation = "Loan Approved"
    elif final_score >= 60:
        recommendation = "Loan Approved with Higher Interest Rate"
    else:
        recommendation = "Loan Rejected"

    reasons = []
    litigation_signals = (litigation or {}).get("signals", [])
    if legal_risk > 60:
        reasons.append("multiple ongoing litigations or legal red flags")
    if litigation_signals:
        reasons.append(f"litigation signals detected: {', '.join(litigation_signals[:5])}")
    if debt_ratio > 0.6:
        reasons.append("high debt ratio")
    if profit_margin < 0.05:
        reasons.append("weak profitability")
    if matched_primary_signals:
        reasons.append(f"primary due-diligence concerns: {', '.join(matched_primary_signals)}")
    discrepancy_flags = synthesis.get("discrepancy_flags", []) if isinstance(synthesis.get("discrepancy_flags", []), list) else []
    if discrepancy_flags:
        reasons.append(f"structured verification flags: {', '.join(discrepancy_flags[:3])}")
    if not reasons:
        reasons.append("balanced financial and external risk profile")

    return {
        "financial_score": round(financial_strength, 2),
        "legal_score": round(legal_strength, 2),
        "promoter_score": round(promoter_strength, 2),
        "operational_score": round(operational_capacity, 2),
        "industry_score": round(industry_strength, 2),
        "final_score": round(final_score, 2),
        "probability_of_default": round(probability_of_default * 100.0, 2),
        "model_confidence": round(model_confidence, 2),
        "recommendation": recommendation,
        "reasons": reasons,
        "components": {
            "financial_strength": round(financial_strength, 2),
            "legal_strength": round(legal_strength, 2),
            "promoter_strength": round(promoter_strength, 2),
            "operational_strength": round(operational_capacity, 2),
            "industry_strength": round(industry_strength, 2),
            "weighted_score": round(weighted_score, 2),
            "primary_insight_penalty": round(insight_penalty, 2),
            "structured_synthesis_penalty": round(synthesis_penalty, 2),
        },
        "ml": {
            "selected_model": (ml_prediction or {}).get("selected_model", "rule_based_fallback"),
            "calibration": (ml_prediction or {}).get("calibration", {}),
            "holdout_metrics": (ml_prediction or {}).get("holdout_metrics", {}),
            "features_used": {
                key: (round(value, 4) if isinstance(value, (int, float)) else value)
                for key, value in model_features.items()
            },
        },
    }


def recommend_terms(final_score: float, annual_revenue: float) -> dict:
    if final_score > 80:
        return {
            "decision": "Approved",
            "recommended_loan_amount": round(annual_revenue * 0.60, 2),
            "suggested_interest_rate": 10.0,
        }

    if final_score >= 60:
        return {
            "decision": "Approved with Conditions",
            "recommended_loan_amount": round(annual_revenue * 0.35, 2),
            "suggested_interest_rate": 12.0,
        }

    return {
        "decision": "Rejected",
        "recommended_loan_amount": 0.0,
        "suggested_interest_rate": 15.0,
    }
