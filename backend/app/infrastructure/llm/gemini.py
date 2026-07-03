import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from google import genai

from app.config import Settings
from app.domain.models import ExtractedData, ReportType
from app.domain.ports import SummaryGenerator

logger = logging.getLogger(__name__)

_AUTH_ERROR_MARKERS = (
    "401",
    "unauthenticated",
    "access_token_type_unsupported",
    "invalid authentication credentials",
)

_SUMMARY_PROMPT = """You are a medical document assistant. Write a brief plain-English summary
using only the structured data below.

Rules:
- Maximum {max_chars} characters.
- Use 2 to 4 short sentences.
- Do not invent values that are not present in the structured data.
- Mention the report type and the most clinically relevant findings.

Report type: {report_type}

Structured data:
{payload}
"""


def _is_auth_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in _AUTH_ERROR_MARKERS)


def _log_auth_help() -> None:
    logger.error(
        "Gemini authentication failed. Verify GEMINI_API_KEY in .env matches the key "
        "shown in https://aistudio.google.com/apikey (AIza or AQ. prefix)."
    )


def _compact_payload(extracted_data: ExtractedData, max_chars: int) -> str:
    """Serialize extracted fields, drop empty values, and cap size sent to Gemini."""
    raw = extracted_data.model_dump()
    compact: dict = {}

    for key, value in raw.items():
        if key == "report_type" or value in (None, "", [], {}):
            continue
        compact[key] = value

    payload = json.dumps(compact, separators=(",", ":"))
    if len(payload) <= max_chars:
        return payload

    return payload[: max_chars - 3] + "..."


class GeminiSummaryGenerator(SummaryGenerator):
    """Generates summaries from extracted fields via the Gemini API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._client

    def generate(self, report_type: ReportType, extracted_data: ExtractedData) -> str | None:
        if not self._settings.gemini_api_key:
            return None

        max_chars = self._settings.gemini_summary_max_chars
        payload = _compact_payload(extracted_data, max_chars)

        prompt = _SUMMARY_PROMPT.format(
            report_type=report_type.value,
            payload=payload,
            max_chars=max_chars,
        )

        for attempt in range(2):
            try:
                summary = self._call_gemini(prompt)
                if len(summary) > max_chars:
                    summary = summary[: max_chars - 3].rstrip() + "..."
                return summary
            except Exception as exc:
                logger.warning("Gemini summary attempt %d failed: %s", attempt + 1, exc)
                if _is_auth_error(exc):
                    _log_auth_help()
                    return None
                if attempt == 1:
                    return None
        return None

    def _call_gemini(self, prompt: str) -> str:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self._get_client().models.generate_content,
                model=self._settings.gemini_model,
                contents=prompt,
            )
            try:
                response = future.result(timeout=self._settings.gemini_timeout_seconds)
            except FuturesTimeoutError as exc:
                raise TimeoutError("Gemini request timed out") from exc

        text = (response.text or "").strip()
        if not text:
            raise ValueError("Gemini returned an empty summary")
        return text
