from pathlib import Path

import pymupdf
import pytest

from app.config import Settings
from app.infrastructure.ocr.tesseract_extractor import is_tesseract_available
from app.infrastructure.pdf.factory import build_text_extractor

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pdfs"
REPO_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "medical-pdf"

CORE_MEDICAL_PDFS = [
    "cbc_report.pdf",
    "ecg_report.pdf",
    "prescription.pdf",
    "discharge_summary.pdf",
    "health_checkup.pdf",
]

TEXT_PDF_FIXTURES = [
    "biochemistry_report.pdf",
    "consultation_summary.pdf",
    "echo_report.pdf",
]


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def text_extractor(settings: Settings):
    return build_text_extractor(settings)


def resolve_fixture(name: str) -> Path | None:
    for directory in (FIXTURES_DIR, REPO_FIXTURES_DIR):
        path = directory / name
        if path.is_file():
            return path
    return None


def load_fixture_bytes(name: str) -> bytes:
    path = resolve_fixture(name)
    if path is None:
        pytest.skip(f"Fixture '{name}' not found. Place PDFs in backend/tests/fixtures/pdfs/")
    return path.read_bytes()


def make_text_pdf(content: str) -> bytes:
    doc = pymupdf.open()
    try:
        page = doc.new_page()
        page.insert_text((72, 72), content, fontsize=12)
        return doc.tobytes()
    finally:
        doc.close()


def require_tesseract() -> None:
    if not is_tesseract_available():
        pytest.skip("Tesseract is not installed — OCR fixture tests skipped")
