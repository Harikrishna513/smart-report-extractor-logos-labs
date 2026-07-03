from dataclasses import dataclass, field
from typing import Any

from app.domain.errors import ErrorCode


@dataclass
class DomainError(Exception):
    code: ErrorCode
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message


class InvalidPdfError(DomainError):
    def __init__(self, message: str = "The uploaded file is not a valid PDF.") -> None:
        super().__init__(ErrorCode.INVALID_PDF, message)


class FileTooLargeError(DomainError):
    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            ErrorCode.FILE_TOO_LARGE,
            f"File exceeds the maximum allowed size of {max_bytes} bytes.",
            {"max_bytes": max_bytes},
        )


class UnsupportedMediaTypeError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.UNSUPPORTED_MEDIA_TYPE,
            "Only PDF files are accepted.",
        )


class TextExtractionError(DomainError):
    def __init__(self, message: str = "Could not extract text from the document.") -> None:
        super().__init__(ErrorCode.TEXT_EXTRACTION_FAILED, message)


class NotMedicalDocumentError(DomainError):
    def __init__(self, domain_score: float) -> None:
        super().__init__(
            ErrorCode.NOT_MEDICAL_DOCUMENT,
            "This document does not appear to be a medical report.",
            {"domain_score": domain_score},
        )


class UnsupportedReportTypeError(DomainError):
    def __init__(
        self,
        confidence: float,
        candidates: list[dict[str, Any]],
        supported_types: list[str],
    ) -> None:
        super().__init__(
            ErrorCode.UNSUPPORTED_REPORT_TYPE,
            "This document does not match any supported medical report format.",
            {
                "confidence": confidence,
                "candidates": candidates,
                "supported_types": supported_types,
            },
        )
