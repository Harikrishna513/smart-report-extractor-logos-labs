import pytest

from app.config import Settings
from app.domain.exceptions import NotMedicalDocumentError, UnsupportedReportTypeError
from app.domain.models import ReportType
from app.infrastructure.classification.domain_gate import RuleBasedMedicalDomainGate
from app.infrastructure.classification.report_classifier import RuleBasedReportClassifier
from tests.fixtures.sample_text import (
    NON_MEDICAL_INVOICE,
    SAMPLE_BIOCHEMISTRY,
    SAMPLE_CBC,
    SAMPLE_CONSULTATION,
    SAMPLE_DISCHARGE,
    SAMPLE_ECG,
    SAMPLE_ECHO,
    SAMPLE_HEALTH_CHECKUP,
    SAMPLE_PRESCRIPTION,
)


@pytest.fixture
def domain_gate() -> RuleBasedMedicalDomainGate:
    return RuleBasedMedicalDomainGate()


@pytest.fixture
def classifier() -> RuleBasedReportClassifier:
    return RuleBasedReportClassifier()


@pytest.mark.parametrize(
    ("text", "expected_type"),
    [
        (SAMPLE_CBC, ReportType.CBC_REPORT),
        (SAMPLE_ECG, ReportType.ECG_REPORT),
        (SAMPLE_PRESCRIPTION, ReportType.PRESCRIPTION),
        (SAMPLE_DISCHARGE, ReportType.DISCHARGE_SUMMARY),
        (SAMPLE_HEALTH_CHECKUP, ReportType.HEALTH_CHECKUP),
        (SAMPLE_BIOCHEMISTRY, ReportType.CBC_REPORT),
        (SAMPLE_CONSULTATION, ReportType.HEALTH_CHECKUP),
        (SAMPLE_ECHO, ReportType.ECG_REPORT),
    ],
)
def test_classifier_identifies_report_types(classifier, text, expected_type):
    result = classifier.classify(text)
    assert result.report_type == expected_type
    assert result.confidence >= Settings().type_confidence_threshold


def test_domain_gate_accepts_medical_text(domain_gate):
    score = domain_gate.evaluate(SAMPLE_CBC)
    assert score >= Settings().domain_score_threshold


def test_domain_gate_rejects_invoice(domain_gate):
    score = domain_gate.evaluate(NON_MEDICAL_INVOICE)
    assert score < Settings().domain_score_threshold


def test_use_case_rejects_non_medical_document():
    from app.api.dependencies import get_extract_use_case
    from tests.conftest import make_text_pdf

    use_case = get_extract_use_case()
    pdf_bytes = make_text_pdf(NON_MEDICAL_INVOICE)

    with pytest.raises(NotMedicalDocumentError):
        use_case.execute(pdf_bytes, "invoice.pdf", "application/pdf")


def test_use_case_rejects_unsupported_medical_format():
    from app.api.dependencies import get_extract_use_case
    from tests.conftest import make_text_pdf

    use_case = get_extract_use_case()
    ambiguous = make_text_pdf(
        "Patient Name: Jane Doe\n"
        "MRN: 12345\n"
        "Physician: Dr. Smith\n"
        "Clinical progress note without a structured laboratory or report format.\n"
        "Assessment: observation only."
    )
    with pytest.raises(UnsupportedReportTypeError):
        use_case.execute(ambiguous, "note.pdf", "application/pdf")
