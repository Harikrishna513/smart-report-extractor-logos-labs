import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleSet:
    phrases: tuple[tuple[str, float], ...]
    keywords: tuple[tuple[str, float], ...]

    @property
    def max_score(self) -> float:
        return sum(weight for _, weight in self.phrases) + sum(weight for _, weight in self.keywords)


MEDICAL_DOMAIN_RULES = RuleSet(
    phrases=(
        ("pathology", 1.5),
        ("laboratory report", 2.0),
        ("medical report", 2.0),
    ),
    keywords=(
        ("patient", 1.0),
        ("mrn", 1.0),
        ("physician", 1.0),
        ("diagnosis", 1.0),
        ("laboratory", 1.0),
        ("specimen", 1.0),
        ("clinical", 1.0),
        ("collected", 1.0),
        ("mg/dl", 1.0),
        ("mmhg", 1.0),
        ("hospital", 1.0),
        ("prescription", 1.0),
        ("report", 0.5),
        ("medical", 0.5),
    ),
)

REPORT_TYPE_RULES: dict[str, RuleSet] = {
    "cbc_report": RuleSet(
        phrases=(
            ("complete blood count", 3.0),
            ("cbc panel", 3.0),
            ("cbc report", 3.0),
            ("hemogram", 2.0),
            ("serum biochemistry", 3.0),
            ("biochemistry panel", 3.0),
            ("metabolic panel", 2.5),
        ),
        keywords=(
            ("wbc", 1.0),
            ("rbc", 1.0),
            ("hemoglobin", 1.0),
            ("haemoglobin", 1.0),
            ("platelet", 1.0),
            ("hematocrit", 1.0),
            ("hct", 0.5),
            ("mcv", 0.5),
            ("mch", 0.5),
            ("differential count", 1.0),
            ("glucose", 0.5),
            ("creatinine", 0.5),
            ("bilirubin", 0.5),
        ),
    ),
    "ecg_report": RuleSet(
        phrases=(
            ("electrocardiogram", 3.0),
            ("ecg report", 3.0),
            ("12-lead ecg", 3.0),
            ("12 lead ecg", 3.0),
            ("ekg report", 3.0),
            ("echocardiography", 3.0),
            ("echo report", 3.0),
            ("transthoracic echo", 3.0),
        ),
        keywords=(
            ("heart rate", 1.0),
            ("pr interval", 1.0),
            ("qrs", 1.0),
            ("qt interval", 1.0),
            ("st segment", 1.0),
            ("sinus rhythm", 1.0),
            ("ejection fraction", 1.5),
            ("rhythm", 0.5),
            ("leads", 0.5),
            ("impression", 0.5),
        ),
    ),
    "prescription": RuleSet(
        phrases=(
            ("prescription", 3.0),
            ("medication order", 2.0),
            ("rx ", 2.0),
        ),
        keywords=(
            ("dispense", 1.0),
            ("sig:", 1.0),
            ("sig ", 1.0),
            ("refills", 1.0),
            ("prescriber", 1.0),
            ("pharmacy", 1.0),
            ("dosage", 1.0),
            ("tablet", 0.5),
            ("capsule", 0.5),
        ),
    ),
    "discharge_summary": RuleSet(
        phrases=(
            ("discharge summary", 4.0),
            ("hospital discharge", 3.0),
        ),
        keywords=(
            ("admission date", 1.5),
            ("discharge date", 1.5),
            ("hospital course", 1.0),
            ("primary diagnosis", 1.0),
            ("procedures performed", 1.0),
            ("follow-up", 0.5),
            ("discharged", 0.5),
        ),
    ),
    "health_checkup": RuleSet(
        phrases=(
            ("health checkup", 3.0),
            ("health check-up", 3.0),
            ("annual physical", 3.0),
            ("preventive health", 2.0),
            ("wellness exam", 2.0),
            ("executive health", 2.0),
            ("consultation summary", 3.0),
            ("outpatient consultation", 3.0),
        ),
        keywords=(
            ("screening", 1.0),
            ("vitals", 1.0),
            ("vital signs", 1.0),
            ("bmi", 1.0),
            ("physical examination", 1.0),
            ("recommendations", 1.0),
            ("checkup date", 1.0),
            ("blood pressure", 0.5),
            ("clinical diagnosis", 1.0),
        ),
    ),
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def score_rules(text: str, rules: RuleSet) -> float:
    normalized = normalize_text(text)
    score = 0.0

    for phrase, weight in rules.phrases:
        if phrase in normalized:
            score += weight

    for keyword, weight in rules.keywords:
        if keyword in normalized:
            score += weight

    return score
