import pdfplumber
import re

def clean_text(text: str) -> str:
    # Normalize line breaks first
    text = text.replace('\r', '\n')

    # Keep paragraph breaks (double newline)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Replace multiple spaces/tabs (but NOT newlines)
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


def extract_text_from_pdf(file_path: str):
    pages_data = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text:
                pages_data.append({
                    "page_number": i + 1,
                    "text": clean_text(text)
                })

    return pages_data