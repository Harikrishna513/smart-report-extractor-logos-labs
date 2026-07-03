from app.domain.ports import BlobStorage, DocumentStore, ExtractionRecord, StoredDocument


class InMemoryBlobStorage(BlobStorage):
    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}

    def save(self, data: bytes, filename: str, content_type: str) -> str:
        del filename, content_type
        blob_id = f"blob-{len(self._blobs) + 1}"
        self._blobs[blob_id] = data
        return blob_id

    def read(self, blob_id: str) -> bytes:
        return self._blobs[blob_id]

    def delete(self, blob_id: str) -> None:
        self._blobs.pop(blob_id, None)


class InMemoryDocumentStore(DocumentStore):
    def __init__(self) -> None:
        self.documents: dict[str, StoredDocument] = {}
        self.extractions: dict[str, ExtractionRecord] = {}

    def save_document(self, document: StoredDocument) -> None:
        self.documents[document.document_id] = document

    def save_extraction(self, record: ExtractionRecord) -> None:
        self.extractions[record.document_id] = record

    def get_extraction(self, document_id: str) -> ExtractionRecord | None:
        return self.extractions.get(document_id)
