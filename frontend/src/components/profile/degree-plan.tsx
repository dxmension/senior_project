"use client";

import { useState } from "react";
import {
  GraduationCap,
  Clock,
  BookOpen,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle2,
  CalendarDays,
  Sun,
  Star,
  Sparkles,
} from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import type { DegreePlan, DegreePlanTerm, DegreePlanCourse, SuggestedCourse } from "@/types";

// ─── Helpers ────────────────────────────────────────────────────────────────

function priorityLabel(p: number | null): string {
  if (p === null) return "No priority";
  return `Priority ${p}`;
}

function priorityClass(p: number | null): string {
  if (p === 1) return "text-accent-green bg-accent-green/10 border-accent-green/25";
  if (p === 2) return "text-accent-blue bg-accent-blue/10 border-accent-blue/25";
  if (p === 3) return "text-accent-orange bg-accent-orange/10 border-accent-orange/25";
  if (p === 4) return "text-text-muted bg-text-muted/10 border-text-muted/25";
  return "text-text-muted/50 bg-bg-card border-border-primary";
}

const CATEGORY_COLORS: Record<string, string> = {
  "Mathematics & Science": "bg-accent-blue/10 text-accent-blue border-accent-blue/25",
  "Computer Science Core": "bg-accent-green/10 text-accent-green border-accent-green/25",
  "Capstone": "bg-accent-orange/10 text-accent-orange border-accent-orange/25",
  "University Core": "bg-accent-red/10 text-accent-red border-accent-red/25",
  "Electives": "bg-text-muted/10 text-text-muted border-text-muted/25",
};

function categoryColor(name: string): string {
  for (const [key, cls] of Object.entries(CATEGORY_COLORS)) {
    if (name.toLowerCase().includes(key.toLowerCase())) return cls;
  }
  return "bg-text-muted/10 text-text-muted border-text-muted/25";
}

// ─── Suggested course row ──────────────────────────────────────────────────

function SuggestedCourseRow({ course }: { course: SuggestedCourse }) {
  return (
    <div className="flex items-center gap-2 py-1">
      <span className="font-mono text-xs text-text-secondary w-20 shrink-0">{course.full_code}</span>
      <span className="text-xs text-text-muted flex-1 truncate">{course.title}</span>
      <span className="text-xs text-text-muted/60 shrink-0">{course.ects} ECTS</span>
      <span className={`text-xs px-1.5 py-0.5 rounded border shrink-0 ${priorityClass(course.user_priority)}`}>
        {priorityLabel(course.user_priority)}
      </span>
    </div>
  );
}

// ─── Course chip ─────────────────────────────────────────────────────────────

function CourseChip({ course }: { course: DegreePlanCourse }) {
  const [open, setOpen] = useState(false);
  const hasSuggestions = course.suggested_courses.length > 0;
  const hasDetails = course.note || course.terms_available.length > 0 || hasSuggestions;

  return (
    <div className="rounded-lg border border-border-primary bg-bg-elevated overflow-hidden">
      <button
        type="button"
        onClick={() => hasDetails && setOpen((v) => !v)}
        className={`w-full flex items-start gap-2.5 px-3 py-2.5 text-left ${hasDetails ? "cursor-pointer hover:bg-bg-card/50" : "cursor-default"} transition-colors`}
      >
        {course.status === "in_progress" ? (
          <Clock size={13} className="text-accent-blue shrink-0 mt-0.5" />
        ) : course.is_elective ? (
          <Sparkles size={13} className="text-accent-orange shrink-0 mt-0.5" />
        ) : (
          <BookOpen size={13} className="text-text-muted shrink-0 mt-0.5" />
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm text-text-primary leading-snug">{course.requirement_name}</p>
          <div className="flex items-center gap-1.5 mt-1 flex-wrap">
            <span className={`text-xs px-1.5 py-0.5 rounded border ${categoryColor(course.category)}`}>
              {course.category}
            </span>
            <span className="text-xs text-text-muted font-mono">{course.ects} ECTS</span>
            {hasSuggestions && (
              <span className="text-xs text-accent-orange">
                {course.suggested_courses.length} option{course.suggested_courses.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        </div>
        {hasDetails && (
          open
            ? <ChevronUp size={12} className="text-text-muted shrink-0 mt-1" />
            : <ChevronDown size={12} className="text-text-muted shrink-0 mt-1" />
        )}
      </button>

      {open && hasDetails && (
        <div className="px-3 pb-3 pt-0 border-t border-border-primary space-y-2">
          {course.note && (
            <p className="text-xs text-text-muted italic pt-2">{course.note}</p>
          )}
          {course.terms_available.length > 0 && (
            <p className="text-xs text-text-muted">
              Offered in:{" "}
              <span className="text-text-secondary">{course.terms_available.join(", ")}</span>
            </p>
          )}
          {hasSuggestions && (
            <div>
              <p className="text-xs text-text-muted mb-1.5 font-medium">
                {course.status === "in_progress"
                  ? "Currently enrolled:"
                  : course.is_elective
                  ? "Courses available this term:"
                  : "Course:"}
              </p>
              <div className="space-y-0.5">
                {course.suggested_courses.map((sc) => (
                  <SuggestedCourseRow key={sc.full_code} course={sc} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Term card ───────────────────────────────────────────────────────────────

function TermCard({ termPlan }: { termPlan: DegreePlanTerm }) {
  const [open, setOpen] = useState(true);
  const isSummer = termPlan.term === "Summer";
  const inProgressCount = termPlan.courses.filter((c) => c.status === "in_progress").length;

  return (
    <div
      className={`rounded-xl border overflow-hidden ${
        termPlan.is_current
          ? "border-accent-blue/40 bg-accent-blue/5"
          : isSummer
          ? "border-accent-orange/25 bg-accent-orange/5"
          : "border-border-primary bg-bg-elevated"
      }`}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-bg-card/50 transition-colors"
      >
        {isSummer ? (
          <Sun size={15} className="text-accent-orange shrink-0" />
        ) : (
          <CalendarDays
            size={15}
            className={termPlan.is_current ? "text-accent-blue shrink-0" : "text-text-muted shrink-0"}
          />
        )}
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-text-primary">{termPlan.label}</span>
            {termPlan.is_current && (
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-accent-blue/15 text-accent-blue border border-accent-blue/30">
                Current
              </span>
            )}
            {isSummer && (
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-accent-orange/15 text-accent-orange border border-accent-orange/30">
                Summer
              </span>
            )}
            {termPlan.study_year && (
              <span className="text-xs text-text-muted/60">
                Year {termPlan.study_year}
                {termPlan.study_year > 4 && (
                  <span className="text-accent-orange ml-1">(extended)</span>
                )}
              </span>
            )}
          </div>
          <p className="text-xs text-text-muted mt-0.5">
            {termPlan.courses.length} course{termPlan.courses.length !== 1 ? "s" : ""} · {termPlan.total_ects} ECTS
            {inProgressCount > 0 && (
              <span className="text-accent-blue ml-1.5">({inProgressCount} in progress)</span>
            )}
          </p>
        </div>
        {open ? (
          <ChevronUp size={14} className="text-text-muted shrink-0" />
        ) : (
          <ChevronDown size={14} className="text-text-muted shrink-0" />
        )}
      </button>

      {open && (
        <div className="px-4 pb-4 pt-1 border-t border-border-primary grid gap-2 sm:grid-cols-2">
          {termPlan.courses.map((course, i) => (
            <CourseChip key={`${course.requirement_name}-${i}`} course={course} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface DegreePlanSectionProps {
  plan: DegreePlan;
}

export function DegreePlanSection({ plan }: DegreePlanSectionProps) {
  if (!plan.terms.length) {
    return (
      <GlassCard className="flex flex-col items-center py-10 text-center">
        <GraduationCap size={32} className="text-text-muted mb-3" />
        <p className="text-sm font-medium text-text-secondary mb-1">
          Degree plan not available for{" "}
          <span className="text-text-primary">{plan.major || "your major"}</span>
        </p>
        <p className="text-xs text-text-muted">
          Set your major and upload your transcript to generate a registration plan.
        </p>
      </GlassCard>
    );
  }

  const totalPending = plan.terms.reduce(
    (sum, t) => sum + t.courses.filter((c) => c.status === "pending").length,
    0,
  );
  const summerTerms = plan.terms.filter((t) => t.term === "Summer" && !t.is_current);

  return (
    <div className="space-y-4">
      {/* Header summary */}
      <GlassCard>
        <div className="flex items-start gap-4">
          <GraduationCap size={22} className="text-accent-green shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-text-primary">
              {plan.graduation_term && plan.graduation_year
                ? `Projected graduation: ${plan.graduation_term} ${plan.graduation_year}`
                : "Graduation timeline not set"}
            </p>
            <p className="text-xs text-text-muted mt-0.5">
              {totalPending} course{totalPending !== 1 ? "s" : ""} remaining across{" "}
              {plan.terms.filter((t) => !t.is_current).length} upcoming semester
              {plan.terms.filter((t) => !t.is_current).length !== 1 ? "s" : ""}
              {summerTerms.length > 0 && (
                <span className="text-accent-orange ml-1.5">
                  including {summerTerms.length} summer session{summerTerms.length !== 1 ? "s" : ""}
                </span>
              )}
            </p>
          </div>
          {plan.needs_extra_time ? (
            <div className="flex items-center gap-1.5 text-xs text-accent-orange shrink-0">
              <AlertTriangle size={13} />
              Extra time needed
            </div>
          ) : (
            plan.graduation_year && (
              <div className="flex items-center gap-1.5 text-xs text-accent-green shrink-0">
                <CheckCircle2 size={13} />
                On track
              </div>
            )
          )}
        </div>

        <div className="flex items-center gap-4 mt-3 text-xs text-text-muted/70">
          <span className="flex items-center gap-1">
            <BookOpen size={11} />
            Required course
          </span>
          <span className="flex items-center gap-1">
            <Sparkles size={11} className="text-accent-orange" />
            Elective — expand to see options
          </span>
          <span className="flex items-center gap-1">
            <Sun size={11} className="text-accent-orange" />
            Summer session
          </span>
        </div>

        <div className="flex items-center gap-2 mt-2">
          <Star size={10} className="text-accent-green" />
          <p className="text-xs text-text-muted/70 leading-relaxed">
            Priority shown for each elective option is based on your current major.
            Priority may change for extended years (5+) — verify with the registrar.
          </p>
        </div>
      </GlassCard>

      {/* Extra-time warning */}
      {plan.needs_extra_time && (
        <div className="flex gap-3 rounded-lg border border-accent-orange/40 bg-accent-orange/10 text-accent-orange px-4 py-3">
          <AlertTriangle size={16} className="shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold">May require extra time</p>
            <p className="text-xs opacity-80 mt-0.5 leading-relaxed">
              Based on your current progress, completing all requirements by{" "}
              {plan.enrollment_year ? `Spring ${plan.enrollment_year + 4}` : "your 4th year"} may not be possible.
              Summer sessions have been included where allowed — consider heavier regular loads too.
            </p>
          </div>
        </div>
      )}

      {/* Term-by-term timeline */}
      <div className="space-y-3">
        {plan.terms.map((termPlan) => (
          <TermCard key={termPlan.label} termPlan={termPlan} />
        ))}
      </div>
    </div>
  );
}
