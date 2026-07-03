import re

from app.domain.models import DischargeSummaryData
from app.infrastructure.extractors.patterns import find_date_near_label, find_labeled_value, find_patient_name


def extract_discharge_summary(text: str) -> DischargeSummaryData:
    procedures: list[str] = []
    procedure_block = find_labeled_value(text, ["Procedures", "Procedures Performed"])
    if procedure_block:
        procedures = [part.strip() for part in re.split(r"[,;]", procedure_block) if part.strip()]

    return DischargeSummaryData(
        patient_name=find_patient_name(text),
        admission_date=find_date_near_label(text, ["Admission Date", "Date of Admission"]),
        discharge_date=find_date_near_label(text, ["Discharge Date", "Date of Discharge"]),
        primary_diagnosis=find_labeled_value(
            text,
            ["Primary Diagnosis", "Principal Diagnosis", "Diagnosis"],
        ),
        procedures=procedures,
        follow_up=find_labeled_value(text, ["Follow-up", "Follow Up", "Followup"]),
    )
