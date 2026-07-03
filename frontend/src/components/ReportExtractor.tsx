"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

import { ErrorDisplay } from "@/components/ErrorDisplay";
import { ExtractionResults } from "@/components/ExtractionResults";
import { UploadZone } from "@/components/UploadZone";
import { WarningsBanner } from "@/components/WarningsBanner";
import { ExtractApiError, ExtractionResponse, extractReport, fetchHealth, HealthResponse, } from "@/lib/api";

export function ReportExtractor() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ExtractionResponse | null>(null);
  const [error, setError] = useState<ExtractApiError | Error | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  useEffect(() => {
    void handleRefreshHealth();
  }, []);

  const handleRefreshHealth = async () => {
    setHealthLoading(true);
    try {
      const data = await fetchHealth();
      setHealth(data);
      setHealthError(null);
    } catch (err) {
      setHealth(null);
      setHealthError(err instanceof Error ? err.message : "Backend unavailable");
    } finally {
      setHealthLoading(false);
    }
  };

  const backendOnline = health?.status === "ok";

  const handleExtract = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await extractReport(file);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Extraction failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-full flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center px-6 py-4">
          <Image
            src="/logos-labs.png"
            alt="LogosLabs"
            width={180}
            height={48}
            className="h-10 w-auto"
            priority
          />
        </div>
      </header>

      <main className="mx-auto w-full max-w-4xl flex-1 space-y-6 px-6 py-10">
        {!healthLoading && !backendOnline && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {healthError ?? "Backend is unavailable. Start the API server and refresh."}
            <button
              type="button"
              onClick={handleRefreshHealth}
              className="ml-2 font-medium underline"
            >
              Retry
            </button>
          </div>
        )}

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <UploadZone
            selectedFile={file}
            disabled={loading || healthLoading || !backendOnline}
            onFileSelect={(selected) => {
              if (
                selected.type !== "application/pdf" &&
                !selected.name.toLowerCase().endsWith(".pdf")
              ) {
                setError(
                  new ExtractApiError(
                    "unsupported_media_type",
                    "Only PDF files are accepted.",
                  ),
                );
                return;
              }
              setFile(selected);
              setResult(null);
              setError(null);
            }}
          />

          <div className="mt-4 flex items-center gap-3">
            <button
              type="button"
              onClick={handleExtract}
              disabled={!file || loading || healthLoading || !backendOnline}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {loading ? "Extracting…" : "Extract report"}
            </button>
            {loading && (
              <span className="text-sm text-slate-500">
                Processing document…
              </span>
            )}
          </div>
        </section>

        <ErrorDisplay error={error} />

        {result && (
          <>
            <WarningsBanner warnings={result.warnings} />
            <ExtractionResults result={result} />
          </>
        )}

        {health && (
          <section className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="text-sm font-medium text-slate-700">
              Supported report types
            </h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {health.supported_report_types.map((type) => (
                <span
                  key={type}
                  className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-600"
                >
                  {type.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 text-center text-sm text-slate-500">
        © 2026 LogosLabs. All rights reserved.
      </footer>
    </div>
  );
}
