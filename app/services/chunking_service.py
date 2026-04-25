from typing import List, Dict
from transformers import AutoTokenizer
import re

# ---------------------------------------------------
# Tokenizer (global init)
# ---------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")


# ---------------------------------------------------
# 1. Section Header Detection (NEW)
# ---------------------------------------------------
def is_section_header(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    # 1. Numbered headings (e.g., 1.2.3 Heading)
    if re.match(r'^\d+(\.\d+)*\s+', line):
        return True

    # 2. ALL CAPS headings
    if line.isupper() and len(line.split()) <= 10:
        return True

    # 3. Title Case headings
    if line.istitle() and len(line.split()) <= 10:
        return True

    return False


# ---------------------------------------------------
# 2. Split text into structured paragraphs
# ---------------------------------------------------
def split_into_paragraphs(text: str) -> List[str]:
    lines = text.split("\n")
    paragraphs = []
    buffer = []

    for line in lines:
        line = line.strip()

        if not line:
            if buffer:
                paragraphs.append("\n".join(buffer))
                buffer = []
            continue

        # 🔥 NEW: force split on headings
        if is_section_header(line):
            if buffer:
                paragraphs.append("\n".join(buffer))
                buffer = []
            paragraphs.append(line)
            continue

        buffer.append(line)

    if buffer:
        paragraphs.append("\n".join(buffer))

    return paragraphs


# ---------------------------------------------------
# 3. Token counter
# ---------------------------------------------------
def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


# ---------------------------------------------------
# 4. Split oversized paragraphs (sentence-based)
# ---------------------------------------------------
def split_large_paragraph(text: str, token_limit: int) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        if current_tokens + sentence_tokens > token_limit:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_tokens = 0

        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks


# ---------------------------------------------------
# 5. Build chunks with overlap
# ---------------------------------------------------
def build_chunks(
    paragraphs: List[str],
    token_limit: int = 400,
    overlap: int = 80
) -> List[str]:

    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = count_tokens(para)

        # ---------------------------------------------------
        # FIX 1: Oversized paragraph handling
        # ---------------------------------------------------
        if para_tokens > token_limit:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_tokens = 0

            sub_chunks = split_large_paragraph(para, token_limit)
            chunks.extend(sub_chunks)
            continue

        # ---------------------------------------------------
        # Normal chunk boundary check
        # ---------------------------------------------------
        if current_tokens + para_tokens > token_limit:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

                # overlap handling
                overlap_paras = []
                overlap_tokens = 0

                for p in reversed(current_chunk):
                    t = count_tokens(p)
                    if overlap_tokens + t > overlap:
                        break
                    overlap_paras.insert(0, p)
                    overlap_tokens += t

                current_chunk = overlap_paras
                current_tokens = overlap_tokens

        current_chunk.append(para)
        current_tokens += para_tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


# ---------------------------------------------------
# 6. Main pipeline (with cross-page support)
# ---------------------------------------------------
def process_pages(
    pages: List[Dict],
    document_id: int,
    token_limit: int = 400,
    overlap: int = 80,
    cross_page_boundary: bool = True
) -> List[Dict]:

    all_chunks = []
    chunk_index = 0

    # ---------------------------------------------------
    # Cross-page chunking mode
    # ---------------------------------------------------
    if cross_page_boundary:
        paragraphs = []

        for page in pages:
            text = page.get("text", "")
            if not text.strip():
                continue

            page_paragraphs = split_into_paragraphs(text)
            paragraphs.extend(page_paragraphs)

        chunks = build_chunks(paragraphs, token_limit, overlap)

        for chunk in chunks:
            all_chunks.append({
                "document_id": document_id,
                "chunk_text": chunk,
                "chunk_index": chunk_index,
                "page_number": None,  # mixed pages
                "char_start": None,
                "char_end": None
            })
            chunk_index += 1

        return all_chunks

    # ---------------------------------------------------
    # Page-by-page fallback
    # ---------------------------------------------------
    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text", "")

        if not text.strip():
            continue

        paragraphs = split_into_paragraphs(text)
        chunks = build_chunks(paragraphs, token_limit, overlap)

        for chunk in chunks:
            all_chunks.append({
                "document_id": document_id,
                "chunk_text": chunk,
                "chunk_index": chunk_index,
                "page_number": page_number,
                "char_start": None,
                "char_end": None
            })
            chunk_index += 1

    return all_chunks