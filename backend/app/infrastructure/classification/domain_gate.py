from app.domain.ports import MedicalDomainGate
from app.infrastructure.classification.rules import MEDICAL_DOMAIN_RULES, score_rules

_FULL_CONFIDENCE_RAW_SCORE = 3.0


class RuleBasedMedicalDomainGate(MedicalDomainGate):
    def evaluate(self, text: str) -> float:
        raw_score = score_rules(text, MEDICAL_DOMAIN_RULES)
        return min(1.0, raw_score / _FULL_CONFIDENCE_RAW_SCORE)
