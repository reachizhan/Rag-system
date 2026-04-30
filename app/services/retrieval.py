from sqlalchemy import text
from app.services.embedding_service import EmbeddingService
from app.db.connection import SessionLocal


def retrieve_chunks(query: str, top_k: int = 5):
    db = SessionLocal()

    try:
        # ✅ Correct embedding call
        query_embedding = EmbeddingService.get_embedding(query)

        # ✅ SQLAlchemy-safe query
        sql = text("""
            SELECT chunk_text, embedding <-> CAST(:embedding AS vector) AS distance
            FROM chunks
             ORDER BY embedding <-> CAST(:embedding AS vector)
            LIMIT :limit
        """)

        results = db.execute(
            sql,
            {
                "embedding": query_embedding,
                "limit": top_k
            }
        ).fetchall()

        formatted = []

        for row in results:
            chunk_text = row[0]
            distance = row[1]

            score = 1 / (1 + distance)

            formatted.append({
                "chunk_text": chunk_text,
                "score": score
            })

        return formatted

    finally:
        db.close()