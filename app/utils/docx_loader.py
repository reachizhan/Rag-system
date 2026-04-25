from docx import Document
import re

def clean_text(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def extract_text_from_docx(file_path: str):
    doc = Document(file_path)

    paragraphs = [
        clean_text(p.text)
        for p in doc.paragraphs
        if p.text.strip()
    ]

    return [{
        "page_number": 1,
        "text": "\n\n".join(paragraphs)  # preserve structure
    }]