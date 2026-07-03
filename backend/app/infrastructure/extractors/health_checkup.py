import re

from app.domain.models import HealthCheckupData
from app.infrastructure.extractors.patterns import find_date_near_label, find_labeled_value, find_patient_name


def extract_health_checkup(text: str) -> HealthCheckupData:
    vitals: dict[str, str] = {}
    screening: dict[str, str] = {}

    for label in ("Blood Pressure", "Pulse", "Heart Rate", "BMI", "Weight", "Height", "Temperature"):
        value = find_labeled_value(text, [label])
        if value:
            vitals[label.lower().replace(" ", "_")] = value

    vitals_line = find_labeled_value(text, ["Vitals"])
    if vitals_line and not vitals:
        for part in re.split(r"[,;]", vitals_line):
            if ":" in part:
                key, val = part.split(":", 1)
                vitals[key.strip().lower().replace(" ", "_")] = val.strip()

    screening_line = find_labeled_value(text, ["Screening", "Screening Results"])
    if screening_line:
        for part in re.split(r"[,;]", screening_line):
            if ":" in part:
                key, val = part.split(":", 1)
                screening[key.strip().lower().replace(" ", "_")] = val.strip()
            elif part.strip():
                screening[part.strip().lower().replace(" ", "_")] = "noted"

    recommendations: list[str] = []
    rec_block = find_labeled_value(text, ["Recommendations", "Advice", "Instructions"])
    if rec_block:
        recommendations = [part.strip() for part in re.split(r"[;\n]", rec_block) if part.strip()]

    return HealthCheckupData(
        patient_name=find_patient_name(text),
        checkup_date=find_date_near_label(text, ["Checkup Date", "Visit Date", "Exam Date"]),
        vitals=vitals,
        screening_results=screening,
        recommendations=recommendations,
    )
