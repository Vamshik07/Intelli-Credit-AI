from backend.services.cam_service import generate_cam_reports


def run_cam_agent(state: dict) -> dict:
    company = state.get("company", {})
    risk = state.get("risk", {})
    recommendation = state.get("recommendation", {})
    structured_synthesis = state.get("structured_synthesis", {})
    research = state.get("research", {})
    observations = state.get("credit_officer_observations", "")

    reports = generate_cam_reports(company, risk, recommendation, structured_synthesis, research, observations)
    return {"reports": reports}
