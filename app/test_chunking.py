from services.chunking_service import process_pages

pages = [
    {
        "page_number": 1,
        "text": """This is paragraph one.

This is paragraph two with more content to simulate chunking.

This is paragraph three.

This is paragraph four."""
    }
]

chunks = process_pages(pages, document_id=1)

for c in chunks:
    print("---- CHUNK ----")
    print(c["chunk_text"])
    print("Page:", c["page_number"])
    print("Index:", c["chunk_index"])
    print()