"use client";

import {
  ArrowLeft,
  BookOpen,
  ChevronDown,
  ChevronUp,
  GraduationCap,
  TrendingUp,
  Users,
} from "lucide-react";
import Link from "next/link";
import { use, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { ReviewsTab } from "@/components/catalog/reviews-tab";
import { api } from "@/lib/api";
import type { ApiResponse, CatalogCourse, ProfessorStats, SectionGpaStats } from "@/types";

type Tab = "overview" | "reviews";

// ---------------------------------------------------------------------------
// Grade order + colours
// ---------------------------------------------------------------------------

// Bucket definitions: each letter grade aggregates its sub-grades
const GRADE_BUCKETS: { label: string; keys: string[] }[] = [
  { label: "A", keys: ["A", "A-"] },
  { label: "B", keys: ["B+", "B", "B-"] },
  { label: "C", keys: ["C+", "C", "C-"] },
  { label: "D", keys: ["D+", "D"] },
  { label: "F", keys: ["F"] },
  { label: "W", keys: ["W"] },
  { label: "I", keys: ["I", "AU", "P", "NP"] },
];

function gradeColor(grade: string): string {
  if (grade === "A") return "bg-accent-green";
  if (grade === "B") return "bg-accent-blue";
  if (grade === "C") return "bg-accent-orange";
  return "bg-accent-red";
}

function buildGradeRows(counts: Record<string, number>): [string, number][] {
  return GRADE_BUCKETS
    .map(({ label, keys }) => {
      const count = keys.reduce((s, k) => s + (counts[k] ?? 0), 0);
      return [label, count] as [string, number];
    })
    .filter(([label, count]) => {
      if (["A", "B", "C", "D", "F"].includes(label)) return true;
      return count > 0;
    });
}

/** Convert a section's percentage-based distribution to actual student counts. */
function sectionCounts(sec: SectionGpaStats): Record<string, number> {
  const enrolled = sec.total_enrolled ?? 0;
  if (!enrolled) return {};
  const counts: Record<string, number> = {};
  for (const [grade, pct] of Object.entries(sec.grade_distribution)) {
    counts[grade] = Math.round((pct / 100) * enrolled);
  }
  return counts;
}

/** Merge multiple sections into combined student counts + total enrolled. */
function mergeSections(sections: SectionGpaStats[]): { counts: Record<string, number>; total: number } {
  const counts: Record<string, number> = {};
  let total = 0;
  for (const s of sections) {
    const enrolled = s.total_enrolled ?? 0;
    if (!enrolled) continue;
    total += enrolled;
    for (const [grade, pct] of Object.entries(s.grade_distribution)) {
      const c = Math.round((pct / 100) * enrolled);
      counts[grade] = (counts[grade] ?? 0) + c;
    }
  }
  return { counts, total };
}

// ---------------------------------------------------------------------------
// Grade Distribution Bar Chart
// ---------------------------------------------------------------------------

function GradeChart({ counts }: { counts: Record<string, number> }) {
  const hasAny = Object.values(counts).some((c) => c > 0);
  if (!hasAny) {
    return <p className="text-xs text-text-muted italic">No grade data available.</p>;
  }

  const rows = buildGradeRows(counts);
  const total = rows.reduce((s, [, c]) => s + c, 0);
  const max = Math.max(...rows.map(([, c]) => c));

  return (
    <div className="space-y-1">
      {rows.map(([grade, count]) => {
        const pct = total > 0 ? ((count / total) * 100).toFixed(1) : "0.0";
        const barWidth = max > 0 ? (count / max) * 100 : 0;
        const isEmpty = count === 0;
        return (
          <div key={grade} className="group flex items-center gap-2 relative">
            <span className={`w-7 text-right text-xs font-mono shrink-0 ${isEmpty ? "text-text-muted/40" : "text-text-secondary"}`}>
              {grade}
            </span>
            <div className="relative flex-1 h-4 bg-bg-elevated rounded-sm overflow-visible">
              {!isEmpty && (
                <div
                  className={`h-full rounded-sm ${gradeColor(grade)}`}
                  style={{ width: `${barWidth}%`, opacity: 0.8 }}
                />
              )}
              {!isEmpty && (
                <span className="pointer-events-none absolute left-1/2 -translate-x-1/2 -top-6 z-10 whitespace-nowrap rounded bg-bg-card border border-border-primary px-1.5 py-0.5 text-[10px] text-text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                  {count} ({pct}%)
                </span>
              )}
            </div>
            <span className="w-4 shrink-0" />
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Professor card
// ---------------------------------------------------------------------------

function ProfessorCard({ prof }: { prof: ProfessorStats }) {
  const [open, setOpen] = useState(false);
  const { counts: mergedCounts } = mergeSections(prof.sections);
  const hasChart = Object.keys(mergedCounts).length > 0;

  return (
    <div className="rounded-lg border border-border-primary bg-bg-elevated overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left hover:bg-bg-card transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <GraduationCap size={15} className="text-text-muted shrink-0" />
          <span className="text-sm font-medium text-text-primary truncate">{prof.faculty}</span>
          {prof.avg_gpa != null && (
            <Badge variant={prof.avg_gpa >= 3.0 ? "green" : prof.avg_gpa >= 2.0 ? "orange" : "red"}>
              {prof.avg_gpa.toFixed(2)} GPA
            </Badge>
          )}
          {prof.total_enrolled > 0 && (
            <span className="text-xs text-text-muted flex items-center gap-1">
              <Users size={11} />
              {prof.total_enrolled}
            </span>
          )}
        </div>
        {hasChart &&
          (open ? (
            <ChevronUp size={14} className="text-text-muted shrink-0" />
          ) : (
            <ChevronDown size={14} className="text-text-muted shrink-0" />
          ))}
      </button>

      {open && hasChart && (
        <div className="px-4 pb-4 pt-1 border-t border-border-primary">
          {/* Per-section breakdown — always shown */}
          <div className={prof.sections.length > 1 ? "mb-4 space-y-3" : "mb-0"}>
            {prof.sections.map((sec, i) => {
              const secCounts = sectionCounts(sec);
              if (Object.keys(secCounts).length === 0) return null;
              return (
                <div key={i}>
                  <p className="text-xs text-text-muted mb-1.5">
                    {sec.term} {sec.year}
                    {sec.section ? ` · Section ${sec.section}` : ""}
                    {sec.avg_gpa != null ? ` · ${sec.avg_gpa.toFixed(2)} GPA` : ""}
                  </p>
                  <GradeChart counts={secCounts} />
                </div>
              );
            })}
          </div>
          {/* Combined chart only when multiple sections */}
          {prof.sections.length > 1 && (
            <>
              <p className="text-xs font-medium text-text-secondary mb-2 mt-4">Combined</p>
              <GradeChart counts={mergedCounts} />
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Term badge
// ---------------------------------------------------------------------------

function TermBadge({ term }: { term: string }) {
  const colors: Record<string, string> = {
    Fall: "bg-orange-500/15 text-orange-400 border border-orange-500/30",
    Spring: "bg-green-500/15 text-green-400 border border-green-500/30",
    Summer: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${colors[term] ?? "bg-bg-elevated text-text-muted border border-border-primary"}`}
    >
      {term}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function CourseDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [course, setCourse] = useState<CatalogCourse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  useEffect(() => {
    api
      .get<ApiResponse<CatalogCourse>>(`/courses/catalog/${id}`)
      .then((res) => setCourse(res.data))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load course."))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl">
        <GlassCard className="flex items-center justify-center py-24">
          <Spinner />
        </GlassCard>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Link
          href="/catalog"
          className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors"
        >
          <ArrowLeft size={14} /> Back to catalog
        </Link>
        <GlassCard className="flex flex-col items-center py-16">
          <BookOpen size={36} className="text-text-muted mb-3" />
          <p className="text-sm text-text-secondary">{error ?? "Course not found."}</p>
        </GlassCard>
      </div>
    );
  }

  const { counts: overallCounts, total: gradeTotal } = mergeSections(course.sections);
  const hasGrades = Object.keys(overallCounts).length > 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Back */}
      <Link
        href="/catalog"
        className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors"
      >
        <ArrowLeft size={14} /> Back to catalog
      </Link>

      {/* Header card */}
      <GlassCard>
        <div className="flex flex-col gap-3">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-sm font-semibold text-accent-green">
                {course.code} {course.level}
              </span>
              {course.academic_level && <Badge variant="muted">{course.academic_level}</Badge>}
              {course.ects > 0 && (
                <Badge variant="muted">{course.ects} ECTS</Badge>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {course.avg_gpa != null && (
                <div className="flex items-center gap-1.5">
                  <TrendingUp size={13} className="text-text-muted" />
                  <Badge
                    variant={
                      course.avg_gpa >= 3.0
                        ? "green"
                        : course.avg_gpa >= 2.0
                          ? "orange"
                          : "red"
                    }
                  >
                    {course.avg_gpa.toFixed(2)} avg GPA
                  </Badge>
                </div>
              )}
              {course.total_enrolled != null && (
                <div className="flex items-center gap-1 text-xs text-text-muted" title="Currently enrolled this semester">
                  <Users size={12} />
                  {course.total_enrolled} this semester
                </div>
              )}
            </div>
          </div>

          <h1 className="text-xl font-bold text-text-primary">{course.title}</h1>

          <div className="flex flex-wrap gap-1.5 text-xs text-text-muted">
            {course.department && <span>{course.department}</span>}
            {course.department && course.school && <span>·</span>}
            {course.school && <span>{course.school}</span>}
          </div>

          {course.terms_available.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {course.terms_available.map((t) => (
                <TermBadge key={t} term={t} />
              ))}
            </div>
          )}
        </div>
      </GlassCard>

      {/* Tabs */}
      <div>
        <div className="flex gap-1 border-b border-border-primary mb-6">
          {(["overview", "reviews"] as Tab[]).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px capitalize ${
                activeTab === tab
                  ? "border-accent-green text-text-primary"
                  : "border-transparent text-text-muted hover:text-text-secondary"
              }`}
            >
              {tab === "overview" ? "Overview" : "Reviews"}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Description */}
            {(course.description || course.prerequisites) && (
              <GlassCard>
                <div className="space-y-4">
                  {course.description && (
                    <div>
                      <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                        Description
                      </h2>
                      <p className="text-sm text-text-secondary leading-relaxed">{course.description}</p>
                    </div>
                  )}
                  {course.prerequisites && (
                    <div>
                      <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                        Prerequisites
                      </h2>
                      <p className="text-sm text-text-secondary">{course.prerequisites}</p>
                    </div>
                  )}
                </div>
              </GlassCard>
            )}

            {/* Overall grade distribution */}
            {hasGrades && (
              <GlassCard>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-text-primary">
                    Overall Grade Distribution
                  </h2>
                  {gradeTotal > 0 && (
                    <span className="text-xs text-text-muted">
                      based on {gradeTotal} students
                    </span>
                  )}
                </div>
                <GradeChart counts={overallCounts} />
              </GlassCard>
            )}

            {/* Per-professor */}
            {course.professors.length > 0 && (
              <div>
                <h2 className="text-sm font-semibold text-text-primary mb-3">By Professor</h2>
                <div className="space-y-2">
                  {course.professors.map((prof) => (
                    <ProfessorCard key={prof.faculty} prof={prof} />
                  ))}
                </div>
              </div>
            )}

            {!hasGrades && course.professors.length === 0 && (
              <GlassCard className="flex flex-col items-center py-12">
                <TrendingUp size={32} className="text-text-muted mb-3" />
                <p className="text-sm text-text-secondary">No grade statistics available yet.</p>
              </GlassCard>
            )}
          </div>
        )}

        {activeTab === "reviews" && (
          <ReviewsTab courseId={Number(id)} />
        )}
      </div>
    </div>
  );
}
