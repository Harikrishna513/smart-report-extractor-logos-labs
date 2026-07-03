from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            _BACKEND_DIR / ".env",
            _PROJECT_ROOT / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_timeout_seconds: int = 30
    gemini_summary_max_chars: int = 500
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    max_upload_bytes: int = 10 * 1024 * 1024  # 10 MB

    domain_score_threshold: float = 0.25
    type_confidence_threshold: float = 0.65
    type_margin_threshold: float = 0.15

    min_extracted_text_chars: int = 30
    ocr_enabled: bool = True
    ocr_max_pages: int = 25
    ocr_dpi: int = 200
    tesseract_cmd: str = ""
    gemini_ocr_enabled: bool = True
    gemini_ocr_model: str = "gemini-2.5-flash-lite"


def get_settings() -> Settings:
    return Settings()
