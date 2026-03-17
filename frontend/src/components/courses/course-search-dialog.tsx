"use client";

import type { KeyboardEvent, ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { Search, X } from "lucide-react";

import { api } from "@/lib/api";
import type { ApiResponse, CourseOption, EnrollmentItem } from "@/types";

interface CourseSearchDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: (item: EnrollmentItem) => void;
}

function courseCode(item: CourseOption): string {
  if (!item.level || item.level === "0") {
    return item.code;
  }
  return `${item.code} ${item.level}`;
}

function sectionLabel(section: string | null): string | null {
  if (!section) {
    return null;
  }
  return `Section ${section}`;
}

function detailRow(
  meetingTime: string | null,
  room: string | null,
): ReactNode {
  const details = [meetingTime, room].filter(Boolean);
  if (!details.length) {
    return null;
  }
  return details.join(" • ");
}

function termYearLabel(item: CourseOption): string {
  return `${item.term} ${item.year}`;
}

export function CourseSearchDialog({
  open,
  onClose,
  onCreated,
}: CourseSearchDialogProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const requestRef = useRef(0);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<CourseOption[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setResults([]);
      setError(null);
      setHighlightedIndex(0);
      return;
    }
    inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }
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
        const response = await api.get<ApiResponse<CourseOption[]>>(
          `/courses?q=${encodeURIComponent(trimmed)}&limit=10`
        );
        if (requestRef.current !== requestId) {
          return;
        }
        setResults(response.data);
        setHighlightedIndex(0);
      } catch (err) {
        if (requestRef.current !== requestId) {
          return;
        }
        const message = err instanceof Error ? err.message : "Search failed";
        setError(message);
        setResults([]);
      } finally {
        if (requestRef.current === requestId) {
          setIsLoading(false);
        }
      }
    }

    void load();
  }, [open, query]);

  if (!open) {
    return null;
  }

  const highlighted = results[highlightedIndex];
  const showEmpty = Boolean(
    query.trim() && !isLoading && !results.length && !error
  );

  async function createEnrollment(courseId: number) {
    if (isSubmitting) {
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await api.post<ApiResponse<EnrollmentItem>>(
        "/enrollments",
        { course_id: courseId }
      );
      onCreated(response.data);
      onClose();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to add course";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function moveHighlight(direction: number) {
    if (!results.length) {
      return;
    }
    setHighlightedIndex((current) => {
      const next = current + direction;
      if (next < 0) {
        return results.length - 1;
      }
      if (next >= results.length) {
        return 0;
      }
      return next;
    });
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveHighlight(1);
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveHighlight(-1);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key === "Enter" && highlighted) {
      event.preventDefault();
      void createEnrollment(highlighted.id);
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center p-4">
      <button
        type="button"
        onClick={onClose}
        className="absolute inset-0 bg-black/60"
        aria-label="Close add course dialog"
      />
      <div className="glass-card relative z-10 w-full max-w-xl p-5">
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              Add Current Course
            </h2>
            <p className="mt-1 text-sm text-text-secondary">
              Search by code, level, or title. Press Enter to add the
              highlighted match.
            </p>
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

        <div className="relative">
          <Search
            size={16}
            className="pointer-events-none absolute top-1/2 left-3
              -translate-y-1/2 text-text-muted"
          />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Search courses"
            className="glass-input w-full py-3 pr-4 pl-10 text-sm"
          />
        </div>

        <div className="mt-4 max-h-72 overflow-y-auto">
          {isLoading ? (
            <p className="text-sm text-text-secondary">Searching...</p>
          ) : null}

          {error ? (
            <p className="text-sm text-accent-red">{error}</p>
          ) : null}

          {showEmpty ? (
            <p className="text-sm text-text-muted">No matching course</p>
          ) : null}

          {!isLoading && !error && results.length ? (
            <div className="space-y-2">
              {results.map((item, index) => {
                const isActive = index === highlightedIndex;
                const details = detailRow(item.meeting_time, item.room);
                const section = sectionLabel(item.section);
                return (
                  <button
                    key={item.id}
                    type="button"
                    onMouseEnter={() => setHighlightedIndex(index)}
                    onClick={() => void createEnrollment(item.id)}
                    disabled={isSubmitting}
                    className={`w-full rounded-[var(--radius-md)] border p-3 text-left
                      transition-colors ${
                        isActive
                          ? "border-accent-green bg-accent-green-dim"
                          : "border-border-primary bg-bg-card"
                      }`}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="font-mono text-xs text-accent-green">
                          {courseCode(item)}
                          {section ? (
                            <span className="ml-2 font-sans text-text-secondary">
                              {section}
                            </span>
                          ) : null}
                        </p>
                        <p className="mt-1 text-sm text-text-primary">
                          {item.title}
                        </p>
                        {details ? (
                          <p className="mt-1 text-xs text-text-secondary">
                            {details}
                          </p>
                        ) : null}
                        <p className="mt-1 text-xs text-text-secondary">
                          {termYearLabel(item)}
                        </p>
                      </div>
                      <p className="text-xs text-text-secondary">
                        {item.ects} ECTS
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
