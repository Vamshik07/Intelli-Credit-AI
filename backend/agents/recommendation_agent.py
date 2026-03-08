def recommend_loan(financials, risk_level):
    """Compute decision, loan limit, and suggested rate based on risk bucket."""
    revenue = float(financials.get("revenue", 0.0))
    base_rate = 9.0

    if risk_level == "Low Risk":
        decision = "Approve"
        loan_limit = revenue * 0.60
        interest_rate = base_rate + 1.0
    elif risk_level == "Medium Risk":
        decision = "Approve with Conditions"
        loan_limit = revenue * 0.35
        interest_rate = base_rate + 3.0
    else:
        decision = "Reject"
        loan_limit = 0.0
        interest_rate = base_rate + 6.0

    return {
        "decision": decision,
        "recommended_loan_limit": round(loan_limit, 2),
        "suggested_interest_rate": round(interest_rate, 2),
    }
