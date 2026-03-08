def run_litigation_agent(state: dict) -> dict:
    research = state.get("research", {})
    text = f"{research.get('analysis', '')} {' '.join(research.get('headlines', []))}".lower()

    litigation_signals = []
    for keyword in [
        "litigation",
        "lawsuit",
        "tribunal",
        "fraud",
        "legal notice",
        "nclt",
        "insolvency",
        "bankruptcy",
        "cheque bounce",
        "arbitration",
        "wilful default",
        "ecourts",
    ]:
        if keyword in text:
            litigation_signals.append(keyword)

    legal_score = 20.0 + min(len(litigation_signals) * 12.0, 75.0)

    return {
        "litigation": {
            "signals": litigation_signals,
            "legal_risk_raw": round(legal_score, 2),
        }
    }
