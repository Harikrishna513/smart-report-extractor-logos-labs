from app.domain.models import ExtractedData, ReportType
from app.domain.ports import SummaryGenerator


class StubSummaryGenerator(SummaryGenerator):
    """Returns no summary — used when Gemini is not configured."""

    def generate(self, report_type: ReportType, extracted_data: ExtractedData) -> str | None:
        del report_type, extracted_data
        return None
