from backend.services.synthesis_service import synthesize_structured_insights


def run_synthesis_agent(state: dict) -> dict:
    documents = state.get("documents", [])
    financial_metrics = state.get("financial_metrics", {})
    primary_insights = state.get("primary_insights", [])

    structured_synthesis = synthesize_structured_insights(documents, financial_metrics, primary_insights)
    return {"structured_synthesis": structured_synthesis}
