"""SQLAlchemy engine + session."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# psycopg3 driver
_url = (
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    if DATABASE_URL.startswith("postgresql://")
    else DATABASE_URL
)
engine = create_engine(_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """FastAPI dependency。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
