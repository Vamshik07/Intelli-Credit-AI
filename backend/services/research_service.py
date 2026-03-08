import requests
from bs4 import BeautifulSoup

from backend.services.llm_router import route_llm


RISK_KEYWORDS = {
    "litigation": ["litigation", "lawsuit", "court", "tribunal", "nclt", "insolvency", "legal notice", "arbitration"],
    "promoter": ["fraud", "default", "probe", "ed", "sfio", "cbi", "resigned", "governance"],
    "industry": ["slowdown", "ban", "regulation", "rbi", "npas", "supply chain", "recession", "inflation"],
}


def _score_from_headlines(headlines: list[str], keywords: list[str]) -> float:
    joined = " ".join(headlines).lower()
    matches = sum(joined.count(keyword) for keyword in keywords)
    return min(25.0 + (matches * 12.0), 95.0)


def fetch_news(company_name: str) -> list[str]:
    url = f"https://news.google.com/search?q={company_name}%20company&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        return ["Unable to fetch external news"]

    soup = BeautifulSoup(response.text, "html.parser")
    anchors = soup.select("a.DY5T1d")
    headlines = [a.get_text(strip=True) for a in anchors[:10] if a.get_text(strip=True)]
    return headlines or ["No major external alerts found"]


def summarize_research(company_name: str, headlines: list[str]) -> dict:
    prompt = (
        "Analyze these headlines for corporate lending risk and produce concise JSON with keys: "
        "industry_risk, promoter_risk, litigation_risk, summary_points.\n"
        f"Company: {company_name}\nHeadlines: {headlines}"
    )
    raw = route_llm("research", prompt)

    industry_risk = _score_from_headlines(headlines, RISK_KEYWORDS["industry"])
    promoter_risk = _score_from_headlines(headlines, RISK_KEYWORDS["promoter"])
    litigation_risk = _score_from_headlines(headlines, RISK_KEYWORDS["litigation"])

    lowered_raw = raw.lower()
    if "high litigation risk" in lowered_raw or "lawsuit" in lowered_raw:
        litigation_risk = max(litigation_risk, 75.0)
    if "promoter risk" in lowered_raw or "governance" in lowered_raw:
        promoter_risk = max(promoter_risk, 65.0)
    if "regulatory pressure" in lowered_raw or "sector headwind" in lowered_raw:
        industry_risk = max(industry_risk, 60.0)

    return {
        "headlines": headlines,
        "analysis": raw,
        "industry_risk": round(industry_risk, 2),
        "promoter_risk": round(promoter_risk, 2),
        "litigation_risk": round(litigation_risk, 2),
    }
