"use client";

import { ArrowUpRight, Plus } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import type { Assessment, EnrollmentItem } from "@/types";

interface CourseCardProps {
  enrollment: EnrollmentItem;
  assessments: Assessment[];
  assessmentsLoading: boolean;
  onAddAssessment: () => void;
  onOpenDetail: () => void;
}

export function CourseCard({
  enrollment,
  assessments,
  assessmentsLoading,
  onAddAssessment,
  onOpenDetail,
}: CourseCardProps) {
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

  return (
    <GlassCard padding={false} className="flex flex-col gap-0 overflow-hidden">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 p-4 pb-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-sm font-semibold text-accent-green">
              {enrollment.course_code}
            </span>
            <span className="text-xs text-text-secondary">·</span>
            <span className="text-xs text-text-secondary">
              {enrollment.term} {enrollment.year}
            </span>
          </div>
          <p className="mt-0.5 text-sm font-medium text-text-primary leading-snug">
            {enrollment.course_title}
          </p>
        </div>
        <button
          type="button"
          onClick={onOpenDetail}
          className="shrink-0 rounded-lg p-1.5 text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
          title="Open course detail"
        >
          <ArrowUpRight size={16} />
        </button>
      </div>

      {/* Meta row */}
      <div className="flex flex-wrap items-center gap-3 px-4 pb-3 text-xs text-text-secondary">
        {enrollment.meeting_time && (
          <span className="flex items-center gap-1">
            <span>📅</span>
            <span>{enrollment.meeting_time}</span>
          </span>
        )}
        {enrollment.room && (
          <span className="flex items-center gap-1">
            <span>📍</span>
            <span>{enrollment.room}</span>
          </span>
        )}
        <span className="flex items-center gap-1">
          <span className="font-medium text-text-primary">{enrollment.ects}</span>
          <span>ECTS</span>
        </span>
      </div>

      <div className="mx-4 h-px bg-[#2a2a2a]" />

      {/* Progress */}
      <div className="px-4 py-3">
        {assessmentsLoading ? (
          <Spinner size={14} />
        ) : (
          <>
            <div className="mb-1.5 flex items-center justify-between text-xs text-text-secondary">
              <span>Progress</span>
              <span>
                {completed}/{total} done
              </span>
            </div>
            <div
              className="h-1.5 w-full rounded-full"
              style={{ background: "#2a2a2a" }}
            >
              <div
                className="h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${progressPct}%`, background: "#a3e635" }}
              />
            </div>

            {/* Stat chips */}
            <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
              {upcoming > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-orange-950/60 px-2 py-0.5 text-xs text-orange-400">
                  ⏰ {upcoming} upcoming
                </span>
              )}
              {overdue > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-950/60 px-2 py-0.5 text-xs text-red-400">
                  ⚠ {overdue} overdue
                </span>
              )}
              {completed > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-green-950/60 px-2 py-0.5 text-xs text-green-400">
                  ✓ {completed} done
                </span>
              )}
              {total === 0 && (
                <span className="text-xs text-text-secondary">No deadlines yet</span>
              )}
            </div>
          </>
        )}
      </div>

      <div className="mx-4 h-px bg-[#2a2a2a]" />

      {/* Footer */}
      <div className="flex justify-end px-4 py-2.5">
        <button
          type="button"
          onClick={onAddAssessment}
          className="btn-secondary inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs"
        >
          <Plus size={12} />
          Add deadline
        </button>
      </div>
    </GlassCard>
  );
}
