from typing import List, Dict
import re
import numpy as np
from app.services.embedding_service import EmbeddingService


# ---------------------------------------------------
# 1. Section Header Detection (reuse yours)
# ---------------------------------------------------
def is_section_header(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    if re.match(r'^\d+(\.\d+)*\s+', line):
        return True

    if line.isupper() and len(line.split()) <= 10:
        return True

    if line.istitle() and len(line.split()) <= 10:
        return True

    return False


# ---------------------------------------------------
# 2. Extract sentences WITH offsets + section
# ---------------------------------------------------
def extract_sentences_with_metadata(text: str) -> List[Dict]:
    lines = text.split("\n")

    current_section = "Unknown"
    sentences = []

    cursor = 0  # track global position

    for line in lines:
        raw_line = line
        line = line.strip()

        if not line:
            cursor += len(raw_line) + 1
            continue

        # Detect section
        if is_section_header(line):
            current_section = line
            cursor += len(raw_line) + 1
            continue

        # Sentence splitting with offsets
        for match in re.finditer(r'[^.!?]+[.!?]?', raw_line):
            sent = match.group().strip()
            if not sent:
                continue

            start = cursor + match.start()
            end = cursor + match.end()

            sentences.append({
                "text": sent,
                "start": start,
                "end": end,
                "section": current_section
            })

        cursor += len(raw_line) + 1

    return sentences


# ---------------------------------------------------
# 3. Cosine similarity
# ---------------------------------------------------
def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ---------------------------------------------------
# 4. Semantic chunking
# ---------------------------------------------------
def semantic_chunking(
    sentences: List[Dict],
    similarity_threshold: float = 0.55,
    max_chunk_size: int = 10
) -> List[List[Dict]]:

    if not sentences:
        return []

    texts = [s["text"] for s in sentences]

    # 🚀 USE PARALLEL EMBEDDINGS
    embeddings = EmbeddingService.get_embeddings_parallel(
        texts,
        max_workers=5
    )

    chunks = []
    current_chunk = [sentences[0]]
    current_embeds = [embeddings[0]]

    for i in range(1, len(sentences)):

        # 🔥 BETTER SIMILARITY (compare with LAST sentence)
        sim = cosine_sim(current_embeds[-1], embeddings[i])

        # 🔥 IMPROVED SPLIT LOGIC
        should_split = False

        # 1. Semantic break
        if sim < similarity_threshold:
            should_split = True

        # 2. Size limit
        elif len(current_chunk) >= max_chunk_size:
            should_split = True

        # 3. Section change (SOFT condition)
        elif (
            sentences[i]["section"] != current_chunk[-1]["section"]
            and len(current_chunk) >= 3   # 👈 allow small variation
        ):
            should_split = True

        if should_split:
            chunks.append(current_chunk)
            current_chunk = []
            current_embeds = []

        current_chunk.append(sentences[i])
        current_embeds.append(embeddings[i])

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ---------------------------------------------------
# 5. Build final chunk objects
# ---------------------------------------------------
def build_chunks_from_semantic(chunks: List[List[Dict]]) -> List[Dict]:
    final_chunks = []

    for idx, chunk in enumerate(chunks):
        text = " ".join([s["text"] for s in chunk])

        final_chunks.append({
            "chunk_text": text,
            "char_start": chunk[0]["start"],
            "char_end": chunk[-1]["end"],
            "section": chunk[0]["section"],  # assume same section
            "chunk_index": idx
        })

    return final_chunks


# ---------------------------------------------------
# 6. MAIN PIPELINE
# ---------------------------------------------------
def process_pages(
    pages: List[Dict],
    document_id: int
) -> List[Dict]:

    all_sentences = []

    # 🔥 Merge all pages (cross-page semantic understanding)
    for page in pages:
        text = page.get("text", "")
        if not text.strip():
            continue

        sentences = extract_sentences_with_metadata(text)
        all_sentences.extend(sentences)

    # 🔥 Semantic chunking
    semantic_chunks: List[List[Dict]] = semantic_chunking(all_sentences)

    # 🔥 Build final chunks
    chunks = build_chunks_from_semantic(semantic_chunks)

    # 🔥 Attach document metadata
    for c in chunks:
        c["document_id"] = document_id
        c["page_number"] = None  # optional: improve later

    return chunks