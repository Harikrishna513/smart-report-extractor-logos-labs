from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

from app.domain.errors import WarningCode


class ReportType(StrEnum):
    CBC_REPORT = "cbc_report"
    ECG_REPORT = "ecg_report"
    PRESCRIPTION = "prescription"
    DISCHARGE_SUMMARY = "discharge_summary"
    HEALTH_CHECKUP = "health_checkup"


SUPPORTED_REPORT_TYPES: list[ReportType] = list(ReportType)


class ExtractionMetadata(BaseModel):
    page_count: int
    extraction_method: str
    duration_ms: int
    text_length: int


class CBCReportData(BaseModel):
    report_type: Literal[ReportType.CBC_REPORT] = ReportType.CBC_REPORT
    patient_name: str | None = None
    patient_id: str | None = None
    collection_date: str | None = None
    wbc: str | None = None
    rbc: str | None = None
    hemoglobin: str | None = None
    platelets: str | None = None
    additional_values: dict[str, str] = Field(default_factory=dict)


class ECGReportData(BaseModel):
    report_type: Literal[ReportType.ECG_REPORT] = ReportType.ECG_REPORT
    patient_name: str | None = None
    heart_rate: str | None = None
    rhythm: str | None = None
    pr_interval: str | None = None
    qrs_duration: str | None = None
    qt_interval: str | None = None
    interpretation: str | None = None


class PrescriptionData(BaseModel):
    report_type: Literal[ReportType.PRESCRIPTION] = ReportType.PRESCRIPTION
    patient_name: str | None = None
    prescriber: str | None = None
    date: str | None = None
    medications: list[dict[str, str]] = Field(default_factory=list)


class DischargeSummaryData(BaseModel):
    report_type: Literal[ReportType.DISCHARGE_SUMMARY] = ReportType.DISCHARGE_SUMMARY
    patient_name: str | None = None
    admission_date: str | None = None
    discharge_date: str | None = None
    primary_diagnosis: str | None = None
    procedures: list[str] = Field(default_factory=list)
    follow_up: str | None = None


class HealthCheckupData(BaseModel):
    report_type: Literal[ReportType.HEALTH_CHECKUP] = ReportType.HEALTH_CHECKUP
    patient_name: str | None = None
    checkup_date: str | None = None
    vitals: dict[str, str] = Field(default_factory=dict)
    screening_results: dict[str, str] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


ExtractedData = Annotated[
    CBCReportData
    | ECGReportData
    | PrescriptionData
    | DischargeSummaryData
    | HealthCheckupData,
    Field(discriminator="report_type"),
]


class ClassificationCandidate(BaseModel):
    report_type: ReportType
    score: float


class ClassificationResult(BaseModel):
    report_type: ReportType
    confidence: float
    candidates: list[ClassificationCandidate]


class ExtractionResponse(BaseModel):
    document_id: str
    status: Literal["success"] = "success"
    report_type: ReportType
    confidence: float
    extracted_data: ExtractedData
    summary: str | None
    warnings: list[WarningCode] = Field(default_factory=list)
    metadata: ExtractionMetadata


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "0.1.0"
    supported_report_types: list[ReportType] = Field(default_factory=lambda: SUPPORTED_REPORT_TYPES)
