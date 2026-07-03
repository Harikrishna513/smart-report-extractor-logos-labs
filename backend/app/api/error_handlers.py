from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainError


def register_exception_handlers(app) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        status_code = _status_for_code(exc.code.value)
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code.value,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )


def _status_for_code(code: str) -> int:
    mapping = {
        "invalid_pdf": 400,
        "file_too_large": 413,
        "unsupported_media_type": 415,
        "text_extraction_failed": 422,
        "not_medical_document": 422,
        "unsupported_report_type": 422,
        "internal_error": 500,
    }
    return mapping.get(code, 500)
