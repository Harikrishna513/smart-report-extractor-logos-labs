from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_PDF = "invalid_pdf"
    FILE_TOO_LARGE = "file_too_large"
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"
    TEXT_EXTRACTION_FAILED = "text_extraction_failed"
    NOT_MEDICAL_DOCUMENT = "not_medical_document"
    UNSUPPORTED_REPORT_TYPE = "unsupported_report_type"
    INTERNAL_ERROR = "internal_error"


class WarningCode(StrEnum):
    INCOMPLETE_EXTRACTION = "incomplete_extraction"
    OCR_USED = "ocr_used"
    SUMMARY_UNAVAILABLE = "summary_unavailable"
    LOW_FIELD_CONFIDENCE = "low_field_confidence"
