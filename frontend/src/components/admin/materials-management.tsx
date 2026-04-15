"use client";

import { useEffect, useState } from "react";
import { Check, FileText, ShieldAlert, Trash2, Undo2, X } from "lucide-react";

import { api } from "@/lib/api";
import type { AdminMaterialUpload, ApiResponse } from "@/types";

interface MaterialsManagementProps {
  refreshKey: number;
}

function defaultForm() {
  return { uploadId: null as number | null, title: "", week: "1" };
}

function groupByCourse(items: AdminMaterialUpload[]) {
  return items.reduce<Record<string, AdminMaterialUpload[]>>((groups, item) => {
    const key = `${item.course_code} · ${item.course_title}`;
    groups[key] = groups[key] ? [...groups[key], item] : [item];
    return groups;
  }, {});
}

const ADMIN_DOC_NAME_STYLE = {
  maxWidth: "clamp(120px, 28vw, 240px)",
};

export function MaterialsManagement({
  refreshKey,
}: MaterialsManagementProps) {
  const [materials, setMaterials] = useState<AdminMaterialUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [publishForm, setPublishForm] = useState(defaultForm());
  const [submittingId, setSubmittingId] = useState<number | null>(null);

  async function loadMaterials() {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<ApiResponse<AdminMaterialUpload[]>>(
        "/admin/materials/uploads"
      );
      setMaterials(response.data ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load materials");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadMaterials();
  }, [refreshKey]);

  async function publish(item: AdminMaterialUpload) {
    setSubmittingId(item.id);
    try {
      await api.post<ApiResponse>(
        `/admin/materials/uploads/${item.id}/publish`,
        {
          title: publishForm.title.trim() || item.original_filename,
          week: Number(publishForm.week),
        }
      );
      setPublishForm(defaultForm());
      await loadMaterials();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to publish");
    } finally {
      setSubmittingId(null);
    }
  }

  async function reject(item: AdminMaterialUpload) {
    setSubmittingId(item.id);
    try {
      await api.post<ApiResponse>(`/admin/materials/uploads/${item.id}/reject`);
      await loadMaterials();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject");
    } finally {
      setSubmittingId(null);
    }
  }

  async function unpublish(item: AdminMaterialUpload) {
    setSubmittingId(item.id);
    try {
      await api.post<ApiResponse>(
        `/admin/materials/uploads/${item.id}/unpublish`
      );
      await loadMaterials();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to unpublish");
    } finally {
      setSubmittingId(null);
    }
  }

  async function remove(item: AdminMaterialUpload) {
    setSubmittingId(item.id);
    try {
      await api.delete<ApiResponse>(`/admin/materials/uploads/${item.id}`);
      await loadMaterials();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    } finally {
      setSubmittingId(null);
    }
  }

  const groupedMaterials = groupByCourse(materials);

  return (
    <div className="glass-card min-w-0 p-6">
      <div className="mb-4 flex min-w-0 items-center gap-2">
        <FileText size={22} className="text-accent-green" />
        <div className="min-w-0">
          <h2 className="text-xl font-semibold text-text-primary">
            Materials
          </h2>
          <p className="text-sm text-text-secondary">
            Review publish requests and shared items.
          </p>
        </div>
      </div>

      {error && (
        <p className="mb-4 rounded-lg bg-accent-red-dim px-3 py-2 text-sm text-accent-red">
          {error}
        </p>
      )}

      {loading ? (
        <p className="py-10 text-center text-text-secondary">Loading uploads...</p>
      ) : materials.length === 0 ? (
        <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-8 text-center">
          <ShieldAlert size={24} className="mx-auto mb-3 text-text-secondary" />
          <p className="text-sm text-text-secondary">
            No pending or published course materials right now.
          </p>
        </div>
      ) : (
        <div className="min-w-0 space-y-4">
          {Object.entries(groupedMaterials).map(([courseLabel, items]) => (
            <div
              key={courseLabel}
              className="min-w-0 rounded-2xl border border-border-primary bg-white/[0.02] p-4"
            >
              <div className="mb-4 border-b border-border-primary pb-3">
                <p
                  className="truncate text-sm font-semibold text-text-primary"
                  title={courseLabel}
                >
                  {courseLabel}
                </p>
                <p className="text-xs text-text-secondary">
                  {items.length} uploads
                </p>
              </div>

              <div className="space-y-3">
                {items.map((item) => {
                  const isEditing = publishForm.uploadId === item.id;
                  const canPublish = item.upload_status === "completed";
                  const publishRequested = item.curation_status !== "not_requested";
                  return (
                    <div
                      key={item.id}
                      className="min-w-0 rounded-2xl border border-border-primary bg-white/[0.03] p-4"
                    >
                      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                        <div className="min-w-0 flex-1 space-y-1">
                          <div className="flex min-w-0 items-center gap-2 text-sm text-text-primary">
                            <p
                              className="truncate"
                              style={ADMIN_DOC_NAME_STYLE}
                              title={item.original_filename}
                            >
                              {item.original_filename}
                            </p>
                            <span className="shrink-0 text-text-secondary">
                              · Week {item.user_week}
                            </span>
                          </div>
                          <p className="text-xs text-text-secondary">
                            {item.uploader_name} · {item.uploader_email}
                          </p>
                          <p className="text-xs text-text-secondary">
                            {item.upload_status} / {item.curation_status}
                          </p>
                        </div>

                        <div className="min-w-0 flex flex-wrap items-center gap-2 lg:max-w-[48%] lg:justify-end">
                          {item.download_url ? (
                            <a
                              href={item.download_url}
                              target="_blank"
                              rel="noreferrer"
                              className="btn-secondary px-3 py-2 text-xs"
                            >
                              Preview
                            </a>
                          ) : null}
                          {item.curation_status !== "published" &&
                          publishRequested ? (
                            <button
                              type="button"
                              disabled={!canPublish}
                              onClick={() =>
                                setPublishForm({
                                  uploadId: item.id,
                                  title: item.shared_title ?? item.original_filename,
                                  week: String(item.shared_week ?? item.user_week),
                                })
                              }
                              className="btn-secondary px-3 py-2 text-xs disabled:opacity-50"
                            >
                              Prepare publish
                            </button>
                          ) : item.curation_status === "published" ? (
                            <button
                              type="button"
                              disabled={submittingId === item.id}
                              onClick={() => void unpublish(item)}
                              className="btn-secondary px-3 py-2 text-xs"
                            >
                              <span className="inline-flex items-center gap-1">
                                <Undo2 size={14} />
                                Unpublish
                              </span>
                            </button>
                          ) : (
                            <span className="rounded-full bg-white/[0.04] px-3 py-2 text-xs text-text-secondary">
                              Private upload
                            </span>
                          )}
                          <button
                            type="button"
                            disabled={submittingId === item.id}
                            onClick={() => void remove(item)}
                            className="rounded-lg border border-border-primary px-3 py-2 text-xs text-accent-red transition-colors hover:bg-accent-red-dim"
                          >
                            <span className="inline-flex items-center gap-1">
                              <Trash2 size={14} />
                              Delete
                            </span>
                          </button>
                        </div>
                      </div>

                      {isEditing && publishRequested ? (
                        <div className="mt-4 grid gap-3 rounded-xl border border-border-primary p-4 2xl:grid-cols-[minmax(0,1fr)_120px_auto_auto]">
                          <input
                            type="text"
                            value={publishForm.title}
                            onChange={(e) =>
                              setPublishForm((prev) => ({
                                ...prev,
                                title: e.target.value,
                              }))
                            }
                            className="glass-input px-3 py-2 text-sm"
                            placeholder="Shared library title"
                          />
                          <select
                            value={publishForm.week}
                            onChange={(e) =>
                              setPublishForm((prev) => ({
                                ...prev,
                                week: e.target.value,
                              }))
                            }
                            className="glass-input px-3 py-2 text-sm"
                          >
                            {Array.from({ length: 15 }, (_, idx) => idx + 1).map(
                              (week) => (
                                <option key={week} value={week}>
                                  Week {week}
                                </option>
                              )
                            )}
                          </select>
                          <button
                            type="button"
                            disabled={submittingId === item.id}
                            onClick={() => void publish(item)}
                            className="btn-primary px-3 py-2 text-sm"
                          >
                            <span className="inline-flex items-center gap-1">
                              <Check size={14} />
                              Publish
                            </span>
                          </button>
                          <button
                            type="button"
                            disabled={submittingId === item.id}
                            onClick={() => void reject(item)}
                            className="rounded-lg border border-border-primary px-3 py-2 text-sm text-accent-red transition-colors hover:bg-accent-red-dim"
                          >
                            <span className="inline-flex items-center gap-1">
                              <X size={14} />
                              Reject
                            </span>
                          </button>
                        </div>
                      ) : null}

                      {item.shared_title ? (
                        <p
                          className="mt-3 truncate text-xs text-accent-green"
                          title={`Shared: ${item.shared_title} · Week ${item.shared_week}`}
                        >
                          Shared: {item.shared_title} · Week {item.shared_week}
                        </p>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
