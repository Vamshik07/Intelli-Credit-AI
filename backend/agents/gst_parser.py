import re
from pathlib import Path

from ..utils.pdf_parser import extract_text_from_pdf


def parse_gst_file(file_path):
    """Extract broad GST indicators from a GST-related document."""
    text = extract_text_from_pdf(file_path) if Path(file_path).suffix.lower() == ".pdf" else ""

    outward_matches = re.findall(r"outward\s+suppl(?:y|ies)[^\d]*(\d+[\d,]*)", text, flags=re.I)
    inward_matches = re.findall(r"inward\s+suppl(?:y|ies)[^\d]*(\d+[\d,]*)", text, flags=re.I)
    gstr2a_itc_matches = re.findall(r"gstr[-\s]*2a[^\d]*(\d+[\d,]*\.?\d*)", text, flags=re.I)
    gstr3b_itc_matches = re.findall(r"gstr[-\s]*3b[^\d]*(\d+[\d,]*\.?\d*)", text, flags=re.I)

    def to_number(values):
        if not values:
            return 0.0
        normalized = values[0].replace(",", "")
        try:
            return float(normalized)
        except ValueError:
            return 0.0

    outward_supply = to_number(outward_matches)
    inward_supply = to_number(inward_matches)
    gstr2a_itc = to_number(gstr2a_itc_matches)
    gstr3b_itc = to_number(gstr3b_itc_matches)

    gst_compliance_score = 0.8
    if outward_supply == 0 and inward_supply == 0:
        gst_compliance_score = 0.5
    elif gstr2a_itc and gstr3b_itc:
        mismatch = abs(gstr2a_itc - gstr3b_itc) / max(gstr2a_itc, gstr3b_itc, 1.0)
        if mismatch > 0.25:
            gst_compliance_score = 0.45
        elif mismatch > 0.1:
            gst_compliance_score = 0.65

    return {
        "outward_supply": outward_supply,
        "inward_supply": inward_supply,
        "gstr2a_itc": gstr2a_itc,
        "gstr3b_itc": gstr3b_itc,
        "gst_compliance_score": gst_compliance_score,
    }
