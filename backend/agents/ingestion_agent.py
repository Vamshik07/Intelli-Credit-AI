from pathlib import Path

from backend.utils.pdf_utils import ensure_folder


def run_ingestion_agent(state: dict) -> dict:
    documents = state.get("documents", [])
    ensure_folder("backend/uploads")

    normalized_docs = []
    for doc in documents:
        path = doc.get("file_path", "")
        if path and Path(path).exists():
            normalized_docs.append(doc)

    return {"documents": normalized_docs}
