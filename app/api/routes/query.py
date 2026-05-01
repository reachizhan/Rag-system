from fastapi import APIRouter
from app.db.schemas import QueryRequest, QueryResponse
from app.services.retrieval import retrieve_chunks
from app.services.context_builder import build_context
from app.services.prompt_constructor import build_prompt
from app.services.llm_service import generate_answer

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query_docs(request: QueryRequest):
    
    results = retrieve_chunks(request.query)
    context = build_context(results, max_chunks=5)
    prompt = build_prompt(context, request.query)
    answer = generate_answer(prompt)

    return {
        "query": request.query,
        "answer": answer,
        "sources": results
    }