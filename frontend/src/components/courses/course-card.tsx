"use client";

import { useState } from "react";
import { Plus, Trash2, AlertTriangle, Clock, MapPin, BookOpen, AlertCircle, Timer, CheckCircle2 } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import type { Assessment, EnrollmentItem } from "@/types";

interface CourseCardProps {
  enrollment: EnrollmentItem;
  assessments: Assessment[];
  assessmentsLoading: boolean;
  onAddAssessment: (e: React.MouseEvent) => void;
  onClick: () => void;
  onRemove?: () => void;
  isRemoving?: boolean;
}

export function CourseCard({
  enrollment,
  assessments,
  assessmentsLoading,
  onAddAssessment,
  onClick,
  onRemove,
  isRemoving,
}: CourseCardProps) {
  const [confirming, setConfirming] = useState(false);

  const now = new Date();
  const completed = assessments.filter((a) => a.is_completed).length;
  const total = assessments.length;
  const upcoming = assessments.filter(
    (a) => !a.is_completed && new Date(a.deadline) >= now
  ).length;
  const overdue = assessments.filter(
    (a) => !a.is_completed && new Date(a.deadline) < now
  ).length;
  const progressPct = total > 0 ? (completed / total) * 100 : 0;

  function handleTrashClick(e: React.MouseEvent) {
    e.stopPropagation();
    setConfirming(true);
  }

  function handleCancelConfirm(e: React.MouseEvent) {
    e.stopPropagation();
    setConfirming(false);
  }

  function handleConfirmRemove(e: React.MouseEvent) {
    e.stopPropagation();
    setConfirming(false);
    onRemove?.();
  }

  return (
    <div
      onClick={onClick}
      className="flex flex-col overflow-hidden rounded-[var(--radius-lg)] border border-[#2a2a2a] bg-[#1a1a1a] cursor-pointer transition-all duration-200 hover:border-[#3a3a3a] hover:bg-[#1e1e1e] hover:shadow-lg group"
    >
      {/* Delete confirmation banner */}
      {confirming && (
        <div
          className="flex items-center gap-3 px-4 py-2.5 bg-red-950/40 border-b border-red-900/50"
          onClick={(e) => e.stopPropagation()}
        >
          <AlertTriangle size={13} className="text-red-400 shrink-0" />
          <span className="text-xs text-red-300 flex-1">Remove this course?</span>
          <button
            type="button"
            onClick={handleCancelConfirm}
            className="px-2.5 py-1 text-xs rounded-md border border-[#3a3a3a] text-text-secondary hover:text-text-primary hover:border-[#555] transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirmRemove}
            disabled={isRemoving}
            className="px-2.5 py-1 text-xs rounded-md bg-red-600 text-white hover:bg-red-500 disabled:opacity-50 transition-colors flex items-center gap-1"
          >
            {isRemoving ? <Spinner size={11} /> : null}
            Remove
          </button>
        </div>
      )}

      {/* ── Section 1: course identity ── */}
      <div className="flex items-start justify-between gap-2 px-4 pt-4 pb-3">
        <div className="min-w-0 flex-1">
          {/* Badge row */}
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs font-semibold text-accent-green">
              {enrollment.course_code}
            </span>
            <span className="text-[10px] text-text-muted">·</span>
            <span className="text-[11px] text-text-muted">
              {enrollment.term} {enrollment.year}
            </span>
          </div>
          {/* Title — fixed 2-line height so all cards align below */}
          <p className="text-sm font-semibold text-text-primary leading-snug line-clamp-2 min-h-[2.5rem]">
            {enrollment.course_title}
          </p>
        </div>

        {onRemove && !confirming && (
          <button
            type="button"
            onClick={handleTrashClick}
            disabled={isRemoving}
            className="shrink-0 mt-0.5 rounded-lg p-1.5 text-text-muted transition-colors hover:bg-red-950/40 hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-50 opacity-0 group-hover:opacity-100"
            title="Remove course"
          >
            {isRemoving ? <Spinner size={13} /> : <Trash2 size={13} />}
          </button>
        )}
      </div>

      {/* ── Section 2: meta ── */}
      <div className="flex flex-col gap-1.5 px-4 pb-3">
        {enrollment.meeting_time && (
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <Clock size={12} className="shrink-0 text-text-muted" />
            <span>{enrollment.meeting_time}</span>
          </div>
        )}
        {enrollment.room && (
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <MapPin size={12} className="shrink-0 text-text-muted" />
            <span className="truncate">{enrollment.room}</span>
          </div>
        )}
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <BookOpen size={12} className="shrink-0 text-text-muted" />
          <span>
            <span className="font-medium text-text-primary">{enrollment.ects}</span>
            {" "}ECTS
          </span>
        </div>
      </div>

      <div className="mx-4 h-px bg-[#2a2a2a]" />

      {/* ── Section 3: progress ── */}
      <div className="px-4 py-3 flex-1">
        {assessmentsLoading ? (
          <div className="flex items-center gap-2 h-[52px]">
            <Spinner size={13} />
            <span className="text-xs text-text-muted">Loading...</span>
          </div>
        ) : (
          <>
            <div className="mb-2 flex items-center justify-between text-xs">
              <span className="text-text-secondary">Progress</span>
              <span className="text-text-muted">{completed}/{total} done</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-[#2a2a2a]">
              <div
                className="h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%`, background: "#a3e635" }}
              />
            </div>
            {/* Stat chips — min-height keeps progress bottom-aligned across cards */}
            <div className="mt-2.5 flex flex-wrap items-center gap-1.5 min-h-[22px]">
              {overdue > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-950/60 px-2 py-0.5 text-xs text-red-400">
                  <AlertCircle size={10} /> {overdue} overdue
                </span>
              )}
              {upcoming > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-orange-950/60 px-2 py-0.5 text-xs text-orange-400">
                  <Timer size={10} /> {upcoming} upcoming
                </span>
              )}
              {completed > 0 && upcoming === 0 && overdue === 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-green-950/60 px-2 py-0.5 text-xs text-green-400">
                  <CheckCircle2 size={10} /> {completed} done
                </span>
              )}
              {total === 0 && (
                <span className="text-xs text-text-muted">No deadlines yet</span>
              )}
            </div>
          </>
        )}
      </div>

      <div className="mx-4 h-px bg-[#2a2a2a]" />

      {/* ── Section 4: footer ── */}
      <div className="flex justify-end px-4 py-2.5">
        <button
          type="button"
          onClick={onAddAssessment}
          className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium border border-[#2a2a2a] text-text-secondary transition-colors hover:border-[#3a3a3a] hover:text-text-primary hover:bg-white/5"
        >
          <Plus size={12} />
          Add deadline
        </button>
      </div>
    </div>
  );
}
