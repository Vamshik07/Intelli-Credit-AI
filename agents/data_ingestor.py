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