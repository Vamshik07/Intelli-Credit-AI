from ..utils.pdf_parser import extract_text_from_pdf
from .bank_statement_parser import parse_bank_statement
from .financial_doc_parser import parse_financial_document
from .gst_parser import parse_gst_file
from .pdf_risk_signals import detect_pdf_risk_signals


def ingest_documents(file_paths):
    documents = []

    for file in file_paths:
        text = extract_text_from_pdf(file)

        lower_name = file.lower()
        gst_data = parse_gst_file(file) if "gst" in lower_name else {}
        bank_data = parse_bank_statement(file) if "bank" in lower_name or "statement" in lower_name else {}
        financial_data = parse_financial_document(file)
        doc_risk = detect_pdf_risk_signals(file)

        documents.append({
            "file": file,
            "content": text,
            "gst_data": gst_data,
            "bank_data": bank_data,
            "financial_data": financial_data,
            "document_risk": doc_risk,
        })

    return documents
