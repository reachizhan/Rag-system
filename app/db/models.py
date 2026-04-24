from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship, declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

# -------------------------
# Documents Table
# -------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # delete chunks if document is deleted
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete"
    )


# -------------------------
# Chunks Table
# -------------------------
class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE")
    )

    chunk_text = Column(Text, nullable=False)

    # embedding (fixed dimension)
    embedding = Column(Vector(768))

    # ordering
    chunk_index = Column(Integer)

    # ✅ NEW: structured metadata fields
    page_number = Column(Integer)
    char_start = Column(Integer)
    char_end = Column(Integer)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # relationship
    document = relationship("Document", back_populates="chunks")