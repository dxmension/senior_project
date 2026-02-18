"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import { GlassCard } from "@/components/ui/glass-card";
import type { ApiResponse, TranscriptStatus, ParsedTranscriptData } from "@/types";

interface UploadStepProps {
  onNext: (data: ParsedTranscriptData | null) => void;
  onSkip: () => void;
}

const MAX_POLLS = 30;
const POLL_INTERVAL = 2000;

export function UploadStep({ onNext, onSkip }: UploadStepProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    setError(null);
    if (accepted.length > 0) {
      const f = accepted[0];
      if (f.size > 10 * 1024 * 1024) {
        setError("File size exceeds 10MB limit");
        return;
      }
      setFile(f);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
  });

  const pollStatus = async (): Promise<ParsedTranscriptData | null> => {
    for (let i = 0; i < MAX_POLLS; i++) {
      await new Promise((r) => setTimeout(r, POLL_INTERVAL));
      const res = await api.get<ApiResponse<TranscriptStatus>>("/transcripts/status");
      const status = res.data;

      if (status.status === "completed" && status.parsed_data) {
        const pd = status.parsed_data as Record<string, unknown>;
        const courses = (pd.courses as Array<Record<string, unknown>>) || [];
        return {
          major: (pd.student_info as Record<string, unknown>)?.major as string | null,
          gpa: status.gpa,
          total_credits_earned: status.total_credits_earned,
          total_credits_enrolled: status.total_credits_enrolled,
          courses: courses.map((c) => ({
            code: (c.code as string) || "",
            title: (c.title as string) || "",
            semester: (c.semester as string) || "",
            term: Number(c.term) || 0,
            grade: (c.grade as string) || "",
            grade_points: Number(c.grade_points) || 0,
            ects: Number(c.ects) || 0,
          })),
        };
      }

      if (status.status === "failed") {
        throw new Error(status.error_message || "Parsing failed");
      }
    }
    throw new Error("Parsing timed out. Please try again.");
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      await api.uploadFile<ApiResponse<TranscriptStatus>>("/transcripts/upload", file);
      setUploading(false);
      setPolling(true);
      const parsed = await pollStatus();
      setPolling(false);
      onNext(parsed);
    } catch (err) {
      setUploading(false);
      setPolling(false);
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (polling) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Spinner size={36} text="Parsing your transcript..." />
        <p className="text-xs text-text-muted mt-4">
          This may take up to 60 seconds
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-1">
          Upload Transcript
        </h2>
        <p className="text-sm text-text-secondary">
          Upload your NU transcript PDF to automatically import your courses and grades.
        </p>
      </div>

      <GlassCard>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-[var(--radius-md)] p-10 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-accent-green bg-accent-green-dim"
              : "border-border-light hover:border-text-muted"
          }`}
        >
          <input {...getInputProps()} />
          <Upload size={36} className="mx-auto mb-3 text-text-muted" />
          <p className="text-sm text-text-secondary">
            {isDragActive
              ? "Drop your PDF here"
              : "Drag & drop your transcript PDF, or click to browse"}
          </p>
          <p className="text-xs text-text-muted mt-1">PDF only, max 10MB</p>
        </div>
      </GlassCard>

      {file && (
        <div className="glass-card-sm flex items-center gap-3 p-4">
          <FileText size={20} className="text-accent-green shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm text-text-primary truncate">{file.name}</p>
            <p className="text-xs text-text-muted">{formatSize(file.size)}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-[var(--radius-sm)] bg-accent-red-dim text-accent-red text-sm">
          <AlertCircle size={16} className="shrink-0" />
          {error}
        </div>
      )}

      <div className="flex flex-col gap-3">
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="btn-primary w-full"
        >
          {uploading ? "Uploading..." : "Upload & Parse"}
        </button>
        <button
          onClick={onSkip}
          className="text-sm text-text-muted hover:text-text-secondary transition-colors text-center"
        >
          Skip and enter manually
        </button>
      </div>
    </div>
  );
}
