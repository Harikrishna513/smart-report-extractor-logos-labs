"use client";

import { ExtractApiError, ERROR_MESSAGES } from "@/lib/api";

type ErrorDisplayProps = {
  error: ExtractApiError | Error | null;
};

export function ErrorDisplay({ error }: ErrorDisplayProps) {
  if (!error) return null;

  const code = error instanceof ExtractApiError ? error.code : "unknown_error";
  const message =
    error instanceof ExtractApiError
      ? ERROR_MESSAGES[code] ?? error.message
      : error.message;

  const details =
    error instanceof ExtractApiError ? error.details : undefined;
  const supportedTypes = details?.supported_types as string[] | undefined;

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <h3 className="text-sm font-semibold text-red-800">Extraction failed</h3>
      <p className="mt-1 text-sm text-red-700">{message}</p>
      {supportedTypes && supportedTypes.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-red-800">Supported formats:</p>
          <div className="mt-1 flex flex-wrap gap-1.5">
            {supportedTypes.map((type) => (
              <span
                key={type}
                className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800"
              >
                {type.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </div>
      )}
      {code === "unsupported_report_type" && details?.confidence !== undefined && (
        <p className="mt-2 text-xs text-red-600">
          Classification confidence: {String(details.confidence)}
        </p>
      )}
    </div>
  );
}
