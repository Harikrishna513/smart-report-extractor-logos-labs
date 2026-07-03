import re

from app.domain.models import PrescriptionData
from app.infrastructure.extractors.patterns import find_date_near_label, find_labeled_value, find_patient_name


def extract_prescription(text: str) -> PrescriptionData:
    medications: list[dict[str, str]] = []

    numbered = re.findall(
        r"(?m)^\s*\d+[\.\)]\s*(.+)$",
        text,
    )
    for entry in numbered[:10]:
        entry = entry.strip()
        if any(word in entry.lower() for word in ("mg", "tablet", "capsule", "daily", "ml")):
            medications.append({"description": entry})

    if not medications:
        single = find_labeled_value(text, ["Medication", "Drug", "Rx"])
        if single:
            medications.append(
                {
                    "description": single,
                    "dosage": find_labeled_value(text, ["Dosage", "Sig", "Directions"]) or "",
                }
            )

    return PrescriptionData(
        patient_name=find_patient_name(text),
        prescriber=find_labeled_value(text, ["Prescriber", "Physician", "Doctor", "Attending Physician"]),
        date=find_date_near_label(text, ["Date", "Prescription Date"]),
        medications=medications,
    )
