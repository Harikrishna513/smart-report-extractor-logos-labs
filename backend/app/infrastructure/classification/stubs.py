from app.domain.models import (
    ClassificationCandidate,
    ClassificationResult,
    ReportType,
)
from app.domain.ports import MedicalDomainGate, ReportClassifier


class StubMedicalDomainGate(MedicalDomainGate):
    """Placeholder until Phase 3. Always passes domain gate."""

    def evaluate(self, text: str) -> float:
        return 1.0 if text.strip() else 0.0


class StubReportClassifier(ReportClassifier):
    """Placeholder until Phase 3. Returns a default type for non-empty text."""

    def classify(self, text: str) -> ClassificationResult:
        report_type = ReportType.HEALTH_CHECKUP
        return ClassificationResult(
            report_type=report_type,
            confidence=1.0,
            candidates=[ClassificationCandidate(report_type=report_type, score=1.0)],
        )
