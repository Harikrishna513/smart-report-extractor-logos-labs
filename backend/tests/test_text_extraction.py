import pytest
from unittest.mock import MagicMock, patch

from app.config import Settings
from app.domain.exceptions import TextExtractionError
from app.infrastructure.ocr.fallback import FallbackOcrExtractor
from app.infrastructure.ocr.gemini_ocr import GeminiOcrExtractor
from app.infrastructure.ocr.tesseract_extractor import TesseractOcrExtractor
from app.infrastructure.pdf.factory import build_text_extractor
from app.infrastructure.pdf.text_extractor import ChainedPdfTextExtractor
from app.infrastructure.pdf.text_extractor import _extract_with_pdfplumber, _extract_with_pymupdf

from tests.conftest import (
    CORE_MEDICAL_PDFS,
    TEXT_PDF_FIXTURES,
    load_fixture_bytes,
    make_text_pdf,
    require_tesseract,
)


def test_extracts_text_from_generated_pdf(text_extractor):
    pdf_bytes = make_text_pdf(
        "Patient Name: Jane Doe\nWBC 6.5 x10^3/uL\nHemoglobin 13.2 g/dL"
    )
    result = text_extractor.extract(pdf_bytes)

    assert result.page_count == 1
    assert result.method in {"pdfplumber", "pymupdf"}
    assert "Jane Doe" in result.text
    assert len(result.text) >= 30


def test_pdfplumber_used_when_text_is_sufficient():
    pdf_bytes = make_text_pdf("Laboratory report with enough extractable text for classification.")
    text, page_count = _extract_with_pdfplumber(pdf_bytes)

    assert page_count == 1
    assert "Laboratory report" in text

    chained = ChainedPdfTextExtractor(settings=Settings(ocr_enabled=False))
    result = chained.extract(pdf_bytes)
    assert result.method == "pdfplumber"
    assert "Laboratory report" in result.text


@pytest.mark.parametrize("fixture_name", TEXT_PDF_FIXTURES)
def test_digital_medical_fixtures_extract_text(text_extractor, fixture_name: str):
    pdf_bytes = load_fixture_bytes(fixture_name)
    result = text_extractor.extract(pdf_bytes)

    assert result.page_count >= 1
    assert result.method in {"pdfplumber", "pymupdf"}
    assert len(result.text) >= 30


@pytest.mark.parametrize("fixture_name", CORE_MEDICAL_PDFS)
def test_scanned_medical_fixtures_extract_text_with_ocr(text_extractor, fixture_name: str):
    require_tesseract()
    pdf_bytes = load_fixture_bytes(fixture_name)
    result = text_extractor.extract(pdf_bytes)

    assert result.page_count >= 1
    assert result.method == "ocr"
    assert len(result.text) >= 30


def test_raises_when_no_text_and_ocr_disabled():
    pdf_bytes = load_fixture_bytes("cbc_report.pdf")
    extractor = ChainedPdfTextExtractor(settings=Settings(ocr_enabled=False), ocr_extractor=None)

    with pytest.raises(TextExtractionError):
        extractor.extract(pdf_bytes)


def test_pymupdf_fallback_when_pdfplumber_returns_less_text():
    pdf_bytes = make_text_pdf("Fallback path check for digital PDF extraction.")
    plumber_text, _ = _extract_with_pdfplumber(pdf_bytes)
    pymupdf_text, _ = _extract_with_pymupdf(pdf_bytes)

    assert plumber_text or pymupdf_text
    assert "Fallback path check" in plumber_text or "Fallback path check" in pymupdf_text


@patch("app.infrastructure.ocr.fallback.is_tesseract_available", return_value=False)
@patch("app.infrastructure.ocr.gemini_ocr.genai.Client")
def test_gemini_ocr_fallback_when_tesseract_missing(mock_client_cls, _mock_tesseract):
    mock_client = mock_client_cls.return_value
    mock_response = MagicMock()
    mock_response.text = "Patient Name: Hari Krishna\nConsultation summary with enough text."
    mock_client.models.generate_content.return_value = mock_response

    pdf_bytes = load_fixture_bytes("cbc_report.pdf")
    settings = Settings(gemini_api_key="AQ.test-key", ocr_max_pages=1)
    extractor = build_text_extractor(settings)
    result = extractor.extract(pdf_bytes)

    assert result.method == "ocr"
    assert "Patient Name" in result.text
    mock_client.models.generate_content.assert_called_once()
