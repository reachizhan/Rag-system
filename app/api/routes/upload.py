from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

from app.services.document_service import process_document
from app.services.chunking_service import process_pages
from app.services.embedding_service import EmbeddingService


router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # ---------------------------------------------------
    # 1. Validate file type
    # ---------------------------------------------------
    filename = file.filename

    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = filename.split(".")[-1].lower()

    if file_ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")

    # ---------------------------------------------------
    # 2. Save file locally
    # ---------------------------------------------------
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ---------------------------------------------------
    # 3. Extract text (page-wise)
    # ---------------------------------------------------
    pages = process_document(file_path, file_ext)

    if not pages:
        raise HTTPException(status_code=500, detail="Failed to extract document text")

    # ---------------------------------------------------
    # 4. Chunking step (NEW)
    # ---------------------------------------------------
    # document_id = None  # temporary (will come from DB later)

    chunks = process_pages(
        pages=pages,
        document_id=1 , # for testing
        token_limit=400,
        overlap=80
    )
    
    
    # ---------------------------------------------------
    # 5. Embedding step (NEW)
    # ---------------------------------------------------
    chunk_texts = [chunk["chunk_text"] for chunk in chunks]

    embeddings = EmbeddingService.get_embeddings_batch(
        chunk_texts,
        batch_size=10
)    
    # Attach embeddings back to chunks
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i]
    print("Embedding length:", len(chunks[0]["embedding"]))    

    # ---------------------------------------------------
    # 6. Response (preview only for now)
    # ---------------------------------------------------
    return {
        "filename": filename,
        "file_type": file_ext,
        "pages_extracted": len(pages),
        "chunks_created": len(chunks),
        "preview_pages": pages[:1],
        "preview_chunks": [
    {
        "chunk_text": c["chunk_text"],
        "chunk_index": c["chunk_index"]
    }
    for c in chunks[10:20]
]
    }