import re

# Field labels that terminate a captured value on the same line.
_NEXT_FIELD = (
    r"(?=\s*(?:Patient ID|MRN|Lab ID|Prescriber|Physician|Doctor|Heart Rate|"
    r"Admission Date|Discharge Date|Checkup Date|Collected|Collection Date|"
    r"Date:|Gender|DOB|Specimen)\b|\n|$)"
)


def first_match(patterns: list[str], text: str, flags: int = re.IGNORECASE) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return re.sub(r"\s+", " ", match.group(1).strip())
    return None


def find_patient_name(text: str) -> str | None:
    return first_match(
        [
            rf"Patient Name[:\s]+([A-Za-z][A-Za-z\s\.\-']+?){_NEXT_FIELD}",
            rf"PATIENT NAME\s+([A-Za-z][A-Za-z\s\.\-']+?){_NEXT_FIELD}",
            rf"Patient[:\s]+([A-Za-z][A-Za-z\s\.\-']+?){_NEXT_FIELD}",
        ],
        text,
    )


def find_labeled_value(text: str, labels: list[str]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:{label_pattern})[:\s]+([^\n\r;|]+)"
    return first_match([pattern], text)


def find_date_near_label(text: str, labels: list[str]) -> str | None:
    value = find_labeled_value(text, labels)
    if not value:
        return None
    date_match = re.search(
        r"(\d{1,2}[\-/][A-Za-z]{3}[\-/]\d{2,4}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        value,
    )
    return date_match.group(1) if date_match else value.strip()[:40]
