"""
Database engine and session factory for CodeForge.

Uses SQLAlchemy with SQLite. The database file lives at data/codeforge.db.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'codeforge.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def init_db():
    """Create all tables defined by the models."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
