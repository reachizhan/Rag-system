from fastapi import APIRouter
from app.db.schemas import QueryRequest, QueryResponse
from app.services.retrieval import retrieve_chunks
from app.services.context_builder import build_context
from app.services.prompt_constructor import build_prompt
from app.services.llm_service import generate_answer

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_docs(request: QueryRequest):

    # ---------------------------------------------------
    # 1. Retrieve (child + parent-aware)
    # ---------------------------------------------------
    results = retrieve_chunks(request.query)

    # ---------------------------------------------------
    # 2. Build context (PARENT-LEVEL)
    # ---------------------------------------------------
    context = build_context(results, max_parents=3)

    # ---------------------------------------------------
    # 3. Build prompt
    # ---------------------------------------------------
    prompt = build_prompt(context, request.query)

    # ---------------------------------------------------
    # 4. Generate answer
    # ---------------------------------------------------
    answer = generate_answer(prompt)

    # ---------------------------------------------------
    # 5. Build CLEAN sources (parent-level)
    # ---------------------------------------------------
    seen = set()
    sources = []

    for r in results:
        pid = r["parent_id"]

        if pid in seen:
            continue

        if not r["parent_text"]:
            continue

        seen.add(pid)

        sources.append({
            "parent_id": pid,
            "parent_text": r["parent_text"],       # 🔥 FULL CONTEXT
            "preview": r["parent_text"][:300]      # 🔥 SHORT PREVIEW
        })

        if len(sources) >= 3:
            break

    # ---------------------------------------------------
    # 6. Final response
    # ---------------------------------------------------
    return {
        "query": request.query,
        "answer": answer,
        "sources": sources
    }