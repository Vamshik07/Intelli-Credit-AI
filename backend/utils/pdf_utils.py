from pathlib import Path

import fitz
import pdfplumber


def extract_pdf_text(file_path: str) -> str:
    text_chunks: list[str] = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or "")

    if "".join(text_chunks).strip():
        return "\n".join(text_chunks)

    # Fallback to PyMuPDF extraction for difficult PDFs.
    doc = fitz.open(file_path)
    try:
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()


def is_scanned_pdf(file_path: str) -> bool:
    # Heuristic: if parsed text is too short, treat as scanned.
    text = extract_pdf_text(file_path)
    return len(text.strip()) < 40


def ensure_folder(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
