from fastapi import APIRouter

from app.api.routes.upload import router as upload_router
from app.api.routes.query import router as query_router
from app.api.routes.documents import router as documents_router

api_router = APIRouter()

api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
api_router.include_router(query_router, prefix="/query", tags=["Query"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])