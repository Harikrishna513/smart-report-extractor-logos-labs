"use client";

import { WARNING_MESSAGES } from "@/lib/api";

type WarningsBannerProps = {
  warnings: string[];
};

export function WarningsBanner({ warnings }: WarningsBannerProps) {
  if (warnings.length === 0) return null;

  return (
    <div className="space-y-2">
      {warnings.map((code) => (
        <div
          key={code}
          className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          {WARNING_MESSAGES[code] ?? code}
        </div>
      ))}
    </div>
  );
}
