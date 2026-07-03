import io
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from google import genai
from google.genai import types

from app.config import Settings
from app.domain.exceptions import TextExtractionError
from app.domain.ports import TextExtractionResult, TextExtractor
from app.infrastructure.ocr.page_images import render_pdf_page_images
from app.infrastructure.pdf.text_extractor import _normalize_text

logger = logging.getLogger(__name__)

_PAGE_PROMPT = (
    "You are an OCR engine for medical documents. "
    "Transcribe only the literal text visible in this scanned page. "
    "Return plain text only. Do not invent text or add commentary."
)


class GeminiOcrExtractor(TextExtractor):
    """OCR scanned PDF pages via Gemini vision when Tesseract is unavailable."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._client

    def extract(self, pdf_bytes: bytes) -> TextExtractionResult:
        if not self._settings.gemini_api_key:
            raise TextExtractionError(
                "OCR is required for this document but no Gemini API key is configured."
            )

        page_count, images = render_pdf_page_images(pdf_bytes, self._settings)
        page_texts: list[str] = []

        for index, image in enumerate(images, start=1):
            png_bytes = self._image_to_png_bytes(image)
            try:
                page_text = self._ocr_page(png_bytes)
            except Exception as exc:
                logger.warning("Gemini OCR failed on page %d/%d: %s", index, len(images), exc)
                continue
            if page_text:
                page_texts.append(page_text)
            logger.debug("Gemini OCR page %d/%d produced %d chars", index, len(images), len(page_text))

        text = _normalize_text("\n\n".join(page_texts))
        if len(text) < self._settings.min_extracted_text_chars:
            raise TextExtractionError("Gemini OCR did not produce readable text from the document.")

        if page_count > len(images):
            logger.info("Gemini OCR limited to %d of %d pages", len(images), page_count)

        return TextExtractionResult(text=text, page_count=page_count, method="ocr")

    def _ocr_page(self, png_bytes: bytes) -> str:
        request = [
            types.Part.from_text(text=_PAGE_PROMPT),
            types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
        ]
        config = types.GenerateContentConfig(temperature=0)

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        self._get_client().models.generate_content,
                        model=self._settings.gemini_ocr_model,
                        contents=request,
                        config=config,
                    )
                    try:
                        response = future.result(timeout=self._settings.gemini_timeout_seconds)
                    except FuturesTimeoutError as exc:
                        raise TimeoutError("Gemini OCR request timed out") from exc

                return (response.text or "").strip()
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                if attempt == 0 and ("429" in message or "503" in message or "unavailable" in message):
                    time.sleep(2)
                    continue
                raise

        if last_error is not None:
            raise last_error
        return ""

    @staticmethod
    def _image_to_png_bytes(image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
