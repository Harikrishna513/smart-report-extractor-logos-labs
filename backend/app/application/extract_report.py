import time
import uuid
from datetime import UTC, datetime

from app.config import Settings
from app.domain.exceptions import (
    FileTooLargeError,
    InvalidPdfError,
    NotMedicalDocumentError,
    UnsupportedMediaTypeError,
    UnsupportedReportTypeError,
)
from app.domain.errors import WarningCode
from app.infrastructure.extractors.composite import completeness_warnings
from app.domain.models import (
    ExtractionMetadata,
    ExtractionResponse,
    SUPPORTED_REPORT_TYPES,
)
from app.domain.ports import (
    BlobStorage,
    DocumentStore,
    ExtractionRecord,
    FieldExtractor,
    MedicalDomainGate,
    ReportClassifier,
    StoredDocument,
    SummaryGenerator,
    TextExtractor,
)


class ExtractReportUseCase:
    """Orchestrates PDF validation, extraction, classification, and summarization."""

    def __init__(
        self,
        text_extractor: TextExtractor,
        domain_gate: MedicalDomainGate,
        classifier: ReportClassifier,
        field_extractor: FieldExtractor,
        summary_generator: SummaryGenerator,
        blob_storage: BlobStorage,
        document_store: DocumentStore,
        settings: Settings,
    ) -> None:
        self._text_extractor = text_extractor
        self._domain_gate = domain_gate
        self._classifier = classifier
        self._field_extractor = field_extractor
        self._summary_generator = summary_generator
        self._blob_storage = blob_storage
        self._document_store = document_store
        self._settings = settings

    def execute(
        self,
        pdf_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> ExtractionResponse:
        start = time.perf_counter()
        self._validate_upload(pdf_bytes, content_type)

        document_id = str(uuid.uuid4())
        blob_id = self._blob_storage.save(pdf_bytes, filename, content_type)
        self._document_store.save_document(
            StoredDocument(
                document_id=document_id,
                filename=filename,
                content_type=content_type,
                size_bytes=len(pdf_bytes),
                created_at=datetime.now(UTC),
                blob_id=blob_id,
            )
        )

        extraction = self._text_extractor.extract(pdf_bytes)

        warnings: list[WarningCode] = []
        if extraction.method == "ocr":
            warnings.append(WarningCode.OCR_USED)

        domain_score = self._domain_gate.evaluate(extraction.text)
        if domain_score < self._settings.domain_score_threshold:
            raise NotMedicalDocumentError(domain_score)

        classification = self._classifier.classify(extraction.text)
        self._validate_classification(classification)

        extracted_data = self._field_extractor.extract(extraction.text, classification.report_type)
        warnings.extend(completeness_warnings(classification.report_type, extracted_data))

        summary = self._summary_generator.generate(classification.report_type, extracted_data)
        if summary is None:
            warnings.append(WarningCode.SUMMARY_UNAVAILABLE)

        duration_ms = int((time.perf_counter() - start) * 1000)
        response = ExtractionResponse(
            document_id=document_id,
            report_type=classification.report_type,
            confidence=classification.confidence,
            extracted_data=extracted_data,
            summary=summary,
            warnings=warnings,
            metadata=ExtractionMetadata(
                page_count=extraction.page_count,
                extraction_method=extraction.method,
                duration_ms=duration_ms,
                text_length=len(extraction.text),
            ),
        )

        self._document_store.save_extraction(
            ExtractionRecord(document_id=document_id, response=response, stored_at=datetime.now(UTC))
        )
        return response

    def _validate_upload(self, pdf_bytes: bytes, content_type: str) -> None:
        if content_type not in ("application/pdf", "application/x-pdf"):
            raise UnsupportedMediaTypeError()
        if len(pdf_bytes) > self._settings.max_upload_bytes:
            raise FileTooLargeError(self._settings.max_upload_bytes)
        if not pdf_bytes.startswith(b"%PDF"):
            raise InvalidPdfError()

    def _validate_classification(self, classification) -> None:
        if classification.confidence < self._settings.type_confidence_threshold:
            raise UnsupportedReportTypeError(
                confidence=classification.confidence,
                candidates=[
                    {"type": c.report_type.value, "score": c.score}
                    for c in classification.candidates
                ],
                supported_types=[t.value for t in SUPPORTED_REPORT_TYPES],
            )
        if len(classification.candidates) >= 2:
            margin = classification.candidates[0].score - classification.candidates[1].score
            if margin < self._settings.type_margin_threshold:
                raise UnsupportedReportTypeError(
                    confidence=classification.confidence,
                    candidates=[
                        {"type": c.report_type.value, "score": c.score}
                        for c in classification.candidates
                    ],
                    supported_types=[t.value for t in SUPPORTED_REPORT_TYPES],
                )
