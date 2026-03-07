from pypdf import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text

    return text