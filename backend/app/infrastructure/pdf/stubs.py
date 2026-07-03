from app.domain.ports import TextExtractionResult, TextExtractor


class StubTextExtractor(TextExtractor):
    """Returns empty text for pipeline tests that skip PDF parsing."""

    def extract(self, pdf_bytes: bytes) -> TextExtractionResult:
        del pdf_bytes
        return TextExtractionResult(text="", page_count=0, method="stub")
