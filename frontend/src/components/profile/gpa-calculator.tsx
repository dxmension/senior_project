"use client";

import { useMemo, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { LETTER_OPTIONS, LETTER_TO_POINTS, computeGpa } from "@/lib/grade-calc";
import type { EnrollmentItem } from "@/types";

interface Props {
  enrollments: EnrollmentItem[];
}

export function GpaCalculator({ enrollments }: Props) {
  const current = useMemo(
    () => enrollments.filter((e) => e.status === "IN_PROGRESS"),
    [enrollments]
  );
  const [picked, setPicked] = useState<Record<number, string | null>>({});

  const items = current.map((e) => ({
    ects: e.ects ?? 0,
    letter: picked[e.catalog_course_id] ?? null,
  }));
  const { gpa, totalEcts } = computeGpa(items);

  return (
    <div className="space-y-4">
      <GlassCard>
        <div className="flex items-end justify-between">
          <div>
            <p className="text-sm text-text-muted">Projected term GPA</p>
            <p className="font-mono text-3xl font-bold text-accent-green">
              {gpa != null ? gpa.toFixed(2) : "—"}
            </p>
          </div>
          <p className="text-xs text-text-muted">{totalEcts} ECTS graded</p>
        </div>
      </GlassCard>

      <GlassCard padding={false}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-primary text-text-muted">
              <th className="text-left px-4 py-3 font-medium">Code</th>
              <th className="text-left px-4 py-3 font-medium">Course</th>
              <th className="text-right px-4 py-3 font-medium w-20">ECTS</th>
              <th className="text-center px-4 py-3 font-medium w-44">Grade</th>
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
                <td className="px-4 py-3 text-text-primary">{e.course_title}</td>
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
                    className="rounded-lg border border-border-primary bg-bg-card px-2 py-1 text-sm text-text-primary"
                  >
                    <option value="">— pick grade —</option>
                    {LETTER_OPTIONS.map((L) => (
                      <option key={L} value={L}>
                        {L} ({LETTER_TO_POINTS[L].toFixed(2)})
                      </option>
                    ))}
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
