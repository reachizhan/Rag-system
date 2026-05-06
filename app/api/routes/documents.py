from fastapi import APIRouter ,HTTPException
from app.db.connection import SessionLocal
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def get_documents():
    db = SessionLocal()

    try:
        result = db.execute(text("""
            SELECT id, filename, file_type, created_at
            FROM documents
            ORDER BY created_at DESC
        """)).fetchall()

        documents = [
            {
                "id": row[0],
                "filename": row[1],
                "file_type": row[2],
                "created_at": row[3]
            }
            for row in result
        ]

        return {
            "documents": documents,
            "count": len(documents)
        }

    finally:
        db.close()
        
@router.delete("/{document_id}")
def delete_document(document_id: int):
    db = SessionLocal()

    try:
        # ---------------------------------------------------
        # 1. Check if document exists
        # ---------------------------------------------------
        doc = db.execute(
            text("SELECT id FROM documents WHERE id = :id"),
            {"id": document_id}
        ).fetchone()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # ---------------------------------------------------
        # 2. Delete document (CASCADE will handle rest)
        # ---------------------------------------------------
        db.execute(
            text("DELETE FROM documents WHERE id = :id"),
            {"id": document_id}
        )

        db.commit()

        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()