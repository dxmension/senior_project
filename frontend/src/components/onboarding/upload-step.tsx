"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import { GlassCard } from "@/components/ui/glass-card";
import type { ApiResponse } from "@/types";

interface UploadStepProps {
  onNext: () => void;
  onSkip: () => void;
}

export function UploadStep({ onNext, onSkip }: UploadStepProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
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

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      await api.uploadFile<ApiResponse>("/transcripts/uploads", file);
      setUploading(false);
      // Transcript is processed synchronously, just move to next step
      onNext();
    } catch (err) {
      setUploading(false);
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  
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
          className={`border-2 border-dashed rounded-md p-10 text-center cursor-pointer transition-colors ${
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
        <div className="flex items-center gap-2 p-3 rounded-sm)] bg-accent-red-dim text-accent-red text-sm">
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
