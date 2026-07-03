"""Vercel serverless entrypoint — re-exports the FastAPI app from the backend package."""

import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent / "backend"
if _backend_dir.is_dir() and str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.main import app
