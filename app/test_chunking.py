from app.services.chunking_service import process_pages


def test_chunking():
    # ---------------------------------------------------
    # Sample document (simulate real PDF text)
    # ---------------------------------------------------
    sample_text = """
1. Introduction
This system is designed to improve retrieval quality.
It uses embeddings and semantic search.

2. Methodology
We apply chunking techniques to split documents.
The system uses cosine similarity to group sentences.
This improves coherence of chunks.

3. Results
The results show significant improvement.
Retrieval accuracy increased by 30%.
The system performs better than baseline methods.

4. Conclusion
Semantic chunking improves overall system performance.
Future work includes optimizing retrieval.
"""

    pages = [
        {
            "page_number": 1,
            "text": sample_text
        }
    ]

    # ---------------------------------------------------
    # Run chunking
    # ---------------------------------------------------
    chunks = process_pages(pages, document_id=1)

    # ---------------------------------------------------
    # Debug Output
    # ---------------------------------------------------
    print("\n" + "="*60)
    print("TOTAL CHUNKS:", len(chunks))
    print("="*60)

    for i, chunk in enumerate(chunks):
        print(f"\n🔹 Chunk {i}")
        print("-"*50)
        print("Section     :", chunk.get("section"))
        print("Char Range  :", chunk.get("char_start"), "→", chunk.get("char_end"))
        print("Text        :", chunk.get("chunk_text"))

    # ---------------------------------------------------
    # Validation Checks
    # ---------------------------------------------------
    print("\n" + "="*60)
    print("RUNNING VALIDATION CHECKS")
    print("="*60)

    for i, chunk in enumerate(chunks):
        assert chunk["chunk_text"], f"Chunk {i} has empty text"
        assert chunk["char_start"] is not None, f"Chunk {i} missing char_start"
        assert chunk["char_end"] is not None, f"Chunk {i} missing char_end"
        assert chunk["char_start"] < chunk["char_end"], f"Chunk {i} invalid offsets"
        assert chunk["section"] is not None, f"Chunk {i} missing section"

    print("✅ All validation checks passed!")


if __name__ == "__main__":
    test_chunking()