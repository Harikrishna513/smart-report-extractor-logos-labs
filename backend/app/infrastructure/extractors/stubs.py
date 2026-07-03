from app.domain.models import (
    ExtractedData,
    HealthCheckupData,
    ReportType,
)
from app.domain.ports import FieldExtractor


class StubFieldExtractor(FieldExtractor):
    """Placeholder until Phase 3."""

    def supports(self, report_type: ReportType) -> bool:
        return True

    def extract(self, text: str, report_type: ReportType) -> ExtractedData:
        del text
        return HealthCheckupData()
