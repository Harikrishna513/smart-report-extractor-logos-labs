import io
from typing import TYPE_CHECKING

import pymupdf
from PIL import Image

if TYPE_CHECKING:
    from app.config import Settings


def render_pdf_page_images(pdf_bytes: bytes, settings: "Settings") -> tuple[int, list[Image.Image]]:
    """Render PDF pages to PIL images for OCR, respecting configured page limits."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
        page_count = len(doc)
        limit = min(page_count, settings.ocr_max_pages)
        images: list[Image.Image] = []
        for index in range(limit):
            pixmap = doc[index].get_pixmap(dpi=settings.ocr_dpi)
            images.append(Image.open(io.BytesIO(pixmap.tobytes("png"))))
        return page_count, images
    finally:
        doc.close()
