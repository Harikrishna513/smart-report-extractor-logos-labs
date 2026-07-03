const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV === "production" ? "" : "http://127.0.0.1:8000");

const REQUEST_TIMEOUT_MS = 5_000;

export type HealthResponse = {
  status: "ok";
  version: string;
  supported_report_types: string[];
};

export type ExtractionMetadata = {
  page_count: number;
  extraction_method: string;
  duration_ms: number;
  text_length: number;
};

export type ExtractionResponse = {
  document_id: string;
  status: "success";
  report_type: string;
  confidence: number;
  extracted_data: Record<string, unknown>;
  summary: string | null;
  warnings: string[];
  metadata: ExtractionMetadata;
};

export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
};

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/v1/health`, {
    cache: "no-store",
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

export async function extractReport(file: File): Promise<ExtractionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/v1/extract`, {
    method: "POST",
    body: formData,
  });

  const body = await response.json();
  if (!response.ok) {
    const error = body as ApiErrorBody;
    throw new ExtractApiError(
      error.error?.code ?? "unknown_error",
      error.error?.message ?? "Extraction failed",
      error.error?.details,
      response.status,
    );
  }

  return body as ExtractionResponse;
}

export class ExtractApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: Record<string, unknown>,
    public status?: number,
  ) {
    super(message);
    this.name = "ExtractApiError";
  }
}

export function getApiDocsUrl(): string {
  return `${API_URL}/api/docs`;
}

export const ERROR_MESSAGES: Record<string, string> = {
  invalid_pdf: "The file is not a valid PDF.",
  file_too_large: "The file exceeds the maximum upload size.",
  unsupported_media_type: "Only PDF files are accepted.",
  text_extraction_failed:
    "Could not read text from this document. It may be a scanned image without OCR support.",
  not_medical_document:
    "This document does not appear to be a medical report.",
  unsupported_report_type:
    "This document does not match any supported medical report format.",
  unknown_error: "Something went wrong. Please try again.",
};

export const WARNING_MESSAGES: Record<string, string> = {
  incomplete_extraction: "Some fields could not be extracted from this document.",
  ocr_used: "Text was extracted using OCR, which may affect accuracy.",
  summary_unavailable: "Structured data was extracted, but the summary could not be generated.",
  low_field_confidence: "Some extracted values have low confidence.",
};
