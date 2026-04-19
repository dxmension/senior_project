"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import {
  AlertCircle,
  BookMarked,
  CheckCircle2,
  FileText,
  Loader2,
  Upload,
} from "lucide-react";
import { api } from "@/lib/api";
import { GlassCard } from "@/components/ui/glass-card";
import type { ApiResponse, HandbookStatus, HandbookUploadResult } from "@/types";

interface HandbookUploadProps {
  currentEnrollmentYear: number | null;
  onUploaded: (year: number) => void;
}

export function HandbookUpload({ currentEnrollmentYear, onUploaded }: HandbookUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [year, setYear] = useState<string>(
    currentEnrollmentYear ? String(currentEnrollmentYear) : ""
  );
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<HandbookStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    setError(null);
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file || !year) return;
    const yearNum = parseInt(year, 10);
    if (isNaN(yearNum) || yearNum < 2010 || yearNum > 2030) {
      setError("Enter a valid enrollment year (2010–2030).");
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const form = new FormData();
      form.append("enrollment_year", String(yearNum));
      form.append("file", file);

      const res = await api.postForm<ApiResponse<HandbookUploadResult>>(
        "/handbook/upload",
        form
      );

      if (res.data.status === "completed") {
        // Fetch full status to get majors list
        const statusRes = await api.get<ApiResponse<HandbookStatus>>(
          `/handbook/${yearNum}`
        );
        setResult(statusRes.data);
        onUploaded(yearNum);
      } else {
        setError(res.data.status === "failed"
          ? "Parsing failed — check the PDF and try again."
          : "Upload queued — refresh in a moment.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  if (result) {
    return (
      <GlassCard>
        <div className="flex items-start gap-3">
          <CheckCircle2 size={18} className="text-accent-green shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-text-primary">
              Handbook parsed — {result.enrollment_year}
            </p>
            <p className="text-xs text-text-muted mt-0.5">
              {result.majors_parsed.length} programs found:{" "}
              {result.majors_parsed.slice(0, 5).join(", ")}
              {result.majors_parsed.length > 5 && " …"}
            </p>
            <button
              type="button"
              onClick={() => setResult(null)}
              className="text-xs text-accent-blue mt-2 hover:underline"
            >
              Upload another
            </button>
          </div>
        </div>
      </GlassCard>
    );
  }

  return (
    <GlassCard>
      <div className="flex items-center gap-2 mb-3">
        <BookMarked size={15} className="text-accent-blue shrink-0" />
        <span className="text-sm font-medium text-text-primary">Upload Academic Handbook</span>
      </div>
      <p className="text-xs text-text-muted mb-4">
        Upload your cohort's handbook PDF so the audit uses the exact
        degree requirements from your enrollment year.
      </p>

      <div className="space-y-3">
        <div>
          <label className="block text-xs text-text-muted mb-1">
            Enrollment Year
          </label>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            placeholder="e.g. 2021"
            min={2010}
            max={2030}
            className="glass-input w-full px-3 py-2 text-sm"
          />
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-md p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-accent-blue bg-accent-blue/5"
              : "border-border-light hover:border-text-muted"
          }`}
        >
          <input {...getInputProps()} />
          <Upload size={24} className="mx-auto mb-2 text-text-muted" />
          <p className="text-xs text-text-secondary">
            {isDragActive ? "Drop PDF here" : "Drag & drop handbook PDF, or click to browse"}
          </p>
        </div>

        {file && (
          <div className="flex items-center gap-2 p-2 rounded bg-bg-elevated">
            <FileText size={14} className="text-accent-green shrink-0" />
            <span className="text-xs text-text-secondary truncate flex-1">{file.name}</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 text-xs text-accent-red">
            <AlertCircle size={13} className="shrink-0" />
            {error}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || !year || uploading}
          className="btn-primary w-full text-sm flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              Parsing handbook…
            </>
          ) : (
            "Parse & Save Requirements"
          )}
        </button>
      </div>
    </GlassCard>
  );
}
