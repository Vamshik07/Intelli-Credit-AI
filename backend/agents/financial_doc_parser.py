import re
from pathlib import Path

from ..utils.pdf_parser import extract_text_from_pdf


def _extract_amount(text, label_patterns):
    for pattern in label_patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            value = match.group(1).replace(",", "")
            try:
                return float(value)
            except ValueError:
                continue
    return 0.0


def parse_financial_document(file_path):
    """Extract basic financial statement fields from uploaded docs."""
    text = extract_text_from_pdf(file_path) if Path(file_path).suffix.lower() == ".pdf" else ""

    revenue = _extract_amount(text, [r"revenue[^\d]*(\d+[\d,]*\.?\d*)", r"turnover[^\d]*(\d+[\d,]*\.?\d*)"])
    profit = _extract_amount(text, [r"profit[^\d]*(\d+[\d,]*\.?\d*)", r"pat[^\d]*(\d+[\d,]*\.?\d*)"])
    debt = _extract_amount(text, [r"debt[^\d]*(\d+[\d,]*\.?\d*)", r"borrowings?[^\d]*(\d+[\d,]*\.?\d*)"])

    return {
        "revenue": revenue,
        "profit": profit,
        "debt": debt,
    }
