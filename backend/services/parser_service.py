import json
import re

from backend.services.llm_router import route_llm
from backend.utils.pdf_utils import extract_pdf_text


FINANCIAL_FIELDS = ["revenue", "ebitda", "net_profit", "total_assets", "total_debt"]


def _extract_number(label: str, text: str) -> float:
    pattern = rf"{label}[^\d]*(\d+[\d,]*\.?\d*)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return 0.0
    return float(match.group(1).replace(",", ""))


def parse_financial_document(file_path: str) -> dict:
    # Some uploads can be malformed or mislabeled; return safe defaults instead of crashing the workflow.
    try:
        text = extract_pdf_text(file_path)
    except Exception:
        text = ""

    metrics = {
        "revenue": _extract_number("revenue|turnover", text),
        "ebitda": _extract_number("ebitda", text),
        "net_profit": _extract_number(r"net\s+profit|profit", text),
        "total_assets": _extract_number(r"total\s+assets|assets", text),
        "total_debt": _extract_number(r"total\s+debt|debt|borrowings", text),
    }

    prompt = (
        "Validate and normalize these extracted financial fields to strict JSON with keys "
        "revenue, ebitda, net_profit, total_assets, total_debt.\n"
        f"Extracted: {metrics}\nDocument text snippet:\n{text[:4000]}"
    )

    llm_raw = route_llm("financial_extraction", prompt)
    try:
        llm_json = json.loads(llm_raw)
        for field in FINANCIAL_FIELDS:
            metrics[field] = float(llm_json.get(field, metrics[field]))
    except Exception:
        pass

    return metrics
