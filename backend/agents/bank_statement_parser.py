import re
from pathlib import Path

from ..utils.pdf_parser import extract_text_from_pdf


def parse_bank_statement(file_path):
    """Extract simple cashflow metrics from bank statements."""
    text = extract_text_from_pdf(file_path) if Path(file_path).suffix.lower() == ".pdf" else ""

    credit_values = [float(x.replace(",", "")) for x in re.findall(r"credit[^\d]*(\d+[\d,]*\.?\d*)", text, flags=re.I)]
    debit_values = [float(x.replace(",", "")) for x in re.findall(r"debit[^\d]*(\d+[\d,]*\.?\d*)", text, flags=re.I)]

    total_credit = sum(credit_values)
    total_debit = sum(debit_values)
    net_cashflow = total_credit - total_debit

    bounce_count = len(re.findall(r"bounced|dishonou?red|return", text, flags=re.I))

    return {
        "total_credit": round(total_credit, 2),
        "total_debit": round(total_debit, 2),
        "net_cashflow": round(net_cashflow, 2),
        "bounce_count": bounce_count,
    }
