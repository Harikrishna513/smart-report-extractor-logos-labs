import pytest

from app.api.dependencies import get_extract_use_case
from app.application.extract_report import ExtractReportUseCase
from app.config import Settings
from app.domain.exceptions import (
    FileTooLargeError,
    InvalidPdfError,
    NotMedicalDocumentError,
    UnsupportedMediaTypeError,
)
from app.infrastructure.classification.stubs import StubMedicalDomainGate, StubReportClassifier
from app.infrastructure.extractors.stubs import StubFieldExtractor
from app.infrastructure.llm.stubs import StubSummaryGenerator
from app.infrastructure.pdf.stubs import StubTextExtractor
from app.infrastructure.storage.in_memory import (
    InMemoryBlobStorage,
    InMemoryDocumentStore,
)


def _use_case(max_bytes: int = 10_000_000) -> ExtractReportUseCase:
    settings = Settings(max_upload_bytes=max_bytes)
    return get_extract_use_case(settings=settings)


def _use_case_with_stub_extractor() -> ExtractReportUseCase:
    settings = Settings()
    return ExtractReportUseCase(
        text_extractor=StubTextExtractor(),
        domain_gate=StubMedicalDomainGate(),
        classifier=StubReportClassifier(),
        field_extractor=StubFieldExtractor(),
        summary_generator=StubSummaryGenerator(),
        blob_storage=InMemoryBlobStorage(),
        document_store=InMemoryDocumentStore(),
        settings=settings,
    )


def test_rejects_non_pdf_content_type():
    use_case = _use_case()
    with pytest.raises(UnsupportedMediaTypeError):
        use_case.execute(b"%PDF-1.4", "test.pdf", "text/plain")


def test_rejects_invalid_pdf_magic_bytes():
    use_case = _use_case()
    with pytest.raises(InvalidPdfError):
        use_case.execute(b"not a pdf", "test.pdf", "application/pdf")


def test_rejects_oversized_file():
    use_case = _use_case(max_bytes=100)
    with pytest.raises(FileTooLargeError):
        use_case.execute(b"%PDF" + b"x" * 200, "big.pdf", "application/pdf")


def test_rejects_unextractable_pdf():
    use_case = _use_case()
    with pytest.raises(InvalidPdfError):
        use_case.execute(b"%PDF-1.4\n%", "bad.pdf", "application/pdf")


def test_rejects_empty_text_as_non_medical():
    use_case = _use_case_with_stub_extractor()
    with pytest.raises(NotMedicalDocumentError):
        use_case.execute(b"%PDF-1.4 test", "empty.pdf", "application/pdf")
