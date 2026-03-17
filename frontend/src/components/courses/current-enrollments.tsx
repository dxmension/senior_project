"use client";

import { Trash2 } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import type { EnrollmentItem } from "@/types";

interface CurrentEnrollmentsProps {
  enrollments: EnrollmentItem[];
  isLoading: boolean;
  deletingKey: string | null;
  onRemove: (item: EnrollmentItem) => void;
}

function itemKey(item: EnrollmentItem): string {
  return `${item.course_id}:${item.term}:${item.year}`;
}

function termYearLabel(item: EnrollmentItem): string {
  return `${item.term} ${item.year}`;
}

function sectionLabel(section: string | null): string | null {
  if (!section) {
    return null;
  }
  return `Section ${section}`;
}

function detailLine(item: EnrollmentItem): string {
  return [item.meeting_time, item.room, termYearLabel(item)]
    .filter(Boolean)
    .join(" • ");
}

export function CurrentEnrollments({
  enrollments,
  isLoading,
  deletingKey,
  onRemove,
}: CurrentEnrollmentsProps) {
  if (isLoading) {
    return <Spinner text="Loading current courses..." className="py-10" />;
  }

  if (!enrollments.length) {
    return (
      <GlassCard className="py-10 text-center">
        <p className="text-sm text-text-muted">No current courses yet.</p>
      </GlassCard>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {enrollments.map((item) => {
        const key = itemKey(item);
        const isDeleting = deletingKey === key;
        const section = sectionLabel(item.section);
        const details = detailLine(item);
        return (
          <GlassCard key={key} className="flex flex-col gap-4">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                <p className="font-mono text-xs text-accent-green">
                  {item.course_code}
                  {section ? (
                    <span className="ml-2 font-sans text-text-secondary">
                      {section}
                    </span>
                  ) : null}
                </p>
                <h3 className="text-base font-semibold text-text-primary">
                  {item.course_title}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => onRemove(item)}
                disabled={isDeleting}
                className="rounded-full border border-border-primary p-2
                  text-text-secondary transition-colors hover:text-accent-red
                  disabled:cursor-not-allowed disabled:opacity-50"
                aria-label={`Remove ${item.course_code}`}
              >
                <Trash2 size={16} />
              </button>
            </div>
            <div className="space-y-2 text-sm text-text-secondary">
              {details ? <p>{details}</p> : null}
              <p>{item.ects} ECTS</p>
            </div>
          </GlassCard>
        );
      })}
    </div>
  );
}
