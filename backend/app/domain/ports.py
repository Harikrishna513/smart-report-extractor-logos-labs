from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.models import (
    ClassificationResult,
    ExtractionResponse,
    ExtractedData,
    ReportType,
)


@dataclass
class TextExtractionResult:
    text: str
    page_count: int
    method: str


@dataclass
class StoredDocument:
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime
    blob_id: str


@dataclass
class ExtractionRecord:
    document_id: str
    response: ExtractionResponse
    stored_at: datetime


class TextExtractor(Protocol):
    def extract(self, pdf_bytes: bytes) -> TextExtractionResult: ...


class MedicalDomainGate(Protocol):
    def evaluate(self, text: str) -> float: ...


class ReportClassifier(Protocol):
    def classify(self, text: str) -> ClassificationResult: ...


class FieldExtractor(Protocol):
    def supports(self, report_type: ReportType) -> bool: ...

    def extract(self, text: str, report_type: ReportType) -> ExtractedData: ...


class SummaryGenerator(Protocol):
    def generate(self, report_type: ReportType, extracted_data: ExtractedData) -> str | None: ...


class BlobStorage(Protocol):
    def save(self, data: bytes, filename: str, content_type: str) -> str: ...

    def read(self, blob_id: str) -> bytes: ...

    def delete(self, blob_id: str) -> None: ...


class DocumentStore(Protocol):
    def save_document(self, document: StoredDocument) -> None: ...

    def save_extraction(self, record: ExtractionRecord) -> None: ...

    def get_extraction(self, document_id: str) -> ExtractionRecord | None: ...
