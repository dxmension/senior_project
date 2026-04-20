"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { BookOpen, Calendar, MapPin, Clock, CheckCircle2, RefreshCw } from "lucide-react";
import type { CalendarEntry } from "@/types";
import { resolveEventColor } from "@/lib/calendar-colors";

interface EventPopupProps {
  entry: CalendarEntry;
  position: { x: number; y: number };
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
}

function formatDateTime(iso: string): string {
  return `${formatDate(iso)} at ${formatTime(iso)}`;
}

function relativeLabel(iso: string): { label: string; color: string } {
  const now = new Date();
  const target = new Date(iso);
  const diffMs = target.getTime() - now.getTime();
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return { label: "Today", color: "#fb923c" };
  if (diffDays > 0) return { label: `in ${diffDays} day${diffDays === 1 ? "" : "s"}`, color: "#a3e635" };
  return { label: `${Math.abs(diffDays)} day${Math.abs(diffDays) === 1 ? "" : "s"} ago`, color: "#f87171" };
}

export function EventPopup({ entry, position }: EventPopupProps) {
  const colors = resolveEventColor(entry);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return null;

  return createPortal(
    <div
      style={{ left: position.x, top: position.y, zIndex: 9999 }}
      className="fixed w-80 glass-card p-4 shadow-2xl pointer-events-none"
    >
      {/* Header */}
      <div className="flex items-center gap-2 min-w-0 mb-3">
        <span
          className="w-2.5 h-2.5 rounded-full flex-shrink-0 mt-0.5"
          style={{ backgroundColor: colors.border }}
        />
        <span className="text-sm font-semibold text-text-primary leading-tight">
          {entry.title}
        </span>
      </div>

      <div className="border-t border-border-primary mb-3" />

      <div className="flex flex-col gap-2 text-sm">
        {(entry.event_type as string).toLowerCase() === "assessment_deadline" && (
          <AssessmentContent entry={entry} colors={colors} />
        )}
        {(entry.event_type as string).toLowerCase() === "personal_event" && (
          <PersonalContent entry={entry} />
        )}
        {(entry.event_type as string).toLowerCase() === "course_session" && (
          <CourseSessionContent entry={entry} />
        )}
      </div>

      {entry.description && (
        <>
          <div className="border-t border-border-primary mt-3 mb-2" />
          <p className="text-xs text-text-secondary italic leading-relaxed">
            &ldquo;{entry.description}&rdquo;
          </p>
        </>
      )}
    </div>,
    document.body
  );
}

function AssessmentContent({
  entry,
  colors,
}: {
  entry: CalendarEntry;
  colors: { border: string };
}) {
  const meta = entry.source_meta;
  const assessmentType = meta.assessment_type as string | undefined;
  const courseCode = meta.course_code as string | undefined;
  const isCompleted = meta.is_completed === true;
  const weight = meta.weight as number | undefined;
  const maxScore = meta.max_score as number | undefined;
  const relative = relativeLabel(entry.start_at);

  return (
    <>
      {assessmentType && (
        <div className="flex items-center gap-1.5">
          <span
            className="text-xs font-semibold px-2 py-0.5 rounded"
            style={{
              backgroundColor: colors.border + "22",
              color: colors.border,
              border: `1px solid ${colors.border}44`,
            }}
          >
            {assessmentType}
          </span>
        </div>
      )}

      {courseCode && (
        <div className="flex items-center gap-2 text-text-secondary">
          <BookOpen size={13} className="flex-shrink-0" />
          <span>{courseCode}</span>
        </div>
      )}

      <div className="flex items-center gap-2 text-text-secondary">
        <Calendar size={13} className="flex-shrink-0" />
        <span>{formatDateTime(entry.start_at)}</span>
      </div>

      <div className="flex items-center gap-2">
        <Clock size={13} className="flex-shrink-0 text-text-secondary" />
        <span style={{ color: relative.color }} className="font-medium">
          {relative.label}
        </span>
      </div>

      {(weight !== undefined || maxScore !== undefined) && (
        <div className="flex items-center gap-3 text-text-secondary">
          {weight !== undefined && <span>Weight: {weight}%</span>}
          {maxScore !== undefined && <span>Max: {maxScore} pts</span>}
        </div>
      )}

      {isCompleted && (
        <div className="flex items-center gap-2 text-[#34d399]">
          <CheckCircle2 size={13} />
          <span className="text-xs font-medium">Completed</span>
        </div>
      )}
    </>
  );
}

function PersonalContent({ entry }: { entry: CalendarEntry }) {
  const meta = entry.source_meta;
  const recurrence = meta.recurrence as string | undefined;

  return (
    <>
      {entry.category_name && (
        <div className="flex items-center gap-2 text-text-secondary">
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: entry.color ?? "#a3e635" }}
          />
          <span>{entry.category_name}</span>
        </div>
      )}

      <div className="flex items-center gap-2 text-text-secondary">
        <Calendar size={13} className="flex-shrink-0" />
        {entry.end_at ? (
          <span>
            {formatDate(entry.start_at)}, {formatTime(entry.start_at)} &rarr;{" "}
            {formatTime(entry.end_at)}
          </span>
        ) : (
          <span>{formatDateTime(entry.start_at)}</span>
        )}
      </div>

      {entry.location && (
        <div className="flex items-center gap-2 text-text-secondary">
          <MapPin size={13} className="flex-shrink-0" />
          <span>{entry.location}</span>
        </div>
      )}

      {recurrence && recurrence !== "NONE" && (
        <div className="flex items-center gap-2 text-text-secondary">
          <RefreshCw size={13} className="flex-shrink-0" />
          <span className="capitalize">Repeats {recurrence.toLowerCase()}</span>
        </div>
      )}
    </>
  );
}

function CourseSessionContent({ entry }: { entry: CalendarEntry }) {
  const meta = entry.source_meta;
  const courseCode = meta.course_code as string | undefined;
  const courseTitle = meta.course_title as string | undefined;
  const room = meta.room as string | null | undefined;
  const faculty = meta.faculty as string | null | undefined;

  return (
    <>
      {(courseCode || courseTitle) && (
        <div className="flex items-center gap-2 text-text-secondary">
          <BookOpen size={13} className="flex-shrink-0" />
          <span>
            {courseCode}
            {courseCode && courseTitle ? " — " : ""}
            {courseTitle}
          </span>
        </div>
      )}

      <div className="flex items-center gap-2 text-text-secondary">
        <Calendar size={13} className="flex-shrink-0" />
        <span>{formatDateTime(entry.start_at)}</span>
      </div>

      {room && (
        <div className="flex items-center gap-2 text-text-secondary">
          <MapPin size={13} className="flex-shrink-0" />
          <span>Room {room}</span>
        </div>
      )}

      {faculty && (
        <div className="flex items-center gap-2 text-text-secondary">
          <span className="text-xs">Faculty:</span>
          <span className="text-text-primary text-xs">{faculty}</span>
        </div>
      )}
    </>
  );
}
