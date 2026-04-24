from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
  
    init_db()
    yield

app = FastAPI(
    title="RAG System",
    lifespan=lifespan
)

@app.get("/")
def health_check():
    return {"status": "RAG system is running"}