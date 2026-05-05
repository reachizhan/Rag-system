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

    # relationships
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete"
    )

    parent_chunks = relationship(
        "ParentChunk",
        back_populates="document",
        cascade="all, delete"
    )


# -------------------------
# Parent Chunks Table (NEW)
# -------------------------
class ParentChunk(Base):
    __tablename__ = "parent_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    parent_text = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # relationships
    document = relationship("Document", back_populates="parent_chunks")

    children = relationship(
        "Chunk",
        back_populates="parent",
        cascade="all, delete"
    )


# -------------------------
# Chunks Table (CHILD CHUNKS)
# -------------------------
class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    # 🔥 NEW: link to parent chunk
    parent_id = Column(
        Integer,
        ForeignKey("parent_chunks.id", ondelete="CASCADE"),
        nullable=True
    )

    chunk_text = Column(Text, nullable=False)

    # embedding (child-level embedding for retrieval)
    embedding = Column(Vector(768))

    # ordering
    chunk_index = Column(Integer)

    # metadata
    page_number = Column(Integer)
    char_start = Column(Integer)
    char_end = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # relationships
    document = relationship("Document", back_populates="chunks")

    parent = relationship("ParentChunk", back_populates="children")