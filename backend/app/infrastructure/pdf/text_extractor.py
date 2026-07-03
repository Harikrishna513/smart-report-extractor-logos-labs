import io
import logging
import re

import pdfplumber
import pymupdf

from app.config import Settings
from app.domain.exceptions import InvalidPdfError, TextExtractionError
from app.domain.ports import TextExtractionResult, TextExtractor

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_with_pdfplumber(pdf_bytes: bytes) -> tuple[str, int]:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            return _normalize_text("\n\n".join(pages)), len(pdf.pages)
    except Exception as exc:
        logger.debug("pdfplumber extraction failed: %s", exc)
        return "", 0


def _extract_with_pymupdf(pdf_bytes: bytes) -> tuple[str, int]:
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise InvalidPdfError("The uploaded file is corrupted or not a readable PDF.") from exc

    try:
        pages = [doc[i].get_text() for i in range(len(doc))]
        return _normalize_text("\n\n".join(pages)), len(doc)
    finally:
        doc.close()


class ChainedPdfTextExtractor(TextExtractor):
    """Extract text via pdfplumber, then PyMuPDF, then optional OCR."""

    def __init__(self, settings: Settings, ocr_extractor: TextExtractor | None = None) -> None:
        self._settings = settings
        self._ocr_extractor = ocr_extractor

    def extract(self, pdf_bytes: bytes) -> TextExtractionResult:
        text, page_count, method = self._extract_digital(pdf_bytes)

        if len(text) < self._settings.min_extracted_text_chars:
            if self._settings.ocr_enabled and self._ocr_extractor is not None:
                try:
                    ocr_result = self._ocr_extractor.extract(pdf_bytes)
                    if len(ocr_result.text) > len(text):
                        return ocr_result
                except TextExtractionError as exc:
                    logger.warning(
                        "OCR fallback failed for document with %d pages: %s",
                        page_count,
                        exc,
                    )

        if len(text) < self._settings.min_extracted_text_chars:
            raise TextExtractionError(
                "Could not extract readable text from the document. "
                "The file may be a scanned image without OCR support available."
            )

        return TextExtractionResult(text=text, page_count=page_count, method=method)

    def _extract_digital(self, pdf_bytes: bytes) -> tuple[str, int, str]:
        plumber_text, page_count = _extract_with_pdfplumber(pdf_bytes)
        if len(plumber_text) >= self._settings.min_extracted_text_chars:
            return plumber_text, page_count, "pdfplumber"

        pymupdf_text, pymupdf_pages = _extract_with_pymupdf(pdf_bytes)
        page_count = max(page_count, pymupdf_pages)

        if len(pymupdf_text) > len(plumber_text):
            return pymupdf_text, page_count, "pymupdf"

        if plumber_text:
            return plumber_text, page_count, "pdfplumber"

        return pymupdf_text, page_count, "pymupdf" if pymupdf_text else "pdfplumber"
