"use client";

import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/ui/glass-card";
import type { EnrollmentItem } from "@/types";

interface EnrollmentHistoryProps {
  enrollments: EnrollmentItem[];
}

function gradeVariant(grade: string | null): "green" | "muted" | "red" {
  if (!grade) return "muted";
  if (grade === "P" || grade === "PASS") return "green";
  if (grade === "NP" || grade === "F") return "red";
  if (grade.startsWith("A")) return "green";
  if (grade.startsWith("B")) return "muted";
  return "red";
}

interface SemesterGroup {
  label: string;
  sortKey: number;
  items: EnrollmentItem[];
}

function termOrder(term: string): number {
  if (term === "Spring") return 0;
  if (term === "Summer") return 1;
  if (term === "Fall") return 2;
  return 99;
}

function termYearLabel(term: string, year: number): string {
  return `${term} ${year}`;
}

function termYearSortKey(term: string, year: number): number {
  return year * 10 + termOrder(term);
}

function groupBySemester(enrollments: EnrollmentItem[]): SemesterGroup[] {
  const map = new Map<string, SemesterGroup>();

  for (const e of enrollments) {
    const key = termYearLabel(e.term, e.year);
    if (!map.has(key)) {
      map.set(key, {
        label: key,
        sortKey: termYearSortKey(e.term, e.year),
        items: [],
      });
    }
    map.get(key)!.items.push(e);
  }

  return Array.from(map.values()).sort((a, b) => b.sortKey - a.sortKey);
}

export function EnrollmentHistory({ enrollments }: EnrollmentHistoryProps) {
  const groups = groupBySemester(enrollments);

  if (groups.length === 0) {
    return (
      <GlassCard className="text-center py-8">
        <p className="text-sm text-text-muted">No course history yet.</p>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-6">
      {groups.map((group) => (
        <div key={group.label}>
          <h3 className="text-sm font-semibold text-text-secondary mb-3">
            {group.label}
          </h3>
          <GlassCard padding={false}>
            <table className="w-full text-sm table-fixed">
              <colgroup>
                <col className="w-32" />
                <col />
                <col className="w-16" />
                <col className="w-24" />
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
                {group.items.map((e) => (
                  <tr
                    key={`${e.course_id}:${e.term}:${e.year}`}
                    className="border-b border-border-primary last:border-0 hover:bg-bg-card-hover transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-accent-green">
                      {e.course_code}
                    </td>
                    <td className="px-4 py-3 text-text-primary truncate">
                      {e.course_title}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-text-secondary">
                      {e.ects ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="inline-flex w-14 justify-center">
                        <Badge variant={gradeVariant(e.grade)}>
                          {e.grade || "—"}
                        </Badge>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </GlassCard>
        </div>
      ))}
    </div>
  );
}
