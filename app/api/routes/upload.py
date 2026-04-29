from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

from app.services.document_service import process_document
from app.services.chunking_service import process_pages
from app.services.embedding_service import EmbeddingService
from app.services.db_service import DBService 

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
    # 4. Insert document into DB ✅
    # ---------------------------------------------------
    try:
        document_id = DBService.insert_document(
            filename=filename,
            file_type=file_ext
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document insert failed: {str(e)}")

    # ---------------------------------------------------
    # 5. Chunking step
    # ---------------------------------------------------
    chunks = process_pages(
        pages=pages,
        document_id=document_id, 
        token_limit=400,
        overlap=80
    )

    if not chunks:
        raise HTTPException(status_code=500, detail="Chunking failed")

    # ---------------------------------------------------
    # 6. Embedding step
    # ---------------------------------------------------
    chunk_texts = [chunk["chunk_text"] for chunk in chunks]

    embeddings = EmbeddingService.get_embeddings_batch(
        chunk_texts,
        batch_size=10
    )

    # Attach embeddings back to chunks
    for i, chunk in enumerate(chunks):
        embedding = embeddings[i]

        # ✅ Safety check (avoid dimension issues)
        if len(embedding) != 768:
            raise HTTPException(
                status_code=500,
                detail=f"Embedding dimension mismatch at chunk {i}"
            )

        chunk["embedding"] = embedding

    print("Embedding length:", len(chunks[0]["embedding"]))

    # ---------------------------------------------------
    # 7. Insert chunks into DB ✅
    # ---------------------------------------------------
    try:
        DBService.insert_chunks(document_id, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunk insert failed: {str(e)}")

    # ---------------------------------------------------
    # 8. Response
    # ---------------------------------------------------
    return {
        "message": "Document processed and stored successfully",
        "document_id": document_id,
        "filename": filename,
        "file_type": file_ext,
        "pages_extracted": len(pages),
        "chunks_created": len(chunks),
        "preview_chunks": [
            {
                "chunk_text": c["chunk_text"],
                "chunk_index": c["chunk_index"]
            }
            for c in chunks[:5]
        ]
    }