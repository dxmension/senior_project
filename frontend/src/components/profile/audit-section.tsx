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
const SEMESTERS_AFTER: Record<string, { regular: number; summers: number }> = {
  "1-Fall":   { regular: 7, summers: 3 },
  "1-Spring": { regular: 6, summers: 3 },
  "1-Summer": { regular: 6, summers: 2 },
  "2-Fall":   { regular: 5, summers: 2 },
  "2-Spring": { regular: 4, summers: 2 },
  "2-Summer": { regular: 4, summers: 1 },
  "3-Fall":   { regular: 3, summers: 1 },
  "3-Spring": { regular: 2, summers: 1 },
  "3-Summer": { regular: 2, summers: 0 },
  "4-Fall":   { regular: 1, summers: 0 },
  "4-Spring": { regular: 0, summers: 0 },
  "4-Summer": { regular: 0, summers: 0 },
};

interface RiskInfo {
  /** True if finishing in 4 years is impossible even at max load (36/16 ECTS). */
  needsFifthYear: boolean;
  /**
   * True if finishing requires at least one summer session or near-max load
   * every semester — i.e. there's no comfortable margin.
   */
  tight: boolean;
  stillNeeded: number;
  maxAchievable: number;   // at 36 regular + 16 summer
  minPerSemester: number;  // avg ECTS/semester needed (regular only)
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

  if (stillNeeded <= 0) {
    return {
      needsFifthYear: false,
      tight: false,
      stillNeeded: 0,
      maxAchievable: 0,
      minPerSemester: 0,
      remaining,
      term,
    };
  }

  // Max physically achievable: 36 ECTS/regular + 16 ECTS/summer.
  const maxAchievable = remaining.regular * 36 + remaining.summers * 16;

  // Needs 5th year: can't finish even at absolute max load.
  const needsFifthYear = stillNeeded > maxAchievable;

  // Tight: needs summers OR needs >30 ECTS every remaining regular semester.
  const comfortableMax = remaining.regular * 30; // ~30 is a full but manageable semester
  const tight = !needsFifthYear && stillNeeded > comfortableMax;

  // Average regular-semester load needed (excluding summers, conservative).
  const minPerSemester =
    remaining.regular > 0 ? Math.ceil(stillNeeded / remaining.regular) : Infinity;

  return { needsFifthYear, tight, stillNeeded, maxAchievable, minPerSemester, remaining, term };
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
  const { needsFifthYear, tight, stillNeeded, minPerSemester, remaining } = risk;

  if (!needsFifthYear && !tight) return null;

  const color = needsFifthYear
    ? "border-accent-red/40 bg-accent-red/10 text-accent-red"
    : "border-accent-orange/40 bg-accent-orange/10 text-accent-orange";

  const title = needsFifthYear
    ? "5th year likely required"
    : "Graduation timeline is tight";

  const body = needsFifthYear
    ? `${stillNeeded} ECTS remaining after this semester, but only ${remaining.regular * 36 + remaining.summers * 16} ECTS achievable at maximum load in the time left.`
    : `You need ~${minPerSemester} ECTS/semester to graduate on time${remaining.summers > 0 ? ", possibly including summer sessions" : ""}.`;

  const note =
    "Note: some courses are only offered in Fall or Spring — check availability when planning each semester.";

  return (
    <div className={`flex gap-3 rounded-lg border px-4 py-3 ${color}`}>
      <CalendarClock size={16} className="shrink-0 mt-0.5" />
      <div className="space-y-0.5">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs opacity-80">{body}</p>
        <p className="text-xs opacity-60 italic">{note}</p>
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
  const atRisk = risk ? risk.needsFifthYear || risk.tight : false;

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
