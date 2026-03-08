from pathlib import Path

from ..utils.pdf_parser import extract_text_from_pdf


RISK_KEYWORDS = {
    "default": 0.25,
    "overdue": 0.2,
    "litigation": 0.25,
    "insolvency": 0.3,
    "penalty": 0.15,
    "wilful defaulter": 0.35,
}


def detect_pdf_risk_signals(file_path):
    """Generate a document risk score from adverse keywords in uploaded PDFs."""
    text = extract_text_from_pdf(file_path) if Path(file_path).suffix.lower() == ".pdf" else ""
    lower_text = text.lower()

    score = 0.0
    hits = []

    for keyword, weight in RISK_KEYWORDS.items():
        if keyword in lower_text:
            score += weight
            hits.append(keyword)

    return {
        "document_risk_score": min(round(score, 2), 1.0),
        "document_risk_signals": hits,
    }
