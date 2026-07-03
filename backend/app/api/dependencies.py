from functools import lru_cache

from app.application.extract_report import ExtractReportUseCase
from app.config import Settings, get_settings
from app.infrastructure.classification.domain_gate import RuleBasedMedicalDomainGate
from app.infrastructure.classification.report_classifier import RuleBasedReportClassifier
from app.infrastructure.extractors.composite import CompositeFieldExtractor
from app.infrastructure.llm.factory import build_summary_generator
from app.infrastructure.pdf.factory import build_text_extractor
from app.infrastructure.storage.in_memory import (
    InMemoryBlobStorage,
    InMemoryDocumentStore,
)


@lru_cache
def get_blob_storage() -> InMemoryBlobStorage:
    return InMemoryBlobStorage()


@lru_cache
def get_document_store() -> InMemoryDocumentStore:
    return InMemoryDocumentStore()


def get_extract_use_case(settings: Settings | None = None) -> ExtractReportUseCase:
    settings = settings or get_settings()
    return ExtractReportUseCase(
        text_extractor=build_text_extractor(settings),
        domain_gate=RuleBasedMedicalDomainGate(),
        classifier=RuleBasedReportClassifier(),
        field_extractor=CompositeFieldExtractor(),
        summary_generator=build_summary_generator(settings),
        blob_storage=get_blob_storage(),
        document_store=get_document_store(),
        settings=settings,
    )
