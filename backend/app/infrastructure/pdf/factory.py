from app.config import Settings
from app.domain.ports import TextExtractor
from app.infrastructure.ocr.fallback import FallbackOcrExtractor
from app.infrastructure.ocr.gemini_ocr import GeminiOcrExtractor
from app.infrastructure.ocr.tesseract_extractor import TesseractOcrExtractor
from app.infrastructure.pdf.text_extractor import ChainedPdfTextExtractor


def build_text_extractor(settings: Settings) -> TextExtractor:
    ocr_extractor = None
    if settings.ocr_enabled:
        gemini_extractor = (
            GeminiOcrExtractor(settings)
            if settings.gemini_ocr_enabled and settings.gemini_api_key
            else None
        )
        ocr_extractor = FallbackOcrExtractor(
            settings=settings,
            tesseract_extractor=TesseractOcrExtractor(settings),
            gemini_extractor=gemini_extractor,
        )
    return ChainedPdfTextExtractor(settings=settings, ocr_extractor=ocr_extractor)
