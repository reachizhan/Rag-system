from sqlalchemy import text
from app.services.embedding_service import EmbeddingService
from app.db.connection import SessionLocal


def retrieve_chunks(query: str, top_k: int = 10):
    db = SessionLocal()

    try:
        # ---------------------------------------------------
        # 1. Query embedding
        # ---------------------------------------------------
        query_embedding = EmbeddingService.get_embedding(query)

        # ---------------------------------------------------
        # 2. Retrieve CHILD chunks (with parent_id)
        # ---------------------------------------------------
        sql = text("""
            SELECT 
                id,
                chunk_text,
                parent_id,
                embedding <=> CAST(:embedding AS vector) AS distance
            FROM chunks
            ORDER BY distance
            LIMIT :limit
        """)

        results = db.execute(
            sql,
            {
                "embedding": query_embedding,
                "limit": top_k
            }
        ).fetchall()

        # ---------------------------------------------------
        # 3. Collect parent IDs
        # ---------------------------------------------------
        parent_ids = list(set([row[2] for row in results if row[2] is not None]))

        # ---------------------------------------------------
        # 4. Fetch PARENT chunks
        # ---------------------------------------------------
        parent_sql = text("""
            SELECT id, parent_text
            FROM parent_chunks
            WHERE id = ANY(:ids)
        """)

        parents = db.execute(
            parent_sql,
            {"ids": parent_ids}
        ).fetchall()

        parent_map = {p[0]: p[1] for p in parents}

        # ---------------------------------------------------
        # 5. Format response
        # ---------------------------------------------------
        formatted = []

        for row in results:
            chunk_id = row[0]
            chunk_text = row[1]
            parent_id = row[2]
            distance = float(row[3])

            # 🔥 FILTER HERE
            if distance < 0.5:
                formatted.append({
                    "chunk_id": chunk_id,
                    "chunk_text": chunk_text,
                    "parent_id": parent_id,
                    "parent_text": parent_map.get(parent_id, ""),
                    "distance": distance
                })

        if not formatted:
            # fallback → return top 1 result anyway
            row = results[0]

            formatted.append({
                "chunk_id": row[0],
                "chunk_text": row[1],
                "parent_id": row[2],
                "parent_text": parent_map.get(row[2], ""),
                "distance": float(row[3])
            })
        
        
        return formatted

    finally:
        db.close()