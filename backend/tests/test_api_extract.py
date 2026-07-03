from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_extract_use_case
from app.config import Settings
from app.domain.models import CBCReportData, ReportType
from app.infrastructure.llm.factory import build_summary_generator
from app.infrastructure.llm.gemini import GeminiSummaryGenerator
from app.main import create_app
from tests.conftest import make_text_pdf
from tests.fixtures.sample_text import NON_MEDICAL_INVOICE, SAMPLE_CBC


@pytest.fixture
def app():
    application = create_app()
    application.dependency_overrides[get_extract_use_case] = (
        lambda: get_extract_use_case(settings=Settings(gemini_api_key=""))
    )
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_extract_endpoint_returns_structured_cbc_response(client):
    pdf_bytes = make_text_pdf(SAMPLE_CBC)
    response = await client.post(
        "/api/v1/extract",
        files={"file": ("cbc.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["report_type"] == "cbc_report"
    assert data["extracted_data"]["patient_name"] == "Thomas William Hughes"
    assert data["extracted_data"]["wbc"] is not None
    assert data["metadata"]["extraction_method"] in {"pdfplumber", "pymupdf"}
    assert "summary_unavailable" in data["warnings"]


@pytest.mark.asyncio
async def test_extract_endpoint_rejects_non_medical_pdf(client):
    pdf_bytes = make_text_pdf(NON_MEDICAL_INVOICE)
    response = await client.post(
        "/api/v1/extract",
        files={"file": ("invoice.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "not_medical_document"


@pytest.mark.asyncio
async def test_extract_endpoint_rejects_non_pdf_content_type(client):
    response = await client.post(
        "/api/v1/extract",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media_type"


@pytest.mark.asyncio
async def test_extract_accepts_pdf_extension_with_octet_stream(client):
    pdf_bytes = make_text_pdf(SAMPLE_CBC)
    response = await client.post(
        "/api/v1/extract",
        files={"file": ("cbc.pdf", pdf_bytes, "application/octet-stream")},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_lists_extract_endpoint(client):
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/extract" in paths


def test_summary_generator_without_api_key_returns_none():
    generator = build_summary_generator(Settings(gemini_api_key=""))
    result = generator.generate(ReportType.CBC_REPORT, CBCReportData())
    assert result is None


def test_gemini_summary_rejects_empty_api_key():
    generator = GeminiSummaryGenerator(Settings(gemini_api_key=""))
    result = generator.generate(ReportType.CBC_REPORT, CBCReportData())
    assert result is None


@patch("app.infrastructure.llm.gemini.genai.Client")
def test_gemini_summary_returns_text(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_response = MagicMock()
    mock_response.text = "The patient has a normal complete blood count."
    mock_client.models.generate_content.return_value = mock_response

    generator = GeminiSummaryGenerator(Settings(gemini_api_key="AQ.test-key"))
    result = generator.generate(
        ReportType.CBC_REPORT,
        CBCReportData(patient_name="Jane Doe", wbc="6.5"),
    )

    assert result == "The patient has a normal complete blood count."
    mock_client.models.generate_content.assert_called_once()
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-2.5-flash-lite"
    assert "Jane Doe" in call_kwargs["contents"]
    assert "cbc_report" in call_kwargs["contents"]


@patch("app.infrastructure.llm.gemini.genai.Client")
def test_gemini_summary_truncates_long_response(mock_client_cls):
    mock_client = mock_client_cls.return_value
    long_text = "A" * 600
    mock_response = MagicMock()
    mock_response.text = long_text
    mock_client.models.generate_content.return_value = mock_response

    generator = GeminiSummaryGenerator(Settings(gemini_api_key="AQ.test-key", gemini_summary_max_chars=500))
    result = generator.generate(ReportType.CBC_REPORT, CBCReportData(patient_name="Jane"))

    assert result is not None
    assert len(result) <= 500


@patch("app.infrastructure.llm.gemini.genai.Client")
def test_gemini_summary_retries_once_then_returns_none(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.models.generate_content.side_effect = RuntimeError("API unavailable")

    generator = GeminiSummaryGenerator(Settings(gemini_api_key="AQ.test-key"))
    result = generator.generate(ReportType.CBC_REPORT, CBCReportData())

    assert result is None
    assert mock_client.models.generate_content.call_count == 2
