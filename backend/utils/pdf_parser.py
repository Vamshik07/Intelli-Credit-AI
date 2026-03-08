from __future__ import annotations

from pypdf import PdfReader

from .pdf_utils import extract_pdf_text


def _extract_with_pypdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF with multiple fallbacks for scanned/complex files."""
    text = ""

    try:
        text = _extract_with_pypdf(file_path)
    except Exception:
        text = ""

    if text.strip():
        return text

    try:
        text = extract_pdf_text(file_path)
    except Exception:
        text = ""

    return text