from app.domain.errors import WarningCode
from app.domain.models import (
    CBCReportData,
    DischargeSummaryData,
    ExtractedData,
    ECGReportData,
    HealthCheckupData,
    PrescriptionData,
    ReportType,
)
from app.domain.ports import FieldExtractor
from app.infrastructure.extractors.cbc import extract_cbc_report
from app.infrastructure.extractors.discharge_summary import extract_discharge_summary
from app.infrastructure.extractors.ecg import extract_ecg_report
from app.infrastructure.extractors.health_checkup import extract_health_checkup
from app.infrastructure.extractors.prescription import extract_prescription

_EXTRACTORS = {
    ReportType.CBC_REPORT: extract_cbc_report,
    ReportType.ECG_REPORT: extract_ecg_report,
    ReportType.PRESCRIPTION: extract_prescription,
    ReportType.DISCHARGE_SUMMARY: extract_discharge_summary,
    ReportType.HEALTH_CHECKUP: extract_health_checkup,
}


class CompositeFieldExtractor(FieldExtractor):
    def supports(self, report_type: ReportType) -> bool:
        return report_type in _EXTRACTORS

    def extract(self, text: str, report_type: ReportType) -> ExtractedData:
        extractor = _EXTRACTORS.get(report_type)
        if extractor is None:
            raise ValueError(f"No extractor registered for {report_type}")
        return extractor(text)


def completeness_warnings(report_type: ReportType, data: ExtractedData) -> list[WarningCode]:
    if _is_incomplete(report_type, data):
        return [WarningCode.INCOMPLETE_EXTRACTION]
    return []


def _is_incomplete(report_type: ReportType, data: ExtractedData) -> bool:
    if isinstance(data, CBCReportData):
        return not data.patient_name and not any([data.wbc, data.hemoglobin, data.platelets])
    if isinstance(data, ECGReportData):
        return not data.patient_name and not any([data.heart_rate, data.rhythm, data.interpretation])
    if isinstance(data, PrescriptionData):
        return not data.patient_name and not data.medications
    if isinstance(data, DischargeSummaryData):
        return not data.patient_name and not data.primary_diagnosis
    if isinstance(data, HealthCheckupData):
        return not data.patient_name and not data.vitals and not data.screening_results
    return False
