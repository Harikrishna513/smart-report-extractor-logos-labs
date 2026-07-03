"""Vercel serverless entrypoint — re-exports the FastAPI app from the backend package."""

from app.main import app
