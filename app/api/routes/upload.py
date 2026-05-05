from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

from app.services.document_service import process_document
from app.services.db_service import DBService
from app.services.ingestion_service import ingest_document

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):

    # ---------------------------------------------------
    # 1. Validate file
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
    # 3. Extract text
    # ---------------------------------------------------
    pages = process_document(file_path, file_ext)

    if not pages:
        raise HTTPException(status_code=500, detail="Failed to extract document text")

    # ---------------------------------------------------
    # 4. Store document metadata
    # ---------------------------------------------------
    try:
        document_id = DBService.insert_document(
            filename=filename,
            file_type=file_ext
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document insert failed: {str(e)}"
        )

    # ---------------------------------------------------
    # 5. FULL INGESTION PIPELINE (NEW CORE SYSTEM)
    # ---------------------------------------------------
    try:
        ingest_document(
            pages=pages,
            document_id=document_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )

    # ---------------------------------------------------
    # 6. Response
    # ---------------------------------------------------
    return {
        "message": "Document processed successfully",
        "document_id": document_id,
        "filename": filename,
        "file_type": file_ext,
        "pages_extracted": len(pages)
    }