"use client";

import { useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  Clock,
  MapPin,
  Plus,
  Timer,
  Trash2,
} from "lucide-react";

import { Plus, Trash2, AlertTriangle, Clock, MapPin, BookOpen, AlertCircle, Timer, CheckCircle2 } from "lucide-react";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
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
  const upcoming = assessments.filter(isUpcoming(now)).length;
  const overdue = assessments.filter(isOverdue(now)).length;
  const progressPct = total > 0 ? (completed / total) * 100 : 0;

  function handleTrashClick(e: React.MouseEvent) {
    e.stopPropagation();
    setShowDeleteDialog(true);
  }

  function handleConfirmDelete() {
    setShowDeleteDialog(false);
    onRemove?.();
  }

  function handleCancelDelete() {
    if (isRemoving) return;
    setShowDeleteDialog(false);
  }

  return (
    <div
      onClick={onClick}
      className="group flex cursor-pointer flex-col overflow-hidden rounded-[var(--radius-lg)] border border-[#2a2a2a] bg-[#1a1a1a] transition-all duration-200 hover:border-[#3a3a3a] hover:bg-[#1e1e1e] hover:shadow-lg"
    >
      {confirming ? (
        <div
          className="flex items-center gap-3 border-b border-red-900/50 bg-red-950/40 px-4 py-2.5"
          onClick={(e) => e.stopPropagation()}
        >
          <AlertTriangle size={13} className="shrink-0 text-red-400" />
          <span className="flex-1 text-xs text-red-300">Remove this course?</span>
          <button
            type="button"
            onClick={handleCancelConfirm}
            className="rounded-md border border-[#3a3a3a] px-2.5 py-1 text-xs text-text-secondary transition-colors hover:border-[#555] hover:text-text-primary"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirmRemove}
            disabled={isRemoving}
            className="flex items-center gap-1 rounded-md bg-red-600 px-2.5 py-1 text-xs text-white transition-colors hover:bg-red-500 disabled:opacity-50"
          >
            {isRemoving ? <Spinner size={11} /> : null}
            Remove
          </button>
        </div>
      ) : null}

      <div className="flex items-start justify-between gap-2 px-4 pt-4 pb-3">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs font-semibold text-accent-green">
              {enrollment.course_code}
            </span>
            {enrollment.section ? (
              <span className="text-[11px] text-text-muted">
                Section {enrollment.section}
              </span>
            ) : null}
            <span className="text-[11px] text-text-muted">
              {enrollment.term} {enrollment.year}
            </span>
          </div>
          <p className="min-h-[2.5rem] line-clamp-2 text-sm leading-snug font-semibold text-text-primary">
            {enrollment.course_title}
          </p>
        </div>

        {onRemove && !confirming ? (
          <button
            type="button"
            onClick={handleTrashClick}
            disabled={isRemoving}
            className="mt-0.5 shrink-0 rounded-lg p-1.5 text-text-muted opacity-0 transition-colors hover:bg-red-950/40 hover:text-red-400 group-hover:opacity-100 disabled:cursor-not-allowed disabled:opacity-50"
            title="Remove course"
          >
            {isRemoving ? <Spinner size={13} /> : <Trash2 size={13} />}
          </button>
        ) : null}
      </div>

      <div className="flex flex-col gap-1.5 px-4 pb-3">
        {enrollment.meeting_time ? (
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <Clock size={12} className="shrink-0 text-text-muted" />
            <span>{formatMeeting(enrollment)}</span>
          </div>
        ) : null}
        {enrollment.room ? (
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <MapPin size={12} className="shrink-0 text-text-muted" />
            <span className="truncate">{enrollment.room}</span>
          </div>
        ) : null}
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <BookOpen size={12} className="shrink-0 text-text-muted" />
          <span>
            <span className="font-medium text-text-primary">{enrollment.ects}</span>
            {" "}ECTS
          </span>
        </div>
      </div>

      <div className="mx-4 h-px bg-[#2a2a2a]" />

      <div className="flex-1 px-4 py-3">
        {assessmentsLoading ? (
          <div className="flex h-[52px] items-center gap-2">
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
            <div className="mt-2.5 flex min-h-[22px] flex-wrap items-center gap-1.5">
              {overdue > 0 ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-950/60 px-2 py-0.5 text-xs text-red-400">
                  <AlertCircle size={10} /> {overdue} overdue
                </span>
              ) : null}
              {upcoming > 0 ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-orange-950/60 px-2 py-0.5 text-xs text-orange-400">
                  <Timer size={10} /> {upcoming} upcoming
                </span>
              ) : null}
              {completed > 0 && upcoming === 0 && overdue === 0 ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-green-950/60 px-2 py-0.5 text-xs text-green-400">
                  <CheckCircle2 size={10} /> {completed} done
                </span>
              ) : null}
              {total === 0 ? (
                <span className="text-xs text-text-muted">No deadlines yet</span>
              ) : null}
            </div>
          </>
        )}
      </div>

      <div className="mx-4 h-px bg-[#2a2a2a]" />

      <div className="flex justify-end px-4 py-2.5">
        <button
          type="button"
          onClick={onAddAssessment}
          className="inline-flex items-center gap-1.5 rounded-lg border border-[#2a2a2a] px-3 py-1.5 text-xs font-medium text-text-secondary transition-colors hover:border-[#3a3a3a] hover:bg-white/5 hover:text-text-primary"
        >
          <Plus size={12} />
          Add deadline
        </button>
      </div>
    </div>

    <ConfirmDialog
      isOpen={showDeleteDialog}
      title="Remove course"
      message={`Remove "${enrollment.course_code}: ${enrollment.course_title}" from your courses?`}
      confirmLabel={isRemoving ? "Removing..." : "Remove"}
      variant="danger"
      onConfirm={handleConfirmDelete}
      onCancel={handleCancelDelete}
    />
    </>
  );
}

function isUpcoming(now: Date) {
  return (assessment: Assessment) =>
    !assessment.is_completed && new Date(assessment.deadline) >= now;
}

function isOverdue(now: Date) {
  return (assessment: Assessment) =>
    !assessment.is_completed && new Date(assessment.deadline) < now;
}

function formatMeeting(enrollment: EnrollmentItem): string {
  return [enrollment.days, enrollment.meeting_time].filter(Boolean).join(" ");
}
