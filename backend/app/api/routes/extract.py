from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies import get_extract_use_case
from app.application.extract_report import ExtractReportUseCase
from app.domain.exceptions import UnsupportedMediaTypeError
from app.domain.models import ExtractionResponse

router = APIRouter(tags=["extraction"])

_ALLOWED_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    summary="Extract structured data from a medical PDF",
    responses={
        400: {"description": "Invalid PDF"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported media type"},
        422: {"description": "Extraction or validation failed"},
    },
)
async def extract_report(
    file: UploadFile = File(..., description="Medical report PDF"),
    use_case: ExtractReportUseCase = Depends(get_extract_use_case),
) -> ExtractionResponse:
    content_type = _resolve_content_type(file)
    pdf_bytes = await file.read()
    filename = file.filename or "upload.pdf"
    return use_case.execute(pdf_bytes, filename, content_type)


def _resolve_content_type(file: UploadFile) -> str:
    if file.content_type in _ALLOWED_CONTENT_TYPES:
        return file.content_type

    if file.filename and file.filename.lower().endswith(".pdf"):
        return "application/pdf"

    raise UnsupportedMediaTypeError()
