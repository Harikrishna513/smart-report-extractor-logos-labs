import logging
import shutil
from pathlib import Path

import pytesseract

from app.config import Settings
from app.domain.exceptions import TextExtractionError
from app.domain.ports import TextExtractionResult, TextExtractor
from app.infrastructure.ocr.page_images import render_pdf_page_images
from app.infrastructure.pdf.text_extractor import _normalize_text

logger = logging.getLogger(__name__)

_WINDOWS_TESSERACT_PATHS = (
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
)

_TESSERACT_CONFIG = "--psm 6"


def configure_tesseract(tesseract_cmd: str = "") -> bool:
    """Locate the Tesseract binary, including common Windows install paths."""
    if tesseract_cmd:
        path = Path(tesseract_cmd)
        if path.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(path)
            return True

    if shutil.which("tesseract"):
        return True

    for path in _WINDOWS_TESSERACT_PATHS:
        if path.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(path)
            return True

    return False


def is_tesseract_available(tesseract_cmd: str = "") -> bool:
    return configure_tesseract(tesseract_cmd)


class TesseractOcrExtractor(TextExtractor):
    """Render PDF pages to images and run Tesseract OCR."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def extract(self, pdf_bytes: bytes) -> TextExtractionResult:
        if not is_tesseract_available(self._settings.tesseract_cmd):
            raise TextExtractionError(
                "OCR is required for this document but Tesseract is not installed."
            )

        page_count, images = render_pdf_page_images(pdf_bytes, self._settings)
        page_texts = [
            pytesseract.image_to_string(image, config=_TESSERACT_CONFIG) for image in images
        ]

        text = _normalize_text("\n\n".join(page_texts))
        if len(text) < self._settings.min_extracted_text_chars:
            raise TextExtractionError("OCR did not produce readable text from the document.")

        if page_count > len(images):
            logger.info("OCR limited to %d of %d pages", len(images), page_count)

        return TextExtractionResult(text=text, page_count=page_count, method="ocr")
