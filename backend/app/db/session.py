import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("recovery_ai.db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/recovery_ai"
)

# SQLite fallback is explicitly forbidden by architecture.md / memory.md
if DATABASE_URL.startswith("sqlite"):
    raise ValueError("SQLite is not supported per architectural rules. Use PostgreSQL (e.g. Supabase).")

# Support both postgresql:// and postgres:// connection prefixes
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()
engine = None
SessionLocal = None

try:
    if "[YOUR-PASSWORD]" not in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            echo=False
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        logger.warning("DATABASE_URL contains placeholder '[YOUR-PASSWORD]'. Database persistence will be bypassed until real password is provided.")
except Exception as e:
    logger.warning(f"Could not initialize database engine: {e}")


def get_db():
    """Dependency that yields a database session or None if database is not configured."""
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
