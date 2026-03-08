from copy import deepcopy


def _apply_stress(financials, revenue_change=0.0, debt_change=0.0):
    stressed = deepcopy(financials)
    stressed["revenue"] = max(0.0, float(stressed.get("revenue", 0.0)) * (1 + revenue_change))
    stressed["debt"] = max(0.0, float(stressed.get("debt", 0.0)) * (1 + debt_change))
    revenue = stressed.get("revenue", 0.0)
    debt = stressed.get("debt", 0.0)
    stressed["debt_ratio"] = (debt / revenue) if revenue else 1.0
    return stressed


def run_scenarios(financials, calculate_risk_fn):
    """Simulate standard stress cases and re-evaluate risk."""
    scenarios = {
        "revenue_drop_20": _apply_stress(financials, revenue_change=-0.20, debt_change=0.0),
        "debt_increase_25": _apply_stress(financials, revenue_change=0.0, debt_change=0.25),
        "industry_downturn": {**_apply_stress(financials, revenue_change=-0.10, debt_change=0.15), "market_trend": "Declining"},
    }

    results = {}
    for scenario_name, scenario_financials in scenarios.items():
        score, risk_level, explanation, intelligence = calculate_risk_fn(scenario_financials, [])
        results[scenario_name] = {
            "risk_score": score,
            "risk_level": risk_level,
            "explanation": explanation,
            "risk_intelligence": intelligence,
        }

    return results
