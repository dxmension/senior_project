"use client";

import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/ui/glass-card";
import type { EnrollmentItem } from "@/types";

interface EnrollmentHistoryProps {
  enrollments: EnrollmentItem[];
}

function gradeVariant(grade: string | null): "green" | "muted" | "red" {
  if (!grade) return "muted";
  if (grade.startsWith("A")) return "green";
  if (grade.startsWith("B")) return "muted";
  return "red";
}

interface SemesterGroup {
  label: string;
  sortKey: number;
  items: EnrollmentItem[];
}

function semesterSortKey(semester: string): number {
  const text = (semester || "").trim();
  if (!text) return -1;

  const match = text.match(/(spring|summer|fall)\s*(\d{4})?/i);
  if (!match) return -1;

  const term = match[1].toLowerCase();
  const termOrder = term === "spring" ? 0 : term === "summer" ? 1 : 2;
  const year = match[2] ? Number(match[2]) : 9999;
  return year * 10 + termOrder;
}

function groupBySemester(enrollments: EnrollmentItem[]): SemesterGroup[] {
  const map = new Map<string, SemesterGroup>();

  for (const e of enrollments) {
    const key = e.semester;
    if (!map.has(key)) {
      map.set(key, { label: key, sortKey: semesterSortKey(key), items: [] });
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
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border-primary text-text-muted">
                  <th className="text-left px-4 py-3 font-medium">Code</th>
                  <th className="text-left px-4 py-3 font-medium">Course</th>
                  <th className="text-center px-4 py-3 font-medium">ECTS</th>
                  <th className="text-center px-4 py-3 font-medium">Grade</th>
                </tr>
              </thead>
              <tbody>
                {group.items.map((e) => (
                  <tr
                    key={e.id}
                    className="border-b border-border-primary last:border-0 hover:bg-bg-card-hover transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-accent-green">
                      {e.course_code}
                    </td>
                    <td className="px-4 py-3 text-text-primary">
                      {e.course_title}
                    </td>
                    <td className="px-4 py-3 text-center text-text-secondary">
                      {e.ects}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={gradeVariant(e.grade)}>
                        {e.grade || "—"}
                      </Badge>
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
