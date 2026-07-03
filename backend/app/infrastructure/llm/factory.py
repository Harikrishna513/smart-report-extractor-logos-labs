from app.config import Settings
from app.domain.ports import SummaryGenerator
from app.infrastructure.llm.gemini import GeminiSummaryGenerator
from app.infrastructure.llm.stubs import StubSummaryGenerator


def build_summary_generator(settings: Settings) -> SummaryGenerator:
    if settings.gemini_api_key:
        return GeminiSummaryGenerator(settings)
    return StubSummaryGenerator()
