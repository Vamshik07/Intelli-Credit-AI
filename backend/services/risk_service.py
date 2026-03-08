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


def _primary_insight_penalty(primary_insights: list[str], observations: str) -> tuple[float, list[str]]:
    combined = " ".join(primary_insights + [observations]).lower()
    matched = [keyword for keyword in NEGATIVE_PRIMARY_KEYWORDS if keyword in combined]
    penalty = min(float(len(matched)) * 4.0, 18.0)
    return penalty, matched


def compute_risk(
    financial: dict,
    research: dict,
    primary_insights: list[str],
    litigation: dict | None = None,
    observations: str = "",
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
    final_score = max(weighted_score - insight_penalty, 0.0)

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
    if not reasons:
        reasons.append("balanced financial and external risk profile")

    return {
        "financial_score": round(financial_strength, 2),
        "legal_score": round(legal_strength, 2),
        "promoter_score": round(promoter_strength, 2),
        "operational_score": round(operational_capacity, 2),
        "industry_score": round(industry_strength, 2),
        "final_score": round(final_score, 2),
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
