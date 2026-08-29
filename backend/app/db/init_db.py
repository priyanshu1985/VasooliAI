import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=backend_dir / ".env")
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import engine, Base, DATABASE_URL
import app.db.models  # Ensure models are imported for metadata registration


def init_database():
    """Initializes all PostgreSQL tables in Supabase / PostgreSQL instance."""
    print("=== AI Revenue Recovery Database Initializer ===")
    if "[YOUR-PASSWORD]" in DATABASE_URL:
        print("\n[ERROR] DATABASE_URL in backend/.env still contains '[YOUR-PASSWORD]'.")
        print("Please replace '[YOUR-PASSWORD]' with your actual Supabase PostgreSQL database password.")
        print(f"Current DATABASE_URL: {DATABASE_URL}\n")
        return False

    if engine is None:
        print("[ERROR] Database engine is not initialized. Please verify your connection string in backend/.env.")
        return False

    try:
        print("Connecting to database and creating tables (payments, diagnoses, retries, promises, audit_log)...")
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: All database tables created and verified successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
