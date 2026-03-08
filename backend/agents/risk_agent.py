from backend.services.risk_service import compute_risk, recommend_terms


def run_risk_agent(state: dict) -> dict:
    financial = state.get("financial_metrics", {})
    research = state.get("research", {})
    litigation = state.get("litigation", {})
    primary = state.get("primary_insights", [])
    observations = state.get("credit_officer_observations", "")

    risk = compute_risk(financial, research, primary, litigation, observations)
    recommendation = recommend_terms(risk["final_score"], financial.get("revenue", 0.0))

    return {"risk": risk, "recommendation": recommendation}
