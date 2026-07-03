from app.domain.models import ClassificationCandidate, ClassificationResult, ReportType
from app.domain.ports import ReportClassifier
from app.infrastructure.classification.rules import REPORT_TYPE_RULES, score_rules

# Raw rule scores at or above this value map to confidence 1.0.
_FULL_CONFIDENCE_RAW_SCORE = 6.0


class RuleBasedReportClassifier(ReportClassifier):
    def classify(self, text: str) -> ClassificationResult:
        scored: list[tuple[ReportType, float]] = []

        for report_type_value, rules in REPORT_TYPE_RULES.items():
            report_type = ReportType(report_type_value)
            raw_score = score_rules(text, rules)
            scored.append((report_type, raw_score))

        scored.sort(key=lambda item: item[1], reverse=True)
        winner_type, winner_raw = scored[0]
        winner_confidence = min(1.0, winner_raw / _FULL_CONFIDENCE_RAW_SCORE)

        candidates = [
            ClassificationCandidate(
                report_type=report_type,
                score=round(min(1.0, raw / _FULL_CONFIDENCE_RAW_SCORE), 4),
            )
            for report_type, raw in scored
            if raw > 0
        ]

        if not candidates:
            candidates = [ClassificationCandidate(report_type=winner_type, score=0.0)]

        return ClassificationResult(
            report_type=winner_type,
            confidence=round(winner_confidence, 4),
            candidates=candidates,
        )
