from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str


class RetrievedChunk(BaseModel):
    parent_id: int
    preview: str
    distance: Optional[float] = None   # make optional if not always present


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[RetrievedChunk]