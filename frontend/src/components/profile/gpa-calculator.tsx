"use client";

import { useMemo, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { LETTER_OPTIONS, INTERNSHIP_OPTIONS, LETTER_TO_POINTS, computeGpa } from "@/lib/grade-calc";
import { useAuthStore } from "@/stores/auth";
import type { EnrollmentItem } from "@/types";

interface Props {
  enrollments: EnrollmentItem[];
}

function gpaColor(val: number | null): string {
  if (val === null) return "text-text-primary";
  if (val >= 3.5) return "text-accent-green";
  if (val >= 2.5) return "text-yellow-400";
  return "text-red-400";
}

export function GpaCalculator({ enrollments }: Props) {
  const { user } = useAuthStore();
  const current = useMemo(
    () => enrollments.filter((e) => e.status === "in_progress"),
    [enrollments]
  );
  const [picked, setPicked] = useState<Record<number, string | null>>({});

  const items = current.map((e) => ({
    ects: e.ects ?? 0,
    letter: picked[e.catalog_course_id] ?? null,
  }));
  const { gpa, totalEcts } = computeGpa(items);
  const cgpa = user?.cgpa ?? null;
  const earnedCredits = user?.total_credits_earned ?? 0;

  // Projected CGPA: weighted blend of past CGPA and this term's projected GPA
  const projectedCgpa = useMemo(() => {
    if (gpa === null) return cgpa;
    if (cgpa === null || earnedCredits === 0) return gpa;
    const total = earnedCredits + totalEcts;
    if (total === 0) return null;
    return Math.round(((cgpa * earnedCredits + gpa * totalEcts) / total) * 100) / 100;
  }, [gpa, cgpa, earnedCredits, totalEcts]);

  return (
    <div className="space-y-4">
      <GlassCard>
        <div className="flex items-center justify-between flex-wrap gap-6">
          <div className="flex gap-10">
            <div>
              <p className="text-sm text-text-muted mb-1">Projected Term GPA</p>
              <p className={`font-mono text-3xl font-bold ${gpaColor(gpa)}`}>
                {gpa != null ? gpa.toFixed(2) : "—"}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted mb-1">Current CGPA</p>
              <p className={`font-mono text-3xl font-bold ${gpaColor(cgpa)}`}>
                {cgpa != null ? cgpa.toFixed(2) : "—"}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted mb-1">Projected CGPA</p>
              <p className={`font-mono text-3xl font-bold ${gpaColor(projectedCgpa)}`}>
                {projectedCgpa != null ? projectedCgpa.toFixed(2) : "—"}
              </p>
            </div>
          </div>
          <p className="text-xs text-text-muted">{totalEcts} ECTS graded this term</p>
        </div>
      </GlassCard>

      <GlassCard padding={false}>
        <table className="w-full text-sm table-fixed">
          <colgroup>
            <col className="w-28" />
            <col />
            <col className="w-16" />
            <col className="w-48" />
          </colgroup>
          <thead>
            <tr className="border-b border-border-primary text-text-muted">
              <th className="text-left px-4 py-3 font-medium">Code</th>
              <th className="text-left px-4 py-3 font-medium">Course</th>
              <th className="text-right px-4 py-3 font-medium">ECTS</th>
              <th className="text-center px-4 py-3 font-medium">Grade</th>
            </tr>
          </thead>
          <tbody>
            {current.map((e) => (
              <tr
                key={e.catalog_course_id}
                className="border-b border-border-primary last:border-0 hover:bg-bg-card-hover transition-colors"
              >
                <td className="px-4 py-3 font-mono text-xs text-accent-green">
                  {e.course_code}
                </td>
                <td className="px-4 py-3 text-text-primary truncate">{e.course_title}</td>
                <td className="px-4 py-3 text-right font-mono text-text-secondary">
                  {e.ects ?? "—"}
                </td>
                <td className="px-4 py-3 text-center">
                  <select
                    value={picked[e.catalog_course_id] ?? ""}
                    onChange={(ev) =>
                      setPicked((p) => ({
                        ...p,
                        [e.catalog_course_id]: ev.target.value || null,
                      }))
                    }
                    className="w-full rounded-lg border border-border-primary bg-bg-card px-2 py-1.5 text-sm text-text-primary"
                  >
                    <option value="">— pick grade —</option>
                    {(e.course_title?.toLowerCase().includes("internship")
                      ? INTERNSHIP_OPTIONS
                      : LETTER_OPTIONS
                    ).map((L) => {
                      const pts = LETTER_TO_POINTS[L] !== undefined
                        ? LETTER_TO_POINTS[L].toFixed(2)
                        : L === "Pass" ? "no GPA impact" : "0.00";
                      return (
                        <option key={L} value={L}>
                          {L} ({pts})
                        </option>
                      );
                    })}
                  </select>
                </td>
              </tr>
            ))}
            {current.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-text-muted">
                  No current courses.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
}
