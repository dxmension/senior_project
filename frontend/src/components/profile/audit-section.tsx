"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Circle,
  Clock,
  ChevronDown,
  ChevronUp,
  GraduationCap,
  AlertTriangle,
  CalendarClock,
} from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import type { AuditResult, AuditCategory, AuditRequirement } from "@/types";

// ─── 5th-year risk calculation ────────────────────────────────────────────────

type Term = "Fall" | "Spring" | "Summer";

function getCurrentTerm(): Term {
  const m = new Date().getMonth() + 1; // 1–12
  if (m <= 5) return "Spring";
  if (m <= 8) return "Summer";
  return "Fall";
}

// Semesters remaining AFTER the current one, within a standard 4-year plan.
// "regular" = Fall or Spring (24–36 ECTS each).
// "summers" = optional Summer sessions (6–16 ECTS each).
// The summer after 4th year counts as a last-chance session before a 5th year.
const SEMESTERS_AFTER: Record<string, { regular: number; summers: number }> = {
  "1-Fall":   { regular: 7, summers: 4 },
  "1-Spring": { regular: 6, summers: 4 },
  "1-Summer": { regular: 6, summers: 3 },
  "2-Fall":   { regular: 5, summers: 3 },
  "2-Spring": { regular: 4, summers: 3 },
  "2-Summer": { regular: 4, summers: 2 },
  "3-Fall":   { regular: 3, summers: 2 },
  "3-Spring": { regular: 2, summers: 2 },
  "3-Summer": { regular: 2, summers: 1 },
  "4-Fall":   { regular: 1, summers: 1 },  // 4th-Spring + last-chance 4th-Summer
  "4-Spring": { regular: 0, summers: 1 },  // only last-chance 4th-Summer remains
  "4-Summer": { regular: 0, summers: 0 },  // already in last-chance summer
};

interface RiskInfo {
  /** True if finishing in 4 years is impossible even at max load (36/16 ECTS). */
  needsFifthYear: boolean;
  /** True if regular semesters alone are not enough — at least one summer session needed. */
  needsSummer: boolean;
  stillNeeded: number;
  maxAchievable: number;   // at 36 regular + 16 summer
  regularMax: number;      // at 36 per regular semester only
  remaining: { regular: number; summers: number };
  term: Term;
}

function computeRisk(
  audit: AuditResult,
  studyYear: number | null | undefined,
): RiskInfo | null {
  if (!studyYear || studyYear < 1 || studyYear > 4) return null;

  const term = getCurrentTerm();
  const key = `${studyYear}-${term}`;
  const remaining = SEMESTERS_AFTER[key];
  if (!remaining) return null;

  // After the current semester ends, this much is still outstanding.
  const stillNeeded =
    audit.total_ects - audit.completed_ects - audit.in_progress_ects;

  const regularMax = remaining.regular * 36;
  const summerMax = remaining.summers * 16;
  const maxAchievable = regularMax + summerMax;

  if (stillNeeded <= 0) {
    return {
      needsFifthYear: false,
      needsSummer: false,
      stillNeeded: 0,
      maxAchievable,
      regularMax,
      remaining,
      term,
    };
  }

  // Split outstanding ECTS by whether the required courses can be taken in summer.
  // A requirement is "summer-eligible" only if at least one of its courses is
  // actually offered during Summer.  If terms_available is empty (data not loaded),
  // we conservatively assume all terms are available.
  let regularOnlyEcts = 0;  // ECTS whose courses are never offered in summer
  let summerEligibleEcts = 0;  // ECTS whose courses are sometimes offered in summer

  for (const cat of audit.categories) {
    for (const req of cat.requirements) {
      const outstanding = Math.max(
        0,
        req.required_count - req.completed_count - req.in_progress_count,
      );
      if (outstanding === 0) continue;
      const outstandingEcts = outstanding * req.ects_per_course;

      const canTakeInSummer =
        req.terms_available.length === 0 ||  // unknown → assume flexible
        req.terms_available.includes("Summer");

      if (canTakeInSummer) {
        summerEligibleEcts += outstandingEcts;
      } else {
        regularOnlyEcts += outstandingEcts;
      }
    }
  }

  // Regular-only courses MUST fit in regular semesters.
  // If they overflow, no amount of summer sessions can help.
  const needsFifthYear =
    regularOnlyEcts > regularMax ||
    stillNeeded > maxAchievable;

  // Needs summer: total doesn't fit in regular semesters alone,
  // but does fit when summer is included.
  const needsSummer = !needsFifthYear && stillNeeded > regularMax;

  return { needsFifthYear, needsSummer, stillNeeded, maxAchievable, regularMax, remaining, term };
}

// ─── Display name normalisation ───────────────────────────────────────────────

const ELECTIVE_ALIASES: Record<string, string> = {
  "cs electives": "Technical Electives",
  "csci electives": "Technical Electives",
  "elce electives": "Technical Electives",
  "mae electives": "Technical Electives",
  "cee electives": "Technical Electives",
  "chme electives": "Technical Electives",
  "robt electives": "Technical Electives",
};

function displayName(name: string): string {
  return ELECTIVE_ALIASES[name.toLowerCase()] ?? name;
}

// ─── Colour helpers ───────────────────────────────────────────────────────────

function statusColor(status: string) {
  if (status === "completed") return "text-accent-green";
  if (status === "in_progress") return "text-accent-blue";
  return "text-text-muted";
}

function statusIcon(status: string) {
  if (status === "completed")
    return <CheckCircle2 size={14} className="text-accent-green shrink-0" />;
  if (status === "in_progress")
    return <Clock size={14} className="text-accent-blue shrink-0" />;
  return <Circle size={14} className="text-text-muted/40 shrink-0" />;
}

function progressColor(pct: number) {
  if (pct >= 100) return "bg-accent-green";
  if (pct >= 60) return "bg-accent-blue";
  if (pct >= 30) return "bg-accent-orange";
  return "bg-accent-red";
}

// ─── Requirement row ──────────────────────────────────────────────────────────

function RequirementRow({ req }: { req: AuditRequirement }) {
  const [open, setOpen] = useState(false);
  const showCourses = req.matched_courses.length > 0;
  const countLabel =
    req.required_count > 1
      ? `${req.completed_count}/${req.required_count}`
      : null;

  return (
    <div>
      <button
        type="button"
        onClick={() => showCourses && setOpen((v) => !v)}
        className={`w-full flex items-center gap-2 py-1.5 text-left ${showCourses ? "cursor-pointer" : "cursor-default"}`}
      >
        {statusIcon(req.status)}
        <span className={`flex-1 text-sm ${statusColor(req.status)}`}>
          {displayName(req.name)}
        </span>
        {countLabel && (
          <span className="text-xs text-text-muted font-mono shrink-0">
            {countLabel}
          </span>
        )}
        {req.note && !showCourses && (
          <span className="text-xs text-text-muted/60 italic truncate max-w-[140px]">
            {req.note}
          </span>
        )}
        {showCourses &&
          (open ? (
            <ChevronUp size={12} className="text-text-muted shrink-0" />
          ) : (
            <ChevronDown size={12} className="text-text-muted shrink-0" />
          ))}
      </button>

      {open && showCourses && (
        <div className="ml-5 mb-1 flex flex-wrap gap-1.5">
          {req.matched_courses.map((mc) => (
            <span
              key={mc.code}
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs border ${
                mc.status === "passed"
                  ? "bg-accent-green/10 text-accent-green border-accent-green/25"
                  : "bg-accent-blue/10 text-accent-blue border-accent-blue/25"
              }`}
            >
              {mc.code}
              {mc.status === "in_progress" && (
                <Clock size={9} className="opacity-70" />
              )}
            </span>
          ))}
          {req.note && (
            <span className="text-xs text-text-muted/60 italic self-center">
              {req.note}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Category card ────────────────────────────────────────────────────────────

function CategoryCard({ cat, showWarning }: { cat: AuditCategory; showWarning: boolean }) {
  const [open, setOpen] = useState(true);
  const pct = cat.total_ects > 0 ? Math.round((cat.completed_ects / cat.total_ects) * 100) : 0;
  const allDone = cat.requirements.every((r) => r.status === "completed");
  // Warning shown only when the student is globally at risk AND this category
  // has unstarted requirements — those are the blockers.
  const anyMissing = cat.requirements.some((r) => r.status === "missing");

  return (
    <div className="rounded-lg border border-border-primary bg-bg-elevated overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-bg-card transition-colors"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-sm font-medium text-text-primary">{cat.name}</span>
            {allDone && (
              <CheckCircle2 size={13} className="text-accent-green shrink-0" />
            )}
            {!allDone && anyMissing && showWarning && (
              <AlertTriangle size={13} className="text-accent-orange shrink-0" />
            )}
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-bg-card rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${progressColor(pct)}`}
                style={{ width: `${Math.min(pct, 100)}%` }}
              />
            </div>
            <span className="text-xs text-text-muted shrink-0 font-mono">
              {cat.completed_ects}/{cat.total_ects} ECTS
            </span>
          </div>
        </div>
        {open ? (
          <ChevronUp size={14} className="text-text-muted shrink-0" />
        ) : (
          <ChevronDown size={14} className="text-text-muted shrink-0" />
        )}
      </button>

      {open && (
        <div className="px-4 pb-3 pt-1 border-t border-border-primary space-y-0.5">
          {cat.requirements.map((req, i) => (
            <RequirementRow key={`${req.name}-${i}`} req={req} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Risk banner ──────────────────────────────────────────────────────────────

function RiskBanner({ risk }: { risk: RiskInfo }) {
  const { needsFifthYear, needsSummer, stillNeeded, maxAchievable, regularMax, remaining } = risk;

  // All requirements completed or in progress
  if (stillNeeded <= 0) {
    return (
      <div className="flex gap-3 rounded-lg border border-accent-green/40 bg-accent-green/10 text-accent-green px-4 py-3">
        <CalendarClock size={16} className="shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <p className="text-sm font-semibold">All requirements on track</p>
          <p className="text-xs opacity-80 leading-relaxed">
            All remaining degree requirements are completed or currently in progress. You are on track to graduate on time.
          </p>
        </div>
      </div>
    );
  }

  // On track — regular semesters are sufficient
  if (!needsFifthYear && !needsSummer) {
    return (
      <div className="flex gap-3 rounded-lg border border-accent-green/40 bg-accent-green/10 text-accent-green px-4 py-3">
        <CalendarClock size={16} className="shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-sm font-semibold">On track to graduate in 4 years</p>
          <p className="text-xs opacity-80 leading-relaxed">
            You have {stillNeeded} ECTS remaining, which fits within your {remaining.regular} remaining regular semester{remaining.regular !== 1 ? "s" : ""} (up to {regularMax} ECTS at maximum load of 36 ECTS/semester).
          </p>
          <p className="text-xs opacity-60 italic">
            Note: some courses are only offered in Fall or Spring — factor this in when planning each semester.
          </p>
        </div>
      </div>
    );
  }

  // Needs at least one summer session to stay on track
  if (needsSummer) {
    const isLastChanceSummer = remaining.regular === 0 && remaining.summers === 1;
    return (
      <div className="flex gap-3 rounded-lg border border-accent-orange/40 bg-accent-orange/10 text-accent-orange px-4 py-3">
        <CalendarClock size={16} className="shrink-0 mt-0.5" />
        <div className="space-y-1.5">
          <p className="text-sm font-semibold">Summer session required to graduate on time</p>
          <p className="text-xs opacity-80 leading-relaxed">
            You have {stillNeeded} ECTS remaining. Regular semesters alone can cover up to {regularMax} ECTS — you will need at least one summer session (6–16 ECTS) to stay on track.
          </p>
          {isLastChanceSummer && (
            <p className="text-xs opacity-80 leading-relaxed">
              The summer after your 4th year is your final opportunity to complete remaining credits before a 5th year becomes necessary.
            </p>
          )}
          <p className="text-xs opacity-60 italic">
            Note: some courses are only offered in Fall or Spring — verify availability before selecting summer courses.
          </p>
        </div>
      </div>
    );
  }

  // Needs 5th year — can't finish even at max load including all summers
  const breakdown: string[] = [];
  if (remaining.regular > 0)
    breakdown.push(`${remaining.regular} semester${remaining.regular > 1 ? "s" : ""} × 36 ECTS = ${remaining.regular * 36} ECTS`);
  if (remaining.summers > 0)
    breakdown.push(`${remaining.summers} summer${remaining.summers > 1 ? "s" : ""} × 16 ECTS = ${remaining.summers * 16} ECTS`);

  return (
    <div className="flex gap-3 rounded-lg border border-accent-red/40 bg-accent-red/10 text-accent-red px-4 py-3">
      <CalendarClock size={16} className="shrink-0 mt-0.5" />
      <div className="space-y-1.5">
        <p className="text-sm font-semibold">5th year likely required</p>
        <p className="text-xs opacity-80 leading-relaxed">
          You need {stillNeeded} more ECTS to graduate, but only {maxAchievable} ECTS are achievable at maximum load in the remaining time{breakdown.length > 0 ? ` (${breakdown.join(" + ")})` : ""}.
        </p>
        <p className="text-xs opacity-80 leading-relaxed">
          Some courses are only offered in Fall or Spring — this further reduces how many ECTS you can realistically take each term.
        </p>
        <p className="text-xs opacity-80 leading-relaxed">
          {remaining.summers > 0
            ? "Even using all available summer sessions at maximum capacity, graduation within 4 years is not possible."
            : "No summer sessions remain in your 4-year plan to compensate."}
        </p>
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface AuditSectionProps {
  audit: AuditResult;
  studyYear?: number | null;
}

export function AuditSection({ audit, studyYear }: AuditSectionProps) {
  if (!audit.supported) {
    return (
      <GlassCard className="flex flex-col items-center py-10 text-center">
        <GraduationCap size={32} className="text-text-muted mb-3" />
        <p className="text-sm font-medium text-text-secondary mb-1">
          Degree audit not available for{" "}
          <span className="text-text-primary">{audit.major || "your major"}</span>
        </p>
        <p className="text-xs text-text-muted">
          Set your major in your profile to see degree progress.
        </p>
      </GlassCard>
    );
  }

  const completedPct =
    audit.total_ects > 0
      ? Math.min(100, Math.round((audit.completed_ects / audit.total_ects) * 100))
      : 0;
  const withInProgressPct =
    audit.total_ects > 0
      ? Math.min(100, Math.round(((audit.completed_ects + audit.in_progress_ects) / audit.total_ects) * 100))
      : 0;

  const risk = computeRisk(audit, studyYear);
  const atRisk = risk ? risk.needsFifthYear : false;

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <GlassCard>
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-text-primary">
                Overall Progress
              </span>
              <span className="text-sm font-mono text-text-secondary">
                {audit.completed_ects} / {audit.total_ects} ECTS
                {audit.in_progress_ects > 0 && (
                  <span className="text-accent-blue ml-1.5">
                    (+{audit.in_progress_ects} in progress)
                  </span>
                )}
              </span>
            </div>
            {/* Stacked bar: completed (solid) + in-progress (lighter) */}
            <div className="h-2.5 bg-bg-elevated rounded-full overflow-hidden relative">
              {audit.in_progress_ects > 0 && (
                <div
                  className="absolute h-full rounded-full bg-accent-blue/30"
                  style={{ width: `${withInProgressPct}%` }}
                />
              )}
              <div
                className={`relative h-full rounded-full ${progressColor(completedPct)}`}
                style={{ width: `${completedPct}%` }}
              />
            </div>
          </div>
          <div className="text-2xl font-bold text-text-primary shrink-0 font-mono">
            {completedPct}%
          </div>
        </div>
        <div className="flex items-center gap-4 mt-3 text-xs text-text-muted">
          <span className="flex items-center gap-1">
            <CheckCircle2 size={11} className="text-accent-green" />
            Completed
          </span>
          <span className="flex items-center gap-1">
            <Clock size={11} className="text-accent-blue" />
            In Progress
          </span>
          <span className="flex items-center gap-1">
            <Circle size={11} className="text-text-muted/40" />
            Missing
          </span>
        </div>
      </GlassCard>

      {/* Risk banner — only when graduation timeline is threatened */}
      {risk && <RiskBanner risk={risk} />}

      {/* Category breakdown */}
      <div className="space-y-2">
        {audit.categories.map((cat) => (
          <CategoryCard key={cat.name} cat={cat} showWarning={atRisk} />
        ))}
      </div>
    </div>
  );
}
