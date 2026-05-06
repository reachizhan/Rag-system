from pydantic import BaseModel
from typing import List


class QueryRequest(BaseModel):
    query: str


class Source(BaseModel):
    parent_id: int
    parent_text: str
    preview: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Source]