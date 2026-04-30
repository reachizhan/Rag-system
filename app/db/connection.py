from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# DATABASE URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ragdb"

# Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # avoids stale connections
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# -------------------------
# DB Dependency (IMPORTANT)
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Initialize DB
# -------------------------
def init_db():
    Base.metadata.create_all(bind=engine)