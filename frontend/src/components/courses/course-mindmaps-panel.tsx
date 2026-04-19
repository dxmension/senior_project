"use client";

import { AlertTriangle, Download, Plus, Trash2, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { MindmapTree } from "@/components/courses/mindmap-tree";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type { ApiResponse, EnrollmentItem, SavedMindmap, StudyMaterialUpload } from "@/types";

// ─── Week label helper ────────────────────────────────────────────────────────

const WEEKS = Array.from({ length: 15 }, (_, i) => i + 1);

// ─── Component ────────────────────────────────────────────────────────────────

interface Props {
  enrollment: EnrollmentItem;
}

export function CourseMindmapsPanel({ enrollment }: Props) {
  const courseId = enrollment.course_id;

  const [mindmaps, setMindmaps] = useState<SavedMindmap[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate form
  const [week, setWeek] = useState(1);

  // Viewer modal
  const [viewing, setViewing] = useState<SavedMindmap | null>(null);
  const downloadRef = useRef<(() => void) | null>(null);

  // Delete confirmation
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Weeks with uploaded materials
  const [weeksWithMaterials, setWeeksWithMaterials] = useState<Set<number>>(new Set());

  // No-material warning modal
  const [showNoMaterialWarning, setShowNoMaterialWarning] = useState(false);

  useEffect(() => {
    void fetchMindmaps();
    void fetchUploadedWeeks();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId]);

  // Escape key handler to close viewer modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && viewing) {
        setViewing(null);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [viewing]);

  async function fetchMindmaps() {
    setLoading(true);
    try {
      const res = await api.get<ApiResponse<SavedMindmap[]>>(
        `/mindmaps/${courseId}`
      );
      setMindmaps(res.data ?? []);
    } catch {
      setError("Failed to load mindmaps.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchUploadedWeeks() {
    try {
      const res = await api.get<ApiResponse<StudyMaterialUpload[]>>(
        `/course-materials/${courseId}/uploads`
      );
      const weeks = new Set(
        (res.data ?? [])
          .filter((u) => u.upload_status === "completed")
          .map((u) => u.week)
      );
      setWeeksWithMaterials(weeks);
    } catch {
      // non-critical — warning just won't show
    }
  }

  function handleGenerateClick() {
    if (!weeksWithMaterials.has(week)) {
      setShowNoMaterialWarning(true);
      return;
    }
    void handleGenerate();
  }

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    try {
      const res = await api.post<ApiResponse<SavedMindmap>>(
        `/mindmaps/${courseId}/generate`,
        { week, depth: 3 }
      );
      if (res.data) {
        setMindmaps((prev) => [res.data!, ...prev]);
      }
    } catch {
      setError("Generation failed. Check your OpenAI API key or try again.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleDelete(id: number) {
    setDeletingId(id);
    try {
      await api.delete(`/mindmaps/${courseId}/${id}`);
      setMindmaps((prev) => prev.filter((m) => m.id !== id));
      setConfirmDeleteId(null);
      if (viewing?.id === id) setViewing(null);
    } catch {
      // keep state, let user retry
    } finally {
      setDeletingId(null);
    }
  }

  // ── Grouped by week ────────────────────────────────────────────────────────

  const byWeek = mindmaps.reduce<Record<number, SavedMindmap[]>>((acc, m) => {
    (acc[m.week] ??= []).push(m);
    return acc;
  }, {});
  const usedWeeks = Object.keys(byWeek)
    .map(Number)
    .sort((a, b) => a - b);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <>
      <div className="space-y-6">
        {/* Generate form */}
        <GlassCard padding={false} className="p-5">
          <h3 className="mb-4 text-sm font-semibold text-text-primary">
            Generate Mindmap
          </h3>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-secondary">Week</label>
              <select
                value={week}
                onChange={(e) => setWeek(Number(e.target.value))}
                className="rounded-lg border border-border-primary bg-surface-secondary
                           px-3 py-2 text-sm text-text-primary focus:outline-none
                           focus:ring-1 focus:ring-accent-green"
              >
                {WEEKS.map((w) => (
                  <option key={w} value={w}>
                    Week {w}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              disabled={generating}
              onClick={handleGenerateClick}
              className="inline-flex items-center gap-1.5 rounded-lg bg-accent-green px-4 py-2
                         text-sm font-medium text-black transition-opacity
                         hover:opacity-90 disabled:opacity-40"
            >
              {generating ? (
                <Spinner />
              ) : (
                <Plus size={14} />
              )}
              {generating ? "Generating…" : "Generate"}
            </button>
          </div>
          <p className="mt-2 text-xs text-text-secondary">
            Choose a week and a mindmap will be generated based on the week&apos;s study materials. 
          </p>

          {error && (
            <p className="mt-3 text-xs text-red-400">{error}</p>
          )}
        </GlassCard>

        {/* Saved mindmaps */}
        {loading ? (
          <div className="flex justify-center py-10">
            <Spinner text="Loading mindmaps…" />
          </div>
        ) : mindmaps.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-14 text-center">
            <p className="text-sm text-text-secondary">No mindmaps yet.</p>
            <p className="text-xs text-text-secondary">
              Enter a topic above and click Generate.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {usedWeeks.map((w) => (
              <div key={w}>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-secondary">
                  Week {w}
                </p>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {byWeek[w].map((mm) => (
                    <MindmapCard
                      key={mm.id}
                      mindmap={mm}
                      onView={() => setViewing(mm)}
                      onDelete={() => setConfirmDeleteId(mm.id)}
                      confirmingDelete={confirmDeleteId === mm.id}
                      deleting={deletingId === mm.id}
                      onConfirmDelete={() => void handleDelete(mm.id)}
                      onCancelDelete={() => setConfirmDeleteId(null)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── No-material warning modal ────────────────────────────────────────── */}
      {showNoMaterialWarning && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={() => setShowNoMaterialWarning(false)}
        >
          <div
            className="flex max-w-sm flex-col gap-4 rounded-xl border border-border-primary
                        bg-[#1a1a1a] p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="mt-0.5 shrink-0 text-yellow-400" />
              <div>
                <p className="text-sm font-semibold text-text-primary">
                  Cannot generate mindmap
                </p>
                <p className="mt-1 text-xs text-text-secondary">
                  Generation is impossible without study materials for Week {week}. 
                  Please upload course materials first to generate a mindmap.
                </p>
                <p className="mt-2 text-xs text-text-secondary">
                  You can upload materials in the <span className="text-text-primary font-medium">Materials</span> tab.
                </p>
              </div>
            </div>
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setShowNoMaterialWarning(false)}
                className="rounded-lg bg-accent-green px-4 py-1.5 text-xs font-medium
                           text-black transition-opacity hover:opacity-90"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Viewer modal ─────────────────────────────────────────────────────── */}
      {viewing && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
        >
          <div
            className="relative flex w-[1200px] max-w-[95vw] flex-col gap-3
                        rounded-xl border border-border-primary bg-surface-primary p-4"
          >
            {/* Modal header */}
            <div className="flex items-center justify-between gap-4">
              <div>
                <span className="text-xs text-text-secondary">Week {viewing.week} · </span>
                <span className="text-sm font-medium text-text-primary">{viewing.topic}</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => downloadRef.current?.()}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border-primary
                             px-3 py-1.5 text-xs text-text-secondary transition-colors
                             hover:border-accent-green hover:text-accent-green"
                >
                  <Download size={12} />
                  PNG
                </button>
                <button
                  type="button"
                  onClick={() => setViewing(null)}
                  className="rounded p-1.5 text-text-secondary transition-colors hover:text-text-primary"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Scrollable mindmap */}
            <div className="rounded-lg overflow-hidden max-h-[85vh] overflow-y-auto">
              <MindmapTree
                root={viewing.root}
                filename={`mindmap-week${viewing.week}`}
                downloadRef={downloadRef}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ─── Mindmap card ──────────────────────────────────────────────────────────────

interface CardProps {
  mindmap: SavedMindmap;
  onView: () => void;
  onDelete: () => void;
  confirmingDelete: boolean;
  deleting: boolean;
  onConfirmDelete: () => void;
  onCancelDelete: () => void;
}

function MindmapCard({
  mindmap,
  onView,
  onDelete,
  confirmingDelete,
  deleting,
  onConfirmDelete,
  onCancelDelete,
}: CardProps) {
  const date = new Date(mindmap.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });

  return (
    <div className="glass-card group relative flex flex-col gap-2 p-4 transition-colors hover:border-accent-green/40">
      <button
        type="button"
        onClick={onView}
        className="flex-1 text-left"
      >
        <p className="text-sm font-medium text-text-primary line-clamp-2">
          {mindmap.topic}
        </p>
        <p className="mt-1 text-xs text-text-secondary">{date}</p>
      </button>

      {confirmingDelete ? (
        <div className="flex items-center gap-2 border-t border-border-primary pt-2 text-xs">
          <span className="text-red-400">Delete?</span>
          <button
            type="button"
            disabled={deleting}
            onClick={onConfirmDelete}
            className="rounded bg-red-600/80 px-2 py-0.5 text-white disabled:opacity-50"
          >
            {deleting ? "…" : "Yes"}
          </button>
          <button
            type="button"
            onClick={onCancelDelete}
            className="text-text-secondary hover:text-text-primary"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between border-t border-border-primary pt-2">
          <button
            type="button"
            onClick={onView}
            className="text-xs text-accent-green hover:opacity-75"
          >
            View →
          </button>
          <button
            type="button"
            onClick={onDelete}
            className="rounded p-1 text-text-secondary transition-colors
                       hover:bg-red-950/50 hover:text-red-400"
          >
            <Trash2 size={13} />
          </button>
        </div>
      )}
    </div>
  );
}
