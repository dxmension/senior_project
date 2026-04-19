"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useDropzone } from "react-dropzone";
import {
  Clock3,
  FileText,
  FolderOpen,
  Library,
  Trash2,
  Upload,
  X,
} from "lucide-react";

import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { GlassCard } from "@/components/ui/glass-card";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  EnrollmentItem,
  SharedCourseMaterial,
  StudyMaterialUpload,
} from "@/types";

const MAX_STAGED_FILES = 10;

const ACCEPTED_FILES = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    [".docx"],
  "application/vnd.openxmlformats-officedocument.presentationml.presentation":
    [".pptx"],
  "image/png": [".png"],
  "image/jpeg": [".jpg", ".jpeg"],
};

type MaterialTab = "mine" | "shared";
type DeleteTarget =
  | { kind: "upload"; id: number; name: string }
  | { kind: "library"; uploadId: number; name: string }
  | null;

interface CourseMaterialsPanelProps {
  enrollment: EnrollmentItem;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatMaterialDate(isoString: string): string {
  return new Date(isoString).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getFileKey(file: File): string {
  return `${file.name}:${file.size}:${file.lastModified}`;
}

function pluralize(count: number, label: string): string {
  return `${count} ${label}${count === 1 ? "" : "s"}`;
}

function mergeStagedFiles(currentFiles: File[], incomingFiles: File[]) {
  const nextFiles = [...currentFiles];
  const existingKeys = new Set(currentFiles.map(getFileKey));
  let duplicateCount = 0;
  let overflowCount = 0;

  for (const file of incomingFiles) {
    const fileKey = getFileKey(file);
    if (existingKeys.has(fileKey)) {
      duplicateCount += 1;
      continue;
    }
    if (nextFiles.length >= MAX_STAGED_FILES) {
      overflowCount += 1;
      continue;
    }
    existingKeys.add(fileKey);
    nextFiles.push(file);
  }

  return { nextFiles, duplicateCount, overflowCount };
}

function getStagingMessage(duplicateCount: number, overflowCount: number) {
  if (duplicateCount === 0 && overflowCount === 0) return null;
  const messages: string[] = [];

  if (duplicateCount > 0) {
    messages.push(`${pluralize(duplicateCount, "duplicate file")} skipped`);
  }
  if (overflowCount > 0) {
    messages.push(
      `${pluralize(overflowCount, "file")} not added. Stage up to ${MAX_STAGED_FILES} files`
    );
  }

  return messages.join(". ");
}

function uploadStatusTone(status: string): string {
  if (status === "failed") return "text-accent-red bg-accent-red-dim";
  if (status === "completed") return "text-accent-green bg-accent-green-dim";
  return "text-accent-blue bg-accent-blue-dim";
}

function curationLabel(item: StudyMaterialUpload): string {
  if (item.is_published) return "Published to shared library";
  if (item.curation_status === "pending") return "On curation";
  if (item.curation_status === "rejected") return "Curation rejected";
  return "Private upload";
}

function curationTone(status: string): string {
  if (status === "published") return "text-accent-green";
  if (status === "pending") return "text-accent-blue";
  if (status === "rejected") return "text-accent-red";
  return "text-text-secondary";
}

const MATERIAL_NAME_STYLE = {
  maxWidth: "clamp(180px, 48vw, 420px)",
};

const MATERIAL_META_STYLE = {
  maxWidth: "clamp(220px, 56vw, 520px)",
};

export function CourseMaterialsPanel({
  enrollment,
}: CourseMaterialsPanelProps) {
  const [tab, setTab] = useState<MaterialTab>("mine");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [week, setWeek] = useState("1");
  const [files, setFiles] = useState<File[]>([]);
  const [requestShared, setRequestShared] = useState(false);
  const [uploads, setUploads] = useState<StudyMaterialUpload[]>([]);
  const [library, setLibrary] = useState<SharedCourseMaterial[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [batchIds, setBatchIds] = useState<number[]>([]);
  const [actingId, setActingId] = useState<number | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget>(null);
  const previousHasActiveUploads = useRef(false);

  const loadUploads = useCallback(async () => {
    const courseId = enrollment.course_id;
    const response = await api.get<ApiResponse<StudyMaterialUpload[]>>(
      `/course-materials/${courseId}/uploads`
    );
    setUploads(response.data ?? []);
  }, [enrollment.course_id]);

  const loadLibrary = useCallback(async () => {
    const courseId = enrollment.course_id;
    const response = await api.get<ApiResponse<SharedCourseMaterial[]>>(
      `/course-materials/${courseId}/library`
    );
    setLibrary(response.data ?? []);
  }, [enrollment.course_id]);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([loadUploads(), loadLibrary()]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load materials";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [loadLibrary, loadUploads]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  const hasActiveUploads = useMemo(
    () =>
      uploads.some(
        (item) =>
          item.upload_status === "queued" ||
          item.upload_status === "uploading"
      ),
    [uploads]
  );

  useEffect(() => {
    if (!hasActiveUploads) return;
    const timer = window.setInterval(() => {
      void loadUploads().catch(() => undefined);
    }, 2000);
    return () => window.clearInterval(timer);
  }, [hasActiveUploads, loadUploads]);

  useEffect(() => {
    const didFinish = previousHasActiveUploads.current && !hasActiveUploads;
    previousHasActiveUploads.current = hasActiveUploads;
    if (!didFinish) return;
    void loadLibrary().catch(() => undefined);
  }, [hasActiveUploads, loadLibrary]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const result = mergeStagedFiles(files, acceptedFiles);
    setFiles(result.nextFiles);
    setError(getStagingMessage(result.duplicateCount, result.overflowCount));
  }, [files]);

  const removeStagedFile = useCallback((fileToRemove: File) => {
    const fileKey = getFileKey(fileToRemove);
    setFiles((currentFiles) =>
      currentFiles.filter((file) => getFileKey(file) !== fileKey)
    );
    setError(null);
  }, []);

  const {
    getInputProps,
    getRootProps,
    isDragActive,
    open: openPicker,
  } = useDropzone({
    onDrop,
    noClick: true,
    accept: ACCEPTED_FILES,
  });

  const batchUploads = uploads.filter((item) => batchIds.includes(item.id));
  const completedCount = batchUploads.filter(
    (item) => item.upload_status === "completed"
  ).length;
  const batchProgress = batchUploads.length
    ? Math.round((completedCount / batchUploads.length) * 100)
    : 0;
  const isBatchActive = batchUploads.length > 0 && hasActiveUploads;
  const isBatchComplete = batchUploads.length > 0 && !hasActiveUploads;

  async function handleSubmit() {
    if (!files.length) {
      setError("Select at least one file.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const response = await api.uploadFiles<ApiResponse<StudyMaterialUpload[]>>(
        `/course-materials/${enrollment.course_id}/uploads`,
        files,
        {
          week,
          request_shared_library: String(requestShared),
        }
      );
      const created = response.data ?? [];
      setBatchIds(created.map((item) => item.id));
      setFiles([]);
      setTab("mine");
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  async function deleteMaterial(target: DeleteTarget) {
    if (!target) return;
    const uploadId = target.kind === "upload" ? target.id : target.uploadId;
    setActingId(uploadId);
    try {
      await api.delete<ApiResponse>(
        `/course-materials/${enrollment.course_id}/uploads/${uploadId}`
      );
      setDeleteTarget(null);
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Delete failed";
      setError(message);
    } finally {
      setActingId(null);
    }
  }

  async function cancelPublish(uploadId: number) {
    setActingId(uploadId);
    setError(null);
    try {
      await api.post<ApiResponse<StudyMaterialUpload>>(
        `/course-materials/${enrollment.course_id}/uploads/${uploadId}/cancel-publish`
      );
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Cancel publish failed";
      setError(message);
    } finally {
      setActingId(null);
    }
  }

  function closeUploadModal() {
    if (submitting) return;
    setUploadModalOpen(false);
    setFiles([]);
    setError(null);
  }

  function openMaterial(url: string | null) {
    if (!url) return;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <>
      <GlassCard padding={false} className="overflow-hidden">
        <div className="border-b border-border-primary px-5 py-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h2 className="text-base font-semibold text-text-primary">
                Course Materials
              </h2>
              <p className="mt-1 text-sm text-text-secondary">
                Upload private notes or send files to the shared library for curation.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setUploadModalOpen(true)}
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary transition-transform hover:scale-[1.02]"
            >
              <FolderOpen size={16} />
              Add course materials
            </button>
          </div>
        </div>

        {error ? (
          <div className="border-b border-border-primary px-5 py-4">
            <p className="rounded-xl bg-accent-red-dim px-3 py-2 text-sm text-accent-red">
              {error}
            </p>
          </div>
        ) : null}

        <div className="flex min-h-[520px] flex-col">
            <div className="flex border-b border-border-primary">
              {(["mine", "shared"] as const).map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setTab(item)}
                  className={`flex-1 px-4 py-3 text-sm transition-colors ${
                    tab === item
                      ? "border-b-2 border-accent-green text-text-primary"
                      : "text-text-secondary hover:text-text-primary"
                  }`}
                >
                  {item === "mine" ? "My uploads" : "Shared library"}
                </button>
              ))}
            </div>

          <div className="flex-1 overflow-y-auto p-5">
            {loading ? (
              <p className="text-sm text-text-secondary">Loading materials...</p>
            ) : tab === "mine" ? (
              <div className="space-y-3">
                {uploads.length === 0 ? (
                  <p className="text-sm text-text-secondary">
                    Your uploaded course materials will appear here.
                  </p>
                ) : (
                  uploads.map((item) => {
                    const canCancel =
                      item.publish_requested &&
                      (item.curation_status === "pending" || item.is_published);
                    return (
                      <div
                        key={item.id}
                        onClick={() => openMaterial(item.download_url)}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            openMaterial(item.download_url);
                          }
                        }}
                        role="button"
                        tabIndex={item.download_url ? 0 : -1}
                          className="w-full rounded-2xl border border-border-primary bg-white/[0.03] p-4 text-left transition-colors hover:border-accent-green/40 hover:bg-white/[0.05]"
                        >
                          <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                            <div className="min-w-0 flex-1">
                              <p
                                className="truncate text-sm font-medium text-text-primary"
                                style={MATERIAL_NAME_STYLE}
                                title={item.original_filename}
                              >
                                {item.original_filename}
                              </p>
                            <p className="mt-1 text-xs text-text-secondary">
                              Week {item.week} · {formatFileSize(item.file_size_bytes)}
                            </p>
                            <p className="mt-1 text-xs text-text-secondary">
                              {formatMaterialDate(item.created_at)}
                            </p>
                          </div>
                          <span
                            className={`self-start rounded-full px-2 py-1 text-[11px] uppercase tracking-wide ${uploadStatusTone(
                              item.upload_status
                            )}`}
                          >
                            {item.upload_status}
                          </span>
                        </div>

                        <div className="mt-3 flex items-center gap-2">
                          <Clock3 size={14} className="text-text-secondary" />
                          <span
                            className={`text-xs ${curationTone(
                              item.curation_status
                            )}`}
                          >
                            {curationLabel(item)}
                          </span>
                        </div>

                        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs">
                          {canCancel ? (
                            <button
                              type="button"
                              disabled={actingId === item.id}
                              onClick={(event) => {
                                event.stopPropagation();
                                void cancelPublish(item.id);
                              }}
                              className="text-accent-blue transition-opacity hover:opacity-80 disabled:opacity-50"
                            >
                              Cancel publish
                            </button>
                          ) : null}
                          <button
                            type="button"
                            disabled={actingId === item.id}
                            onClick={(event) => {
                              event.stopPropagation();
                              setDeleteTarget({
                                kind: "upload",
                                id: item.id,
                                name: item.original_filename,
                              });
                            }}
                            className="text-accent-red transition-opacity hover:opacity-80 disabled:opacity-50"
                          >
                            Delete
                          </button>
                        </div>

                        {item.error_message ? (
                          <p className="mt-2 text-xs text-accent-red">
                            {item.error_message}
                          </p>
                        ) : null}
                      </div>
                    );
                  })
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {library.length === 0 ? (
                  <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4 text-sm text-text-secondary">
                    Shared course materials curated by admins will appear here.
                  </div>
                ) : (
                  library.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => openMaterial(item.download_url)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          openMaterial(item.download_url);
                        }
                      }}
                      role="button"
                      tabIndex={item.download_url ? 0 : -1}
                      className="w-full rounded-2xl border border-border-primary bg-white/[0.03] p-4 text-left transition-colors hover:border-accent-green/40 hover:bg-white/[0.05]"
                    >
                      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <Library
                              size={14}
                              className="mt-0.5 shrink-0 text-accent-green"
                            />
                            <p
                              className="truncate text-sm font-medium text-text-primary"
                              style={MATERIAL_NAME_STYLE}
                              title={item.title}
                            >
                              {item.title}
                            </p>
                          </div>
                          <p
                            className="mt-1 truncate text-xs text-text-secondary"
                            style={MATERIAL_META_STYLE}
                            title={`Week ${item.week} · ${item.original_filename}`}
                          >
                            Week {item.week} · {item.original_filename}
                          </p>
                          <p className="mt-1 text-xs text-text-secondary">
                            Added {formatMaterialDate(item.published_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3 text-sm">
                          {item.is_owned_by_current_user ? (
                            <button
                              type="button"
                              disabled={actingId === item.upload_id}
                              onClick={(event) => {
                                event.stopPropagation();
                                setDeleteTarget({
                                  kind: "library",
                                  uploadId: item.upload_id,
                                  name: item.title,
                                });
                              }}
                              className="inline-flex items-center gap-1 text-accent-red transition-opacity hover:opacity-80 disabled:opacity-50"
                            >
                              <Trash2 size={14} />
                              Delete
                            </button>
                          ) : null}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </GlassCard>

      {uploadModalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl border border-border-primary bg-bg-primary shadow-2xl">
            <div className="flex items-center justify-between border-b border-border-primary px-6 py-5">
              <div>
                <h3 className="text-lg font-semibold text-text-primary">
                  Add course materials
                </h3>
                <p className="mt-1 text-sm text-text-secondary">
                  Drop files here, choose the week, and set whether the upload stays private or goes to shared library curation.
                </p>
              </div>
              <button
                type="button"
                onClick={closeUploadModal}
                className="rounded-full p-2 text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
                aria-label="Close upload modal"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-5 p-6">
              {batchUploads.length > 0 ? (
                <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4">
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-text-primary">Current batch</span>
                    <span className="text-text-secondary">
                      {completedCount}/{batchUploads.length} completed
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-border-primary">
                    <div
                      className="h-2 rounded-full bg-accent-green transition-all"
                      style={{ width: `${batchProgress}%` }}
                    />
                  </div>
                </div>
              ) : null}

              <div
                {...getRootProps()}
                className={`rounded-2xl border-2 border-dashed p-6 transition-colors ${
                  isDragActive
                    ? "border-accent-green bg-accent-green-dim"
                    : "border-border-primary bg-white/[0.02]"
                }`}
              >
                <input {...getInputProps()} />
                <div className="flex items-start gap-3">
                  <Upload size={24} className="mt-0.5 shrink-0 text-accent-green" />
                  <div>
                    <p className="text-sm font-medium text-text-primary">
                      {isDragActive
                        ? "Drop files here"
                        : "Drag files here or use browse to choose them"}
                    </p>
                    <p className="mt-1 text-xs text-text-secondary">
                      PDF, DOCX, PPTX, PNG, JPG. Up to 10 files, 25MB each.
                    </p>
                    <button
                      type="button"
                      onClick={openPicker}
                      className="mt-3 inline-flex items-center gap-2 rounded-2xl border border-border-primary px-3 py-1.5 text-xs font-medium text-text-primary transition-colors hover:bg-white/5"
                    >
                      <FolderOpen size={14} />
                      Browse files
                    </button>
                  </div>
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-[120px_1fr]">
                <label className="text-xs text-text-secondary">
                  Week
                  <select
                    value={week}
                    onChange={(e) => setWeek(e.target.value)}
                    className="glass-input mt-1 w-full px-3 py-2 text-sm"
                  >
                    {Array.from({ length: 15 }, (_, idx) => idx + 1).map((value) => (
                      <option key={value} value={value}>
                        Week {value}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="text-xs text-text-secondary">
                  Privacy
                  <select
                    value={requestShared ? "shared" : "private"}
                    onChange={(e) => setRequestShared(e.target.value === "shared")}
                    className="glass-input mt-1 w-full px-3 py-2 text-sm"
                  >
                    <option value="private">Private upload</option>
                    <option value="shared">Send to shared library</option>
                  </select>
                </label>
              </div>

              {files.length > 0 ? (
                <div className="space-y-2">
                  {files.map((file) => (
                    <div
                      key={getFileKey(file)}
                      className="glass-card-sm flex items-start gap-3 p-3"
                    >
                      <FileText
                        size={18}
                        className="mt-0.5 shrink-0 text-accent-green"
                      />
                      <div className="min-w-0 flex-1">
                        <p
                          className="truncate text-sm text-text-primary"
                          title={file.name}
                        >
                          {file.name}
                        </p>
                        <p className="mt-1 text-xs text-text-secondary">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeStagedFile(file)}
                        className="rounded-lg p-1.5 text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
                        aria-label={`Remove ${file.name}`}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4 text-sm text-text-secondary">
                  No files selected yet.
                </div>
              )}

              <p className="text-xs text-text-secondary">
                {requestShared
                  ? "Files sent to the shared library appear as On curation until reviewed."
                  : "Private uploads stay visible only in your materials list."}
              </p>

              {error ? (
                <p className="rounded-xl bg-accent-red-dim px-3 py-2 text-sm text-accent-red">
                  {error}
                </p>
              ) : null}

              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={closeUploadModal}
                  className="w-full rounded-2xl border border-border-primary px-4 py-2 text-sm text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary disabled:opacity-50"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => void handleSubmit()}
                  disabled={submitting || files.length === 0 || isBatchActive}
                  className="w-full rounded-2xl bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary transition-opacity hover:opacity-90 disabled:opacity-40"
                >
                  {submitting
                    ? "Queueing..."
                    : isBatchActive
                      ? `Uploading ${batchProgress}%`
                      : isBatchComplete && files.length === 0
                        ? "Upload complete"
                        : "Upload batch"}
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <ConfirmDialog
        isOpen={deleteTarget !== null}
        title="Delete material"
        message={
          deleteTarget
            ? `Delete "${deleteTarget.name}" from course materials?`
            : ""
        }
        confirmLabel={actingId ? "Deleting..." : "Delete"}
        variant="danger"
        onConfirm={() => void deleteMaterial(deleteTarget)}
        onCancel={() => {
          if (actingId) return;
          setDeleteTarget(null);
        }}
      />
    </>
  );
}
