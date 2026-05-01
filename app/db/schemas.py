from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    query: str

class RetrievedChunk(BaseModel):
    chunk_text: str
    score: float

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[RetrievedChunk]