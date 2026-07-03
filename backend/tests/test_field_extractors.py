import pytest

from app.domain.models import ReportType
from app.infrastructure.extractors.cbc import extract_cbc_report
from app.infrastructure.extractors.discharge_summary import extract_discharge_summary
from app.infrastructure.extractors.ecg import extract_ecg_report
from app.infrastructure.extractors.health_checkup import extract_health_checkup
from app.infrastructure.extractors.prescription import extract_prescription
from tests.conftest import CORE_MEDICAL_PDFS, load_fixture_bytes, require_tesseract
from tests.fixtures.sample_text import (
    SAMPLE_CBC,
    SAMPLE_DISCHARGE,
    SAMPLE_ECG,
    SAMPLE_HEALTH_CHECKUP,
    SAMPLE_PRESCRIPTION,
)


def test_cbc_extractor_pulls_core_fields():
    data = extract_cbc_report(SAMPLE_CBC)
    assert data.patient_name == "Thomas William Hughes"
    assert data.patient_id == "SPC-2026-44102"
    assert data.wbc is not None
    assert data.hemoglobin is not None


def test_ecg_extractor_pulls_core_fields():
    data = extract_ecg_report(SAMPLE_ECG)
    assert data.patient_name == "Patricia Morrison"
    assert data.heart_rate is not None
    assert data.rhythm is not None
    assert data.interpretation is not None


def test_prescription_extractor_pulls_medications():
    data = extract_prescription(SAMPLE_PRESCRIPTION)
    assert data.patient_name == "Robert Lee"
    assert len(data.medications) >= 2


def test_discharge_summary_extractor_pulls_dates_and_diagnosis():
    data = extract_discharge_summary(SAMPLE_DISCHARGE)
    assert data.patient_name == "Mary Johnson"
    assert data.admission_date is not None
    assert data.discharge_date is not None
    assert "pneumonia" in (data.primary_diagnosis or "").lower()


def test_health_checkup_extractor_pulls_vitals_and_recommendations():
    data = extract_health_checkup(SAMPLE_HEALTH_CHECKUP)
    assert data.patient_name == "Alex Brown"
    assert data.checkup_date is not None
    assert data.vitals
    assert data.recommendations


@pytest.mark.parametrize(
    ("fixture_name", "expected_type"),
    [
        ("cbc_report.pdf", ReportType.CBC_REPORT),
        ("ecg_report.pdf", ReportType.ECG_REPORT),
        ("prescription.pdf", ReportType.PRESCRIPTION),
        ("discharge_summary.pdf", ReportType.DISCHARGE_SUMMARY),
        ("health_checkup.pdf", ReportType.HEALTH_CHECKUP),
    ],
)
def test_end_to_end_fixture_classification_and_extraction(fixture_name, expected_type, settings):
    require_tesseract()
    from app.api.dependencies import get_extract_use_case

    pdf_bytes = load_fixture_bytes(fixture_name)
    use_case = get_extract_use_case(settings=settings)
    response = use_case.execute(pdf_bytes, fixture_name, "application/pdf")

    assert response.report_type == expected_type
    assert response.confidence >= settings.type_confidence_threshold
    assert response.extracted_data.report_type == expected_type


@pytest.mark.parametrize(
    ("fixture_name", "expected_type"),
    [
        ("biochemistry_report.pdf", ReportType.CBC_REPORT),
        ("consultation_summary.pdf", ReportType.HEALTH_CHECKUP),
        ("echo_report.pdf", ReportType.ECG_REPORT),
    ],
)
def test_digital_fixture_classification(fixture_name, expected_type, settings):
    from app.infrastructure.classification.report_classifier import RuleBasedReportClassifier
    from app.infrastructure.pdf.factory import build_text_extractor
    from tests.conftest import load_fixture_bytes

    pdf_bytes = load_fixture_bytes(fixture_name)
    text = build_text_extractor(settings).extract(pdf_bytes).text
    result = RuleBasedReportClassifier().classify(text)
    assert result.report_type == expected_type
    assert result.confidence >= settings.type_confidence_threshold


@pytest.mark.parametrize("fixture_name", CORE_MEDICAL_PDFS)
def test_fixture_pdfs_yield_extractable_text(text_extractor, fixture_name, settings):
    require_tesseract()
    pdf_bytes = load_fixture_bytes(fixture_name)
    result = text_extractor.extract(pdf_bytes)
    assert len(result.text) >= settings.min_extracted_text_chars
