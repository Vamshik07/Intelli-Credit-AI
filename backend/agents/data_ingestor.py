try:
    # Package mode: imported via `backend.agents...`.
    from ..utils.pdf_parser import extract_text_from_pdf
except ImportError:
    # Script mode: imported via `agents...` when running from backend/.
    from utils.pdf_parser import extract_text_from_pdf


def ingest_documents(file_paths):
    documents = []

    for file in file_paths:
        text = extract_text_from_pdf(file)

        documents.append({
            "file": file,
            "content": text
        })

    return documents
