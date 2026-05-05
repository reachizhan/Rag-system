from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.connection import init_db
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RAG System",
    lifespan=lifespan
)

# ---------------------------------------------------
# CORS Configuration
# ---------------------------------------------------
origins = [
    "http://localhost:3000",   # React / Next.js
    "http://127.0.0.1:3000",

    # If using Vite
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# Routes
# ---------------------------------------------------
app.include_router(api_router, prefix="/api")