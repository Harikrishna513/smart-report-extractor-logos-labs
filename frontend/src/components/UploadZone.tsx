"use client";

import { useCallback, useState } from "react";

type UploadZoneProps = {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  selectedFile: File | null;
};

export function UploadZone({
  onFileSelect,
  disabled,
  selectedFile,
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file || disabled) return;
      onFileSelect(file);
    },
    [disabled, onFileSelect],
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFile(e.dataTransfer.files[0]);
      }}
      className={`rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
        isDragging
          ? "border-blue-400 bg-blue-50"
          : "border-slate-300 bg-slate-50 hover:border-slate-400"
      } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
    >
      <input
        type="file"
        accept="application/pdf,.pdf"
        disabled={disabled}
        className="hidden"
        id="pdf-upload"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      <label
        htmlFor="pdf-upload"
        className={disabled ? "cursor-not-allowed" : "cursor-pointer"}
      >
        <p className="text-sm font-medium text-slate-700">
          Drop a medical PDF here, or click to browse
        </p>
        <p className="mt-1 text-xs text-slate-500">PDF only, max 10 MB</p>
        {selectedFile && (
          <p className="mt-4 text-sm text-blue-700">
            Selected: <span className="font-medium">{selectedFile.name}</span>
          </p>
        )}
      </label>
    </div>
  );
}
