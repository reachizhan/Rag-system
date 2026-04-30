from fastapi import APIRouter
from app.db.schemas import QueryRequest, QueryResponse
from app.services.retrieval import retrieve_chunks

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query_docs(request: QueryRequest):
    
    results = retrieve_chunks(request.query)

    return {
        "query": request.query,
        "results": results
    }