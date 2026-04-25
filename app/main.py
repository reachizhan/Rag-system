from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.connection import init_db

# 👇 import aggregated router
from app.api.routes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="RAG System",
    lifespan=lifespan
)

# 👇 plug all routes here
app.include_router(api_router, prefix="/api")