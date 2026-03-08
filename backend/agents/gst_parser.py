import re
from pathlib import Path

from ..utils.pdf_parser import extract_text_from_pdf


def parse_gst_file(file_path):
    """Extract broad GST indicators from a GST-related document."""
    text = extract_text_from_pdf(file_path) if Path(file_path).suffix.lower() == ".pdf" else ""

    outward_matches = re.findall(r"outward\s+suppl(?:y|ies)[^\d]*(\d+[\d,]*)", text, flags=re.I)
    inward_matches = re.findall(r"inward\s+suppl(?:y|ies)[^\d]*(\d+[\d,]*)", text, flags=re.I)

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

    gst_compliance_score = 0.8
    if outward_supply == 0 and inward_supply == 0:
        gst_compliance_score = 0.5

    return {
        "outward_supply": outward_supply,
        "inward_supply": inward_supply,
        "gst_compliance_score": gst_compliance_score,
    }
