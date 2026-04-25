from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

from app.services.document_service import process_document

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # 1. Validate file type
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = filename.split(".")[-1].lower()

    if file_ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")

    # 2. Save file locally
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Process document (extraction happens inside service layer)
    pages = process_document(file_path, file_ext)

    # 4. Return response (for now preview only)
    return {
        "filename": filename,
        "file_type": file_ext,
        "pages_extracted": len(pages),
        "preview": pages[:1]
    }