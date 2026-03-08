from backend.services.research_service import fetch_news, summarize_research


def run_research_agent(state: dict) -> dict:
    company = state.get("company", {})
    company_name = company.get("name", "Unknown Company")

    headlines = fetch_news(company_name)
    research = summarize_research(company_name, headlines)

    return {"research": research}
