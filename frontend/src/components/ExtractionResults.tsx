"use client";

import { ExtractionResponse } from "@/lib/api";

function formatLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function FieldRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-3 gap-2 border-b border-slate-100 py-2 last:border-0">
      <dt className="col-span-1 text-sm text-slate-500">{label}</dt>
      <dd className="col-span-2 text-sm text-slate-900">{value}</dd>
    </div>
  );
}

function renderValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (Array.isArray(value)) {
    if (value.length === 0) return "—";
    return value
      .map((item) =>
        typeof item === "object" && item !== null
          ? Object.entries(item)
              .map(([k, v]) => `${k}: ${v}`)
              .join(", ")
          : String(item),
      )
      .join("; ");
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>).filter(
      ([, v]) => v !== null && v !== "",
    );
    if (entries.length === 0) return "—";
    return entries.map(([k, v]) => `${formatLabel(k)}: ${v}`).join("; ");
  }
  return String(value);
}

function flattenFields(
  data: Record<string, unknown>,
): { label: string; value: string }[] {
  const rows: { label: string; value: string }[] = [];

  for (const [key, value] of Object.entries(data)) {
    if (key === "report_type") continue;

    if (
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(value) &&
      Object.keys(value as object).length > 0
    ) {
      for (const [nestedKey, nestedValue] of Object.entries(
        value as Record<string, unknown>,
      )) {
        rows.push({
          label: `${formatLabel(key)} — ${formatLabel(nestedKey)}`,
          value: renderValue(nestedValue),
        });
      }
    } else {
      rows.push({ label: formatLabel(key), value: renderValue(value) });
    }
  }

  return rows;
}

type ExtractionResultsProps = {
  result: ExtractionResponse;
};

export function ExtractionResults({ result }: ExtractionResultsProps) {
  const fields = flattenFields(result.extracted_data);
  const showLowConfidence = result.confidence < 0.85;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
          {result.report_type.replace(/_/g, " ")}
        </span>
        {showLowConfidence && (
          <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
            Confidence: {(result.confidence * 100).toFixed(0)}%
          </span>
        )}
        <span className="text-xs text-slate-500">
          {result.metadata.duration_ms} ms · {result.metadata.page_count} page
          {result.metadata.page_count !== 1 ? "s" : ""} · {result.metadata.extraction_method}
        </span>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Extracted fields</h3>
        <dl className="mt-3">
          {fields.map((field) => (
            <FieldRow key={field.label} label={field.label} value={field.value} />
          ))}
        </dl>
      </section>

      {result.summary && (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold text-slate-900">Summary</h3>
          <p className="mt-2 text-sm leading-relaxed text-slate-700">
            {result.summary}
          </p>
        </section>
      )}
    </div>
  );
}
