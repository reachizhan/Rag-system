#  RAG System Backend
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-00a393.svg)
![pgvector](https://img.shields.io/badge/pgvector-Supported-336791.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
**A high-performance, fully localized Retrieval-Augmented Generation (RAG) system implementing advanced semantic chunking and parent-child retrieval.**
## Why this project?
Standard RAG systems often struggle with a critical tradeoff: small chunks provide accurate search results but lack enough context for the LLM to generate good answers, while large chunks provide great context but ruin search accuracy. This project solves that problem by implementing **Parent-Child Retrieval** and **Semantic Chunking**—ensuring you find the exact needle in the haystack while still feeding the LLM the entire haystack for context.
## Key Features
- **Intelligent Document Ingestion:** Supports automated text extraction from both PDF and DOCX files.
- **Semantic Chunking:** Splits documents based on sentence embeddings and cosine similarity to ensure chunks retain semantic meaning rather than relying on arbitrary character limits.
- **Parent-Child Retrieval Strategy:** Stores granular child chunks for highly precise vector search, while retrieving larger parent chunks to provide the LLM with sufficient surrounding context.
- **Query Expansion:** Utilizes an LLM to automatically expand and rewrite user queries, bridging vocabulary gaps for improved semantic matching.
- **Parallel Processing:** Leverages concurrent execution for embedding generation to significantly accelerate the ingestion pipeline.
- **Fully Local AI Pipeline:** Operates entirely on locally hosted models via Ollama, ensuring data privacy and removing reliance on external APIs.
## Tech Stack
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Vector Extension:** `pgvector`
- **ORM:** SQLAlchemy (with `pgvector.sqlalchemy`)
- **AI/LLM Provider:** Ollama (Local)
  - **Embedding Model:** `nomic-embed-text`
  - **Generation Model:** `llama3.1:8b`
- **Containerization:** Docker & Docker Compose
## System Architecture
The system pipeline flows through two primary phases: Ingestion and Retrieval.
1. **Ingestion Pipeline:**
   - **Upload & Extract:** Documents (PDF/DOCX) are uploaded and text is extracted.
   - **Semantic Splitting:** Text is divided into sentences with exact character offsets.
   - **Embedding Generation:** Sentences are embedded in parallel using `nomic-embed-text`.
   - **Chunk Aggregation:** Sentences are grouped into *Child Chunks* using cosine similarity. These are further aggregated into larger *Parent Chunks* based on section headers and size thresholds.
   - **Storage:** Both chunk layers are persisted to PostgreSQL, with child chunks indexed via `pgvector` for vector similarity search.
2. **Query Pipeline:**
   - **Query Expansion:** The user's query is rewritten into multiple search-friendly variations using the LLM.
   - **Vector Search:** The query variations are embedded and searched against the highly specific child chunks using cosine distance (`<=>`).
   - **Context Construction:** The system retrieves the broader *Parent Chunks* associated with the matching child chunks.
   - **Response Generation:** The parent chunk text is injected into the prompt context, and `llama3.1:8b` generates the final synthesized answer.
## Installation & Setup
### 1. Prerequisites
- Python 3.10+
- Docker and Docker Compose
- [Ollama](https://ollama.com/) installed and running locally
### 2. Prepare Local Models
Ensure Ollama is running (`ollama serve`), then pull the required models:
```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```
### 3. Database Configuration
Start the PostgreSQL database with the `pgvector` extension using Docker Compose:
```bash
docker-compose up -d
```
This will spin up a local database accessible on port `5432` with the credentials defined in the `docker-compose.yml`.
### 4. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
## Configuration
Best practice is to use an environment variable file for configuration. Copy the provided `.env.example` file to create your own `.env` file:
```bash
cp .env.example .env
```
Even if your configuration is minimal, this ensures your secrets and environment-specific settings are not checked into version control.
The database connection string is built around the parameters set in the `docker-compose.yml`. If running the default setup, no extra configuration is needed.
If modifying, ensure the following environment or config variables align with your PostgreSQL instance:
- `POSTGRES_USER`: postgres
- `POSTGRES_PASSWORD`: postgres
- `POSTGRES_DB`: ragdb
- `OLLAMA_URL`: `http://localhost:11434` (default Ollama port)
## Usage
### Running the Server
Start the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --reload
```
### Interacting with the API
Once running, the API is accessible at `http://127.0.0.1:8000`. FastAPI provides auto-generated interactive documentation.
- **Swagger UI:** Navigate to `http://127.0.0.1:8000/docs` to test endpoints directly from the browser.
**Core Endpoints:**
- `POST /api/upload`: Upload a PDF or DOCX file for ingestion and vectorization.
- `POST /api/query`: Submit a JSON payload `{"query": "your question here"}` to search the knowledge base and generate an answer.
- `GET /api/documents`: List all ingested documents.
- `DELETE /api/documents/{id}`: Remove a document and cascade delete its chunks.