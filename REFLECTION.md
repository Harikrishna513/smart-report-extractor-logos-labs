# AI Reflection Log

> Required for the Logos Labs engineering assessment.

## Where AI helped

| Phase | What I prompted | What it produced | What I used |
|-------|-----------------|------------------|-------------|
| Planning | Architecture for medical PDF extractor with no DB, Gemini summary-only | Phased plan, ports-and-adapters layout, domain gate vs classifier split | Adopted two-stage validation, extension points for storage/RAG |
| 1 | Monorepo scaffold | Backend domain layer, FastAPI health, Next.js shell, Docker | Used as starting structure; simplified frontend Docker (Vercel deploy instead) |
| 2 | PDF text extraction pipeline | pdfplumber → PyMuPDF → OCR chain | Implemented with config flags; documented OCR limitation on Vercel |
| 3 | Classification and extractors | Rule-based scorer + per-type regex extractors | Used approach; tuned confidence scaling and patient-name regex after test failures |
| 4 | Gemini summary + extract API | Summary from structured JSON only, retry/fallback | Adopted; kept `google.generativeai` (deprecated warning noted for future migration) |
| 5 | Upload UI | Drag-drop components, error/warning mapping | Built client components matching API error codes |
| 6 | Release polish | README, Vercel config fix, cleanup | Fixed `api/index.py` entrypoint after local `vercel build` failure |

## Where AI was wrong or incomplete

| Phase | Issue | What I did instead |
|-------|-------|-------------------|
| 3 | Patient name regex over-captured adjacent labels ("Patient Name: X Patient ID") | Added lookahead boundary in `patterns.py` |
| 3 | Raw rule scores produced confidence below threshold | Rescaled confidence with a fixed denominator instead of max possible rule weight |
| 4 | Initial `vercel.json` pointed to `backend/app/main.py` | Vercel requires `api/` entrypoint — added `api/index.py` shim |
| 2 | Assumed sample PDFs were digital text | Found most are scanned; OCR tests skip locally without Tesseract |

## Notes

- AI tools (Cursor) were used for scaffolding, implementation, and iteration — not for unchecked copy-paste.
- Classification rules and extractors were validated against synthetic test text and local sample PDFs.
- I reviewed and corrected AI output when tests failed or when platform constraints (Vercel, OCR) required different decisions.
