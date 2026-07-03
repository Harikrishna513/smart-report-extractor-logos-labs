import re

from app.domain.models import CBCReportData
from app.infrastructure.extractors.patterns import (
    find_date_near_label,
    find_labeled_value,
    find_patient_name,
)


def _lab_value(text: str, labels: list[str]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:{label_pattern})\s+([0-9]+\.?[0-9]*\s*[^\n\r|]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return re.sub(r"\s+", " ", match.group(1).strip())
    return find_labeled_value(text, labels)


def extract_cbc_report(text: str) -> CBCReportData:
    additional: dict[str, str] = {}
    for label in ("Hematocrit", "HCT", "MCV", "MCH", "RDW"):
        value = _lab_value(text, [label])
        if value:
            additional[label.lower()] = value

    for label in ("Glucose", "Creatinine", "Bilirubin", "ALT", "AST"):
        value = _lab_value(text, [label])
        if value:
            additional[label.lower()] = value

    return CBCReportData(
        patient_name=find_patient_name(text),
        patient_id=find_labeled_value(text, ["Patient ID", "MRN", "Lab ID"]),
        collection_date=find_date_near_label(text, ["Collected", "Collection Date", "Reported"]),
        wbc=_lab_value(text, ["WBC", "White Blood Cell"]),
        rbc=_lab_value(text, ["RBC", "Red Blood Cell"]),
        hemoglobin=_lab_value(text, ["Hemoglobin", "Haemoglobin", "HGB", "Hb"]),
        platelets=_lab_value(text, ["Platelet", "Platelets", "PLT"]),
        additional_values=additional,
    )
