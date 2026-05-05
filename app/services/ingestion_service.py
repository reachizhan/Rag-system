from app.db.connection import SessionLocal
from app.db.models import ParentChunk, Chunk

from app.services.chunking_service import process_pages
from app.services.embedding_service import EmbeddingService

import re


# ---------------------------------------------------
# Helper: Get ROOT section
# ---------------------------------------------------
def get_section_root(section: str):
    if not section:
        return "Unknown"

    match = re.match(r"^(\d+)", section.strip())

    if match:
        return match.group(1)

    return section.strip()


# ---------------------------------------------------
# Improved Parent Grouping
# ---------------------------------------------------
def build_parent_chunks(chunks, max_size=6, min_size=3):
    parents = []
    current_group = []

    current_root = get_section_root(chunks[0]["section"])

    for chunk in chunks:
        chunk_root = get_section_root(chunk["section"])

        should_split = False

        # Size-based split
        if len(current_group) >= max_size:
            should_split = True

        # Section split only if group is meaningful
        elif chunk_root != current_root and len(current_group) >= min_size:
            should_split = True

        if should_split:
            parents.append(current_group)
            current_group = []
            current_root = chunk_root

        current_group.append(chunk)

    if current_group:
        parents.append(current_group)

    return parents


# ---------------------------------------------------
# MAIN INGESTION
# ---------------------------------------------------
def ingest_document(pages: list, document_id: int):
    db = SessionLocal()

    try:
        print("\n🚀 STARTING INGESTION")

        # 1. Chunking
        chunks = process_pages(pages, document_id)

        print("Total chunks:", len(chunks))

        # 2. Parent grouping
        parent_groups = build_parent_chunks(chunks)

        print("Total parent groups:", len(parent_groups))

        # ---------------------------------------------------
        # 3. Process each parent group
        # ---------------------------------------------------
        for i, group in enumerate(parent_groups):

            print(f"\n🔥 Parent {i+1} | size={len(group)}")

            # Create parent
            parent_text = " ".join([c["chunk_text"] for c in group])

            parent = ParentChunk(
                document_id=document_id,
                parent_text=parent_text
            )

            db.add(parent)
            db.flush()

            # 🚀 PARALLEL EMBEDDINGS (PER GROUP)
            texts = [c["chunk_text"] for c in group]

            embeddings = EmbeddingService.get_embeddings_parallel(
                texts,
                max_workers=5  # 🔥 adjust if needed
            )

            # Insert children
            for chunk, embedding in zip(group, embeddings):

                db_chunk = Chunk(
                    document_id=document_id,
                    chunk_text=chunk["chunk_text"],
                    embedding=embedding,
                    chunk_index=chunk["chunk_index"],
                    char_start=chunk["char_start"],
                    char_end=chunk["char_end"],
                    page_number=chunk.get("page_number"),
                    parent_id=parent.id
                )

                db.add(db_chunk)

                print(f"   ➜ child {chunk['chunk_index']} stored")

        db.commit()

        print("\n✅ INGESTION COMPLETE")

    except Exception as e:
        db.rollback()
        print("❌ ERROR:", str(e))
        raise

    finally:
        db.close()