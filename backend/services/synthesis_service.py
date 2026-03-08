from __future__ import annotations

from backend.agents.bank_statement_parser import parse_bank_statement
from backend.agents.financial_doc_parser import parse_financial_document
from backend.agents.gst_parser import parse_gst_file


def _safe_ratio(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    return float(numerator) / float(denominator)


def _pct_gap(a: float, b: float) -> float:
    baseline = max(abs(float(a)), abs(float(b)), 1.0)
    return abs(float(a) - float(b)) / baseline * 100.0


def synthesize_structured_insights(documents: list[dict], financial_metrics: dict, primary_insights: list[str]) -> dict:
    gst_totals = {
        "outward_supply": 0.0,
        "inward_supply": 0.0,
        "gstr2a_itc": 0.0,
        "gstr3b_itc": 0.0,
        "compliance_score": 0.0,
        "count": 0,
    }
    bank_totals = {
        "total_credit": 0.0,
        "total_debit": 0.0,
        "net_cashflow": 0.0,
        "bounce_count": 0,
        "count": 0,
    }
    itr_totals = {"revenue": 0.0, "profit": 0.0, "debt": 0.0, "count": 0}

    for doc in documents:
        file_path = doc.get("file_path", "")
        doc_type = str(doc.get("document_type", "")).lower()
        path_lower = file_path.lower()

        is_gst = "gst" in doc_type or "gstr" in path_lower
        is_bank = "bank" in doc_type or "statement" in path_lower
        is_itr = "itr" in doc_type or "income_tax" in doc_type or "itr" in path_lower

        if is_gst:
            parsed = parse_gst_file(file_path)
            gst_totals["outward_supply"] += float(parsed.get("outward_supply", 0.0))
            gst_totals["inward_supply"] += float(parsed.get("inward_supply", 0.0))
            gst_totals["gstr2a_itc"] += float(parsed.get("gstr2a_itc", 0.0))
            gst_totals["gstr3b_itc"] += float(parsed.get("gstr3b_itc", 0.0))
            gst_totals["compliance_score"] += float(parsed.get("gst_compliance_score", 0.0))
            gst_totals["count"] += 1

        if is_bank:
            parsed = parse_bank_statement(file_path)
            bank_totals["total_credit"] += float(parsed.get("total_credit", 0.0))
            bank_totals["total_debit"] += float(parsed.get("total_debit", 0.0))
            bank_totals["net_cashflow"] += float(parsed.get("net_cashflow", 0.0))
            bank_totals["bounce_count"] += int(parsed.get("bounce_count", 0))
            bank_totals["count"] += 1

        if is_itr:
            parsed = parse_financial_document(file_path)
            itr_totals["revenue"] += float(parsed.get("revenue", 0.0))
            itr_totals["profit"] += float(parsed.get("profit", 0.0))
            itr_totals["debt"] += float(parsed.get("debt", 0.0))
            itr_totals["count"] += 1

    gst_compliance_score = gst_totals["compliance_score"] / gst_totals["count"] if gst_totals["count"] else 0.0

    gst_declared_revenue = gst_totals["outward_supply"]
    itr_declared_revenue = itr_totals["revenue"]
    bank_inflow = bank_totals["total_credit"]
    model_revenue = float(financial_metrics.get("revenue", 0.0))

    gst_itr_gap_pct = _pct_gap(gst_declared_revenue, itr_declared_revenue) if (gst_declared_revenue or itr_declared_revenue) else 0.0
    gst_bank_gap_pct = _pct_gap(gst_declared_revenue, bank_inflow) if (gst_declared_revenue or bank_inflow) else 0.0
    itr_model_gap_pct = _pct_gap(itr_declared_revenue, model_revenue) if (itr_declared_revenue or model_revenue) else 0.0

    circular_trading_risk = 0.0
    if gst_totals["outward_supply"] > 0:
        inward_ratio = gst_totals["inward_supply"] / max(gst_totals["outward_supply"], 1.0)
        if inward_ratio > 0.92 and bank_totals["net_cashflow"] < 0:
            circular_trading_risk = 72.0
        elif inward_ratio > 0.85:
            circular_trading_risk = 48.0

    debt = float(financial_metrics.get("total_debt", 0.0))
    assets = float(financial_metrics.get("total_assets", 0.0))
    revenue = float(financial_metrics.get("revenue", 0.0))
    net_profit = float(financial_metrics.get("net_profit", 0.0))
    ebitda = float(financial_metrics.get("ebitda", 0.0))

    equity_proxy = max(assets - debt, 1.0)
    liquidity_ratio = _safe_ratio(assets * 0.35, (debt * 0.55) + 1.0)
    solvency_ratio = _safe_ratio(assets, debt if debt else 1.0)
    leverage_ratio = _safe_ratio(debt, equity_proxy)
    profitability_ratio = _safe_ratio(net_profit, revenue if revenue else 1.0)
    net_margin = profitability_ratio * 100.0
    cash_flow_coverage = _safe_ratio(ebitda, debt if debt else 1.0)

    gstr_itc_mismatch_pct = _pct_gap(gst_totals["gstr2a_itc"], gst_totals["gstr3b_itc"]) if (gst_totals["gstr2a_itc"] or gst_totals["gstr3b_itc"]) else 0.0

    indian_context_checks = {
        "gstr_2a_vs_3b_mismatch_pct": round(gstr_itc_mismatch_pct, 2),
        "cibil_commercial_available": any("cibil" in str(item).lower() for item in primary_insights),
        "mca_filings_screened": any("mca" in str(item).lower() for item in primary_insights),
        "regulatory_watchlist_flags": [
            signal
            for signal in ["rbi", "nclt", "insolvency", "wilful default"]
            if any(signal in str(item).lower() for item in primary_insights)
        ],
    }

    discrepancy_flags: list[str] = []
    if gst_itr_gap_pct > 25:
        discrepancy_flags.append("Large GST vs ITR turnover variance")
    if gst_bank_gap_pct > 25:
        discrepancy_flags.append("GST sales not aligned with bank inflows")
    if itr_model_gap_pct > 30:
        discrepancy_flags.append("ITR revenue differs significantly from extracted statements")
    if bank_totals["bounce_count"] >= 2:
        discrepancy_flags.append("Repeated cheque/payment bounce signals in bank statements")
    if gstr_itc_mismatch_pct > 20:
        discrepancy_flags.append("GSTR-2A vs GSTR-3B ITC mismatch exceeds threshold")
    if circular_trading_risk > 60:
        discrepancy_flags.append("Possible circular trading pattern detected")

    penalty = 0.0
    penalty += min(gst_itr_gap_pct / 4.0, 12.0)
    penalty += min(gst_bank_gap_pct / 4.0, 12.0)
    penalty += min(circular_trading_risk / 20.0, 8.0)
    penalty += min(bank_totals["bounce_count"] * 1.5, 6.0)
    penalty += 4.0 if gstr_itc_mismatch_pct > 20 else 0.0

    return {
        "ratios": {
            "liquidity_ratio": round(liquidity_ratio, 3),
            "solvency_ratio": round(solvency_ratio, 3),
            "profitability_ratio": round(profitability_ratio, 3),
            "leverage_ratio": round(leverage_ratio, 3),
            "net_margin_pct": round(net_margin, 2),
            "cash_flow_coverage": round(cash_flow_coverage, 3),
        },
        "cross_verification": {
            "gst_declared_revenue": round(gst_declared_revenue, 2),
            "itr_declared_revenue": round(itr_declared_revenue, 2),
            "bank_total_credit": round(bank_inflow, 2),
            "model_extracted_revenue": round(model_revenue, 2),
            "gst_itr_gap_pct": round(gst_itr_gap_pct, 2),
            "gst_bank_gap_pct": round(gst_bank_gap_pct, 2),
            "itr_model_gap_pct": round(itr_model_gap_pct, 2),
            "circular_trading_risk": round(circular_trading_risk, 2),
            "gst_compliance_score": round(gst_compliance_score, 3),
            "bank_bounce_count": int(bank_totals["bounce_count"]),
        },
        "indian_context_checks": indian_context_checks,
        "discrepancy_flags": discrepancy_flags,
        "risk_penalty": round(penalty, 2),
    }
