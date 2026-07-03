# Smart Report Extractor

Extract structured data and plain-English summaries from medical PDF reports (CBC, ECG, prescription, discharge summary, health checkup).

## Features

- Upload a PDF via web UI or REST API
- Deterministic medical domain validation and report-type classification (no LLM for gating)
- Structured field extraction per report type
- Plain-English summary via Gemini from extracted fields only
- Clear error codes for invalid, non-medical, or unsupported documents

## Quick start (local)

### 1. Environment

Copy `.env.example` to `.env` at the **project root** (or in `backend/`):

```bash
cp .env.example .env
# Set GEMINI_API_KEY from https://aistudio.google.com/apikey (AIza or AQ. prefix)
```

The backend loads `.env` from the project root or `backend/` automatically.

### 2. Backend

```bash
cd backend
python -m venv .venv

# Activate the virtual environment (required before pip install)
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"

# Use python -m so uvicorn works even when Scripts/ is not on PATH
python -m uvicorn app.main:app --reload --port 8000 --reload-exclude ".venv"
```

If you skip activation, `pip` may install globally and `uvicorn` won't be found. Either activate the venv first, or run:

```bash
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000 --reload-exclude ".venv"
```

- Health: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/api/docs

**Scanned PDFs (OCR):** Digital extraction is tried first. For image-only PDFs, the backend uses Tesseract when installed, otherwise **Gemini vision OCR** (requires `GEMINI_API_KEY`). On Windows, install Tesseract with:

```powershell
winget install UB-Mannheim.TesseractOCR
```

Then restart the terminal so `tesseract` is on PATH, or set `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`.

### 3. Frontend

```bash
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://localhost:8000   # Windows
npm run dev
```

Open http://localhost:3000 — upload a medical PDF and click **Extract report**.

### API upload (curl)

```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -F "file=@your-report.pdf;type=application/pdf"
```

## Docker (backend only)

```bash
docker compose up --build
```

Runs the API on port 8000 with Tesseract available for OCR. Run the frontend separately with `npm run dev`.

## Tests

```bash
cd backend
pytest -v
```

**51 tests** — 36 run locally without Tesseract; 15 OCR fixture tests run when Tesseract is installed (e.g. in Docker).

Place sample PDFs in `backend/tests/fixtures/pdfs/` for local development (gitignored).

## Supported report types

| Type | Description |
|------|-------------|
| `cbc_report` | Complete blood count / lab panel |
| `ecg_report` | Electrocardiogram |
| `prescription` | Medication prescription |
| `discharge_summary` | Hospital discharge summary |
| `health_checkup` | Preventive health / wellness exam |

Non-medical documents (invoices, resumes, etc.) return `422 not_medical_document` — no LLM is used for validation.

## Project structure

```
api/                 # Vercel serverless entrypoint
backend/app/         # FastAPI + business logic
frontend/src/        # Next.js UI
docker-compose.yml   # Local backend with OCR
vercel.json          # Vercel routing (frontend + Python API)
```

## Deployment (Vercel)

Configured for a single Vercel project:

- **Frontend** — Next.js build from `frontend/`
- **Backend** — FastAPI via `api/index.py` (rewrites `/api/v1/*`, `/api/docs`)

Environment variables to set in Vercel:

| Variable | Notes |
|----------|-------|
| `GEMINI_API_KEY` | Required for summaries |
| `OCR_ENABLED` | Set `false` on Vercel (Tesseract not available serverless) |
| `NEXT_PUBLIC_API_URL` | Leave empty or set to your Vercel domain for same-origin API calls |

Verify build locally (no deploy):

```bash
npx vercel build --yes
```

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) — design and extension points
- [REFLECTION.md](./REFLECTION.md) — AI tooling reflection (required for submission)

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | For summaries | — | Google AI Studio key (`AIza…` or newer `AQ.…` auth keys) |
| `GEMINI_MODEL` | No | `gemini-2.5-flash-lite` | Gemini model |
| `GEMINI_TIMEOUT_SECONDS` | No | `30` | Summary timeout |
| `OCR_ENABLED` | No | `true` | Disable on Vercel |
| `OCR_MAX_PAGES` | No | `25` | Max pages to OCR per document |
| `TESSERACT_CMD` | No | — | Path to `tesseract.exe` on Windows |
| `GEMINI_OCR_ENABLED` | No | `true` | Use Gemini vision when Tesseract is missing |
| `GEMINI_OCR_MODEL` | No | `gemini-2.5-flash-lite` | Model for vision OCR |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:8000` | Backend URL |

## Submission checklist

- [ ] GitHub repo with README, ARCHITECTURE.md, REFLECTION.md
- [ ] Working UI and API (`/api/docs`)
- [ ] AI reflection log and chat export
- [ ] No `.env`, sample PDFs, or `__pycache__` committed
- [ ] `pytest` passes locally
