from app.utils.pdf_loader import extract_text_from_pdf
from app.utils.docx_loader import extract_text_from_docx


def process_document(file_path: str, file_type: str):
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)

    elif file_type == "docx":
        return extract_text_from_docx(file_path)

    else:
        raise ValueError("Unsupported file type")