import psycopg2
from pgvector.psycopg2 import register_vector

DB_CONFIG = {
    "dbname": "ragdb",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}


class DBService:

    @staticmethod
    def get_connection():
        conn = psycopg2.connect(**DB_CONFIG)  # type:ignore
        register_vector(conn)  
        return conn

    # -----------------------------
    # 1. Insert Document
    # -----------------------------
    @staticmethod
    def insert_document(filename: str, file_type: str):
        conn = DBService.get_connection()
        cur = conn.cursor()

        query = """
        INSERT INTO documents (filename, file_type)
        VALUES (%s, %s)
        RETURNING id;
        """

        cur.execute(query, (filename, file_type))
        document_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return document_id

    # -----------------------------
    # 2. Insert Chunks (BATCH)
    # -----------------------------
    @staticmethod
    def insert_chunks(document_id: int, chunks: list):
        conn = DBService.get_connection()
        cur = conn.cursor()

        query = """
        INSERT INTO chunks (
            document_id,
            chunk_text,
            embedding,
            chunk_index,
            page_number,
            char_start,
            char_end
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        data = []

        for chunk in chunks:
            data.append((
                document_id,
                chunk["chunk_text"],
                chunk["embedding"],  # ✅ list → vector works after register_vector
                chunk["chunk_index"],
                chunk["page_number"],
                chunk["char_start"],
                chunk["char_end"]
            ))

        cur.executemany(query, data)

        conn.commit()
        cur.close()
        conn.close()