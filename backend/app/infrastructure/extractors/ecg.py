import re

import re

from app.domain.models import ECGReportData
from app.infrastructure.extractors.patterns import find_labeled_value, find_patient_name, first_match


def extract_ecg_report(text: str) -> ECGReportData:
    interpretation = first_match(
        [
            r"Interpretation[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)",
            r"Impression[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)",
            r"Conclusion[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)",
        ],
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return ECGReportData(
        patient_name=find_patient_name(text),
        heart_rate=find_labeled_value(text, ["Heart Rate", "Rate"]),
        rhythm=find_labeled_value(text, ["Rhythm"]),
        pr_interval=find_labeled_value(text, ["PR Interval", "PR"]),
        qrs_duration=find_labeled_value(text, ["QRS Duration", "QRS"]),
        qt_interval=find_labeled_value(text, ["QT Interval", "QT", "QTc"]),
        interpretation=interpretation,
    )
