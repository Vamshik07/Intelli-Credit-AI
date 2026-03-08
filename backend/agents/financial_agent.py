from backend.services.parser_service import parse_financial_document


def run_financial_agent(state: dict) -> dict:
    documents = state.get("documents", [])
    allowed_types = {"annual_report", "financial_statement", "gst", "itr", "bank_statement", "auto", "other", ""}
    financial_docs = [d for d in documents if str(d.get("document_type", "")).lower() in allowed_types]

    if not financial_docs:
        financial_docs = documents

    metrics = {
        "revenue": 0.0,
        "ebitda": 0.0,
        "net_profit": 0.0,
        "total_assets": 0.0,
        "total_debt": 0.0,
    }

    parsed_count = 0
    for doc in financial_docs:
        try:
            parsed = parse_financial_document(doc["file_path"])
        except Exception:
            continue

        for key in metrics:
            metrics[key] += float(parsed.get(key, 0.0))
        parsed_count += 1

    if parsed_count:
        count = float(parsed_count)
        metrics = {k: round(v / count, 2) for k, v in metrics.items()}

    return {"financial_metrics": metrics}
