from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/ragdb"
# DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ragdb"
# DATABASE_URL = "postgresql://postgres:postgres@host.docker.internal:5432/ragdb"
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ragdb"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

#  CREATE TABLES
def init_db():
    Base.metadata.create_all(bind=engine)