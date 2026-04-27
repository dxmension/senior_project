"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";

import { AiInsightsPanel } from "@/components/study/ai-insights-panel";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { predictedGradeBadge } from "@/lib/predicted-grade";
import { resolveStudyRouteCourseId } from "@/lib/study-course-route";
import type {
  ApiResponse,
  EnrollmentItem,
  InsightsData,
  MockExamCourseGroup,
} from "@/types";

type StudyCourseGroup = MockExamCourseGroup & { route_course_id: number };

export default function StudyPage() {
  const [groups, setGroups] = useState<StudyCourseGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  useEffect(() => {
    async function loadStudyCourses() {
      setLoading(true);
      setError(null);
      try {
        const [studyResponse, enrollmentResponse] = await Promise.all([
          api.get<ApiResponse<MockExamCourseGroup[]>>("/mock-exams"),
          api.get<ApiResponse<EnrollmentItem[]>>("/enrollments?status=in_progress"),
        ]);
        setGroups(
          withRouteCourseIds(
            studyResponse.data ?? [],
            enrollmentResponse.data ?? [],
          ),
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load study courses";
        setError(message);
      } finally {
        setLoading(false);
      }
    }

    async function loadInsights() {
      setInsightsLoading(true);
      setInsightsError(null);
      try {
        const insightsResponse = await api.get<ApiResponse<InsightsData>>("/insights");
        setInsights(insightsResponse.data);
      } catch (err) {
        setInsightsError(
          err instanceof Error ? err.message : "Failed to load insights",
        );
        setInsights(null);
      } finally {
        setInsightsLoading(false);
      }
    }

    void loadStudyCourses();
    void loadInsights();
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Study Assistant</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Choose a course to open its study tools.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner text="Loading study courses..." />
        </div>
      ) : error ? (
        <GlassCard>
          <p className="text-sm text-accent-red">{error}</p>
        </GlassCard>
      ) : groups.length === 0 ? (
        <GlassCard className="py-14 text-center">
          <p className="text-lg font-semibold text-text-primary">No current courses found</p>
          <p className="mt-2 text-sm text-text-secondary">
            Add or sync your current enrollments to unlock course-specific study flows.
          </p>
        </GlassCard>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <AiInsightsPanel
            data={insights}
            loading={insightsLoading}
            error={insightsError}
          />

          <div className="flex min-w-0 flex-col gap-5">
            {groups.map((group) => (
              <StudyCourseCard key={group.route_course_id} group={group} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StudyCourseCard({ group }: { group: StudyCourseGroup }) {
  const grade = predictedGradeBadge(
    group.predicted_grade_letter,
    group.predicted_score_pct,
  );

  return (
    <Link href={`/study/${group.route_course_id}`} className="block w-full">
      <GlassCard
        padding={false}
        className="w-full cursor-pointer overflow-hidden border-border-primary !bg-white/[0.03]
          transition-all duration-200 hover:border-accent-green/40 hover:!bg-white/[0.05]"
      >
        <div className="flex flex-wrap items-center justify-between gap-5 px-7 py-6">
          <div className="min-w-0 flex-1">
            <p className="font-mono text-sm font-semibold text-accent-green">
              {group.course_code}
            </p>
            <h2 className="mt-1 text-lg font-semibold text-text-primary">
              {group.course_title}
            </h2>
          </div>
          <div className="flex shrink-0 items-center gap-4">
            <div className="flex min-w-[140px] flex-col items-end text-right">
              <p className="text-[11px] uppercase tracking-[0.18em] text-text-secondary">
                Predicted Grade
              </p>
              <div className="mt-1 flex items-center gap-2">
                <span
                  className={`rounded-full px-3 py-1 text-sm font-semibold ring-1 ${grade.badgeClass}`}
                >
                  {grade.letter}
                </span>
                <span className={`text-sm font-medium ${grade.textClass}`}>
                  {grade.scoreLabel}
                </span>
              </div>
            </div>
            <ArrowRight size={16} className="text-text-secondary" />
          </div>
        </div>
      </GlassCard>
    </Link>
  );
}

function withRouteCourseIds(
  groups: MockExamCourseGroup[],
  enrollments: EnrollmentItem[],
): StudyCourseGroup[] {
  return groups.map((group) => ({
    ...group,
    route_course_id: resolveStudyRouteCourseId(enrollments, group.course_id),
  }));
}
