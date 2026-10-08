"""Database setup: engine, session factory, Base class, and the get_db dependency."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()  # reads .env if present

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./landshield.db")

# SQLite needs check_same_thread=False because FastAPI uses multiple threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this Base (SQLAlchemy 2.x style)."""
    pass


def get_db():
    """FastAPI dependency: gives a route its own DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
