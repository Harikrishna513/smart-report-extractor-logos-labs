import logging

from app.config import Settings
from app.domain.exceptions import TextExtractionError
from app.domain.ports import TextExtractionResult, TextExtractor
from app.infrastructure.ocr.gemini_ocr import GeminiOcrExtractor
from app.infrastructure.ocr.tesseract_extractor import TesseractOcrExtractor, is_tesseract_available

logger = logging.getLogger(__name__)


class FallbackOcrExtractor(TextExtractor):
    """Prefer local Tesseract OCR; fall back to Gemini vision when needed."""

    def __init__(
        self,
        settings: Settings,
        tesseract_extractor: TesseractOcrExtractor,
        gemini_extractor: GeminiOcrExtractor | None,
    ) -> None:
        self._settings = settings
        self._tesseract_extractor = tesseract_extractor
        self._gemini_extractor = gemini_extractor

    def extract(self, pdf_bytes: bytes) -> TextExtractionResult:
        if is_tesseract_available(self._settings.tesseract_cmd):
            try:
                return self._tesseract_extractor.extract(pdf_bytes)
            except TextExtractionError as exc:
                logger.warning("Tesseract OCR failed, trying Gemini fallback: %s", exc)

        if self._settings.gemini_ocr_enabled and self._gemini_extractor is not None:
            return self._gemini_extractor.extract(pdf_bytes)

        if not is_tesseract_available(self._settings.tesseract_cmd):
            raise TextExtractionError(
                "OCR is required for this scanned document. Install Tesseract "
                "(https://github.com/UB-Mannheim/tesseract/wiki) or set GEMINI_API_KEY "
                "to enable Gemini vision OCR."
            )

        raise TextExtractionError("OCR did not produce readable text from the document.")
