"use client";

import type { KeyboardEvent } from "react";
import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Search, X } from "lucide-react";

import { api } from "@/lib/api";
import type {
  ApiResponse,
  CourseSearchGroup,
  CourseSearchOfferingOption,
  EnrollmentItem,
} from "@/types";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

interface CourseSearchDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: (item: EnrollmentItem) => void;
}

type Phase = "search" | "picker";

function courseLabel(group: CourseSearchGroup): string {
  if (!group.level || group.level === "0") return group.code;
  return `${group.code} ${group.level}`;
}

function seatLabel(o: CourseSearchOfferingOption): string {
  if (o.enrolled == null || o.capacity == null) return "";
  return `${o.enrolled}/${o.capacity}`;
}

export function CourseSearchDialog({
  open,
  onClose,
  onCreated,
}: CourseSearchDialogProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const requestRef = useRef(0);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<CourseSearchGroup[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [phase, setPhase] = useState<Phase>("search");
  const [selectedGroup, setSelectedGroup] = useState<CourseSearchGroup | null>(null);
  // component_type → offering_id
  const [selectedOfferingIds, setSelectedOfferingIds] = useState<Record<string, number>>({});

  // overload: list of offering_ids that still need to be enrolled
  const [overloadPendingIds, setOverloadPendingIds] = useState<number[] | null>(null);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setResults([]);
      setError(null);
      setHighlightedIndex(0);
      setPhase("search");
      setSelectedGroup(null);
      setSelectedOfferingIds({});
      setOverloadPendingIds(null);
      return;
    }
    if (phase === "search") {
      inputRef.current?.focus();
    }
  }, [open, phase]);

  useEffect(() => {
    if (!open || phase !== "search") return;
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setHighlightedIndex(0);
      setIsLoading(false);
      return;
    }

    const requestId = requestRef.current + 1;
    requestRef.current = requestId;
    setIsLoading(true);
    setError(null);

    async function load() {
      try {
        const response = await api.get<ApiResponse<CourseSearchGroup[]>>(
          `/courses?q=${encodeURIComponent(trimmed)}&limit=10`
        );
        if (requestRef.current !== requestId) return;
        setResults(response.data);
        setHighlightedIndex(0);
      } catch (err) {
        if (requestRef.current !== requestId) return;
        setError(err instanceof Error ? err.message : "Search failed");
        setResults([]);
      } finally {
        if (requestRef.current === requestId) setIsLoading(false);
      }
    }

    void load();
  }, [open, query, phase]);

  if (!open) return null;

  const highlighted = results[highlightedIndex];
  const showEmpty = Boolean(query.trim() && !isLoading && !results.length && !error);

  function openPicker(group: CourseSearchGroup) {
    setSelectedGroup(group);
    setSelectedOfferingIds({});
    setError(null);
    setPhase("picker");
  }

  function backToSearch() {
    setPhase("search");
    setSelectedGroup(null);
    setSelectedOfferingIds({});
    setError(null);
    setTimeout(() => inputRef.current?.focus(), 0);
  }

  function moveHighlight(direction: number) {
    if (!results.length) return;
    setHighlightedIndex((cur) => {
      const next = cur + direction;
      if (next < 0) return results.length - 1;
      if (next >= results.length) return 0;
      return next;
    });
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") { event.preventDefault(); moveHighlight(1); return; }
    if (event.key === "ArrowUp") { event.preventDefault(); moveHighlight(-1); return; }
    if (event.key === "Escape") { event.preventDefault(); onClose(); return; }
    if (event.key === "Enter" && highlighted) { event.preventDefault(); openPicker(highlighted); }
  }

  const allRequired = selectedGroup
    ? selectedGroup.components
        .filter((c) => c.required)
        .every((c) => selectedOfferingIds[c.component_type] != null)
    : false;

  async function enrollAll(ids: number[], overloadAcknowledged = false) {
    if (isSubmitting) return;
    setIsSubmitting(true);
    setError(null);
    const created: EnrollmentItem[] = [];
    try {
      for (const offeringId of ids) {
        const response = await api.post<ApiResponse<EnrollmentItem>>("/enrollments", {
          course_id: offeringId,
          course_overload_acknowledged: overloadAcknowledged,
        });
        created.push(response.data);
      }
      for (const item of created) onCreated(item);
      onClose();
    } catch (err) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const code: string | undefined = (err as any)?.response?.data?.error?.code;
      if (code === "ENROLLMENT_CREDITS_EXCEEDED") {
        setOverloadPendingIds(ids);
      } else {
        setError(err instanceof Error ? err.message : "Failed to add course");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleAddCourse() {
    if (!selectedGroup || !allRequired) return;
    const ids = selectedGroup.components.map((c) => selectedOfferingIds[c.component_type]);
    void enrollAll(ids);
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <button
        type="button"
        onClick={onClose}
        className="absolute inset-0"
        aria-label="Close add course dialog"
      />
      <div className="glass-card relative z-10 w-full max-w-2xl p-5">
        {/* Header */}
        <div className="mb-4 flex items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            {phase === "picker" && (
              <button
                type="button"
                onClick={backToSearch}
                className="rounded-full border border-border-primary p-1.5 text-text-secondary
                  transition-colors hover:text-text-primary"
                aria-label="Back to search"
              >
                <ArrowLeft size={14} />
              </button>
            )}
            <div>
              {phase === "search" ? (
                <>
                  <h2 className="text-lg font-semibold text-text-primary">Add Current Course</h2>
                  <p className="mt-1 text-sm text-text-secondary">
                    Search by code, level, or title. Press Enter to select.
                  </p>
                </>
              ) : (
                <>
                  <h2 className="text-lg font-semibold text-text-primary">
                    {courseLabel(selectedGroup!)} — {selectedGroup!.title}
                  </h2>
                  <p className="mt-1 text-sm text-text-secondary">
                    Choose a section for each component below.
                  </p>
                </>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-border-primary p-2
              text-text-secondary transition-colors hover:text-text-primary"
            aria-label="Close dialog"
          >
            <X size={16} />
          </button>
        </div>

        {/* Search phase */}
        {phase === "search" && (
          <>
            <div className="relative">
              <Search
                size={16}
                className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-text-muted"
              />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Search courses"
                className="glass-input w-full py-3 pr-4 pl-10 text-sm"
              />
            </div>

            <div className="mt-4 max-h-72 overflow-y-auto">
              {isLoading && (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="rounded-[var(--radius-md)] border border-white/[0.06] bg-white/[0.02] p-3 animate-pulse"
                    >
                      <div className="h-3 w-24 rounded bg-white/10 mb-2" />
                      <div className="h-3.5 w-48 rounded bg-white/[0.06]" />
                    </div>
                  ))}
                </div>
              )}

              {error && (
                <div className="flex items-center gap-2 rounded-lg bg-accent-red/10 px-3 py-2.5 text-xs text-accent-red">
                  <span className="flex-shrink-0">⚠</span>
                  {error}
                </div>
              )}

              {showEmpty && (
                <p className="py-4 text-center text-sm text-text-secondary">
                  No courses found for &quot;{query.trim()}&quot;
                </p>
              )}

              {!isLoading && !error && results.length > 0 && (
                <div className="space-y-2">
                  {results.map((group, index) => {
                    const isActive = index === highlightedIndex;
                    const componentLabels = group.components.map((c) => c.label).join(" + ");
                    return (
                      <button
                        key={group.course_id}
                        type="button"
                        onMouseEnter={() => setHighlightedIndex(index)}
                        onClick={() => openPicker(group)}
                        className={`w-full rounded-[var(--radius-md)] border p-3 text-left transition-colors ${
                          isActive
                            ? "border-accent-green bg-accent-green-dim"
                            : "border-border-primary bg-bg-card"
                        }`}
                      >
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <p className="font-mono text-xs text-accent-green">
                              {courseLabel(group)}
                              <span className="ml-2 font-sans text-text-muted normal-case">
                                {componentLabels}
                              </span>
                            </p>
                            <p className="mt-1 text-sm text-text-primary">{group.title}</p>
                            <p className="mt-1 text-xs text-text-secondary">
                              {group.term} {group.year}
                            </p>
                          </div>
                          <p className="shrink-0 text-xs text-text-secondary">{group.ects} ECTS</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}

        {/* Picker phase */}
        {phase === "picker" && selectedGroup && (
          <div className="space-y-5 max-h-[60vh] overflow-y-auto pr-1">
            {selectedGroup.components.map((component) => (
              <div key={component.component_type}>
                <div className="mb-2 flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-text-primary">{component.label}</h3>
                  {component.required && (
                    <span className="rounded-full bg-accent-green/10 px-2 py-0.5 text-xs text-accent-green">
                      Required
                    </span>
                  )}
                </div>
                <div className="overflow-x-auto rounded-[var(--radius-md)] border border-border-primary">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-border-primary text-text-muted">
                        <th className="w-6 py-2 pl-3 pr-2" />
                        <th className="py-2 pr-3 text-left font-medium">Section</th>
                        <th className="py-2 pr-3 text-left font-medium">Faculty</th>
                        <th className="py-2 pr-3 text-left font-medium">Days</th>
                        <th className="py-2 pr-3 text-left font-medium">Time</th>
                        <th className="py-2 pr-3 text-left font-medium">Room</th>
                        <th className="py-2 pr-3 text-right font-medium">Seats</th>
                      </tr>
                    </thead>
                    <tbody>
                      {component.offerings.map((o) => {
                        const isSelected =
                          selectedOfferingIds[component.component_type] === o.offering_id;
                        return (
                          <tr
                            key={o.offering_id}
                            onClick={() =>
                              setSelectedOfferingIds((prev) => ({
                                ...prev,
                                [component.component_type]: o.offering_id,
                              }))
                            }
                            className={`cursor-pointer border-b border-border-primary/50 last:border-b-0
                              transition-colors ${
                                isSelected
                                  ? "bg-accent-green/10"
                                  : "hover:bg-white/[0.03]"
                              }`}
                          >
                            <td className="py-2.5 pl-3 pr-2">
                              <div
                                className={`h-3.5 w-3.5 rounded-full border-2 transition-colors ${
                                  isSelected
                                    ? "border-accent-green bg-accent-green"
                                    : "border-border-primary bg-transparent"
                                }`}
                              />
                            </td>
                            <td className="py-2.5 pr-3 font-mono text-text-primary">
                              {o.section ?? "—"}
                            </td>
                            <td className="py-2.5 pr-3 text-text-secondary">
                              {o.faculty ?? "—"}
                            </td>
                            <td className="py-2.5 pr-3 text-text-secondary">
                              {o.days ?? "—"}
                            </td>
                            <td className="py-2.5 pr-3 text-text-secondary">
                              {o.meeting_time ?? "—"}
                            </td>
                            <td className="py-2.5 pr-3 text-text-secondary">
                              {o.room ?? "—"}
                            </td>
                            <td className="py-2.5 pr-3 text-right text-text-secondary">
                              {seatLabel(o) || "—"}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}

            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-accent-red/10 px-3 py-2.5 text-xs text-accent-red">
                <span className="flex-shrink-0">⚠</span>
                {error}
              </div>
            )}

            <div className="flex justify-end pt-1">
              <button
                type="button"
                onClick={handleAddCourse}
                disabled={!allRequired || isSubmitting}
                className="rounded-[var(--radius-md)] bg-accent-green px-5 py-2 text-sm font-medium
                  text-bg-base transition-opacity disabled:opacity-40"
              >
                {isSubmitting ? "Adding…" : "Add Course"}
              </button>
            </div>
          </div>
        )}
      </div>

      <ConfirmDialog
        isOpen={overloadPendingIds !== null}
        title="Course overload?"
        message="Adding this course would exceed the 36 ECTS limit. If you've been approved for a course overload (up to 42 ECTS), you can proceed. Have you been approved?"
        confirmLabel="Yes, I'm approved"
        cancelLabel="Cancel"
        variant="default"
        onConfirm={() => {
          const ids = overloadPendingIds!;
          setOverloadPendingIds(null);
          void enrollAll(ids, true);
        }}
        onCancel={() => setOverloadPendingIds(null)}
      />
    </div>
  );
}
