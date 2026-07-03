# Smart Report Extractor

## Overview

Smart Report Extractor is a web application that extracts structured information from medical PDF reports and generates a short summary of the report.

The project was built as part of the Logos Labs AI Engineer take-home assignment. The focus of the implementation is on clean architecture, deterministic extraction, and keeping the LLM limited to summarization instead of using it for document understanding.

Version 1 supports the following report types:

- CBC Report
- ECG Report
- Prescription
- Discharge Summary
- Health Checkup Report

Documents outside this scope are rejected with a clear error message instead of attempting a best-effort extraction.

---

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- Pydantic v2
- pdfplumber
- PyMuPDF
- Tesseract OCR (fallback)
- Gemini API (summary generation)
- Pytest

### Frontend

- Next.js
- TypeScript

### Deployment

- Vercel

---

## Why this approach?

The assignment allows complete freedom in how the extraction pipeline is designed.

Instead of relying on an LLM for everything, I chose a deterministic pipeline for document validation, report classification, and field extraction. This makes the system easier to test, explain, and maintain.

Gemini is only used to generate a human-readable summary after structured data has already been extracted.

This keeps API usage low while making the extraction process predictable.

---

## Extraction Flow

1. Upload PDF
2. Validate file
3. Extract text
4. Detect whether the document is a supported medical report
5. Classify the report type
6. Extract structured fields
7. Generate a summary
8. Return the response

If any step fails, the API returns a descriptive error instead of continuing with incorrect data.

---

## Running the project

### Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -e ".[dev]"

python -m uvicorn app.main:app --reload
```

API

```
http://localhost:8000
```

Swagger

```
http://localhost:8000/api/docs
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend

```
http://localhost:3000
```

---

## Environment Variables

Copy

```
.env.example
```

to

```
.env
```

and update

```
GEMINI_API_KEY
```

OCR is optional.

If Tesseract is installed locally it will be used automatically.

---

## Running Tests

```bash
cd backend

pytest
```

---

## Project Structure

```
backend/
    app/
    tests/

frontend/
    src/

api/
    index.py

docker-compose.yml

README.md

ARCHITECTURE.md

ENGINEERING_PLAN.md

REFLECTION.md
```

---

## Current Limitations

Version 1 intentionally keeps the scope small.

Supported

- Medical reports
- Digital PDFs
- OCR fallback for scanned PDFs

Not supported

- Invoices
- Bank statements
- Resume parsing
- Medical image interpretation
- Handwritten notes

---

## Future Improvements

The application is designed so new components can be added without changing the extraction workflow.

Some planned extensions are:

- Google Drive integration
- AWS S3 storage
- Database for document history
- Semantic search
- RAG over previously processed reports
- Additional medical report types
- Background processing for large documents

---

## Documentation

The repository also contains:

- ENGINEERING_PLAN.md
- ARCHITECTURE.md
- REFLECTION.md

These documents explain the design decisions, implementation approach, and how AI tools were used during development.