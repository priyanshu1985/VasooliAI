import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
load_dotenv(dotenv_path=backend_dir / ".env")
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.init_db import init_database

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
