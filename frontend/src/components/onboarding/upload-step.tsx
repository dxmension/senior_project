"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle, Languages } from "lucide-react";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import { GlassCard } from "@/components/ui/glass-card";
import type { ApiResponse } from "@/types";

const KLL_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

interface UploadStepProps {
  onNext: () => void;
  onSkip: () => void;
}

export function UploadStep({ onNext, onSkip }: UploadStepProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Phase 2: after upload succeeds, ask for Kazakh level
  const [uploaded, setUploaded] = useState(false);
  const [kazakhLevel, setKazakhLevel] = useState("");
  const [saving, setSaving] = useState(false);

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
      setUploaded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleContinue = async () => {
    setSaving(true);
    try {
      if (kazakhLevel) {
        await api.patch<ApiResponse>("/profile", { kazakh_level: kazakhLevel });
      }
      onNext();
    } catch {
      // Non-critical — proceed anyway
      onNext();
    } finally {
      setSaving(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // ── Phase 2: transcript uploaded, ask for Kazakh level ──────────────────
  if (uploaded) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary mb-1">
            One more thing
          </h2>
          <p className="text-sm text-text-secondary">
            Your transcript was uploaded successfully. Do you have a Kazakh
            language proficiency level? It determines eligibility for some courses.
          </p>
        </div>

        <GlassCard>
          <div className="flex items-start gap-3">
            <Languages size={18} className="text-accent-green shrink-0 mt-0.5" />
            <div className="flex-1 space-y-3">
              <p className="text-sm font-medium text-text-primary">
                Kazakh Language Level (KLL)
              </p>
              <select
                value={kazakhLevel}
                onChange={(e) => setKazakhLevel(e.target.value)}
                className="glass-input w-full px-3 py-2 text-sm"
              >
                <option value="">Not set — skip this</option>
                {KLL_LEVELS.map((lvl) => (
                  <option key={lvl} value={lvl}>KLL {lvl}</option>
                ))}
              </select>
              <p className="text-xs text-text-muted">
                You can change this later in your profile.
              </p>
            </div>
          </div>
        </GlassCard>

        <button
          onClick={handleContinue}
          disabled={saving}
          className="btn-primary w-full"
        >
          {saving ? "Saving…" : "Continue to Dashboard"}
        </button>
      </div>
    );
  }

  // ── Phase 1: file upload ─────────────────────────────────────────────────
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
        <div className="flex items-center gap-2 p-3 rounded-sm bg-accent-red-dim text-accent-red text-sm">
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
          {uploading ? <><Spinner />&nbsp;Uploading…</> : "Upload & Parse"}
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
