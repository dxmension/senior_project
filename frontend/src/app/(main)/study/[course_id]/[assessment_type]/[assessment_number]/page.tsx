"use client";

import Link from "next/link";
import { use, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Brain, LoaderCircle, PlayCircle } from "lucide-react";

import { MockExamCountdown } from "@/components/study/mock-exam-countdown";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { predictedGradeBadge } from "@/lib/predicted-grade";
import { findStudyGroupByRouteCourseId } from "@/lib/study-course-route";
import { findMockExamFamily, sortMockExams } from "@/lib/study-mock-families";
import type {
  ApiResponse,
  Assessment,
  EnrollmentItem,
  MockExamGenerationQueued,
  MockExamCourseGroup,
  MockExamListItem,
} from "@/types";

type PageParams = Promise<{
  course_id: string;
  assessment_type: string;
  assessment_number: string;
}>;

function scoreTone(score: number | null) {
  if (score == null) return "text-text-secondary";
  if (score < 60) return "text-accent-red";
  if (score < 80) return "text-accent-orange";
  return "text-accent-green";
}

function scoreLabel(score: number | null) {
  return score == null ? "—" : `${score}%`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function primaryAction(item: MockExamListItem) {
  return item.has_active_attempt ? "Resume Mock Exam" : "Start Mock Exam";
}

export default function StudyAssessmentFamilyPage({
  params,
}: {
  params: PageParams;
}) {
  const { course_id, assessment_type, assessment_number } = use(params);
  const router = useRouter();
  const courseId = Number(course_id);
  const assessmentNumber = Number(assessment_number);
  const [group, setGroup] = useState<MockExamCourseGroup | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const examsBeforeGenerate = useRef<number>(0);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function loadFamilyData(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const [studyResponse, enrollmentResponse, assessmentsResponse] =
        await Promise.all([
          api.get<ApiResponse<MockExamCourseGroup[]>>("/mock-exams"),
          api.get<ApiResponse<EnrollmentItem[]>>(
            "/enrollments?status=in_progress"
          ),
          api.get<ApiResponse<Assessment[]>>(
            `/assessments?course_id=${courseId}`
          ),
        ]);
      const next = findStudyGroupByRouteCourseId(
        studyResponse.data ?? [],
        enrollmentResponse.data ?? [],
        courseId,
      );
      if (!next) {
        throw new Error("Study course not found");
      }
      setGroup(next);
      setAssessments(assessmentsResponse.data ?? []);
    } catch (err) {
      const message = err instanceof Error
        ? err.message
        : "Failed to load assessment family";
      setError(message);
    } finally {
      if (!silent) setLoading(false);
    }
  }

  useEffect(() => {
    void loadFamilyData();
  }, [courseId]);

  const family = useMemo(
    () => (
      group
        ? findMockExamFamily(group.exams, assessment_type, assessmentNumber)
        : null
    ),
    [assessmentNumber, assessment_type, group],
  );
  const familyExams = useMemo(
    () => (family ? sortMockExams(family.exams) : []),
    [family],
  );
  const assessment = useMemo(
    () => assessments.find((item) => (
      item.assessment_type === assessment_type
      && item.assessment_number === assessmentNumber
    )) ?? null,
    [assessmentNumber, assessment_type, assessments],
  );
  const predicted = predictedGradeBadge(
    family?.predictedLetter ?? null,
    family?.predictedScore ?? null,
  );

  function stopPolling() {
    if (pollIntervalRef.current !== null) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }

  // Stop polling and mark done when a new exam appears
  useEffect(() => {
    if (!isGenerating) return;
    if (familyExams.length > examsBeforeGenerate.current) {
      stopPolling();
      setIsGenerating(false);
    }
  }, [familyExams.length, isGenerating]);

  useEffect(() => () => stopPolling(), []);

  async function handleGenerateMock() {
    if (!assessment) return;
    examsBeforeGenerate.current = familyExams.length;
    setIsGenerating(true);
    try {
      await api.post<ApiResponse<MockExamGenerationQueued>>(
        `/assessments/${assessment.id}/generate-mock-exam`
      );
    } catch {
      setIsGenerating(false);
      return;
    }
    // Poll every 2.5s, max 60s
    let elapsed = 0;
    pollIntervalRef.current = setInterval(() => {
      elapsed += 2500;
      void loadFamilyData(true);
      if (elapsed >= 60000) {
        stopPolling();
        setIsGenerating(false);
      }
    }, 2500);
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading assessment family..." />
      </div>
    );
  }

  if (error || !group || !family) {
    return (
      <GlassCard className="space-y-3">
        <p className="text-sm text-accent-red">
          {error ?? "Assessment family not found"}
        </p>
        <button
          type="button"
          onClick={() => router.push(`/study/${courseId}`)}
          className="btn-secondary rounded-lg px-4 py-2 text-sm"
        >
          Back to Course Study
        </button>
      </GlassCard>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <button
        type="button"
        onClick={() => router.push(`/study/${courseId}`)}
        className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
      >
        <ArrowLeft size={14} />
        Back to Course Study
      </button>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-sm font-semibold text-accent-green">
            {group.course_code}
          </p>
          <h1 className="mt-1 text-2xl font-bold text-text-primary">
            {family.label}
          </h1>
          <p className="mt-2 text-sm text-text-secondary">
            Stats and available mocks for this assessment family.
          </p>
        </div>
        {assessment ? (
          familyExams.length > 0 && !isGenerating ? (
            <Link
              href={`/study/mock-exams/${familyExams[0].id}`}
              className="inline-flex items-center gap-2 rounded-lg border border-accent-green
                bg-[#243111] px-4 py-2 text-sm font-medium text-accent-green transition-colors
                hover:bg-accent-green/20"
            >
              <PlayCircle size={15} />
              See the mock exam
            </Link>
          ) : (
            <button
              type="button"
              disabled={isGenerating}
              onClick={() => void handleGenerateMock()}
              className="inline-flex items-center gap-2 rounded-lg border border-border-primary
                px-4 py-2 text-sm text-text-secondary transition-colors
                hover:border-accent-green hover:bg-[#243111] hover:text-accent-green
                disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isGenerating ? (
                <>
                  <LoaderCircle size={15} className="animate-spin" />
                  Generating mock exam…
                </>
              ) : (
                <>
                  <Brain size={15} />
                  Generate AI Mock
                </>
              )}
            </button>
          )
        ) : null}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Mocks" value={String(family.mocksCount)} />
        <MetricCard
          label="Completed"
          value={String(family.completedAttempts)}
        />
        <MetricCard
          label="Best"
          value={scoreLabel(family.bestScore)}
          tone={scoreTone(family.bestScore)}
        />
        <MetricCard
          label="Latest"
          value={scoreLabel(family.latestScore)}
          tone={scoreTone(family.latestScore)}
        />
        <MetricCard
          label="Predicted"
          value={predicted.letter}
          tone={predicted.textClass}
        />
      </div>

      <div className="space-y-4">
        {familyExams.map((item) => (
          <MockExamCard
            key={item.id}
            courseId={courseId}
            assessmentType={assessment_type}
            assessmentNumber={assessmentNumber}
            item={item}
            onTimerExpire={() => void loadFamilyData(true)}
          />
        ))}
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <GlassCard padding={false} className="space-y-2 p-4">
      <div className="text-xs uppercase tracking-wide text-text-secondary">
        {label}
      </div>
      <p className={`text-lg font-semibold ${tone ?? "text-text-primary"}`}>
        {value}
      </p>
    </GlassCard>
  );
}

function MockExamCard({
  courseId,
  assessmentType,
  assessmentNumber,
  item,
  onTimerExpire,
}: {
  courseId: number;
  assessmentType: string;
  assessmentNumber: number;
  item: MockExamListItem;
  onTimerExpire: () => void;
}) {
  const predicted = predictedGradeBadge(
    item.predicted_grade_letter,
    item.predicted_score_pct,
  );
  const href = `/study/mock-exams/${item.id}?course_id=${courseId}&assessment_type=${assessmentType}&assessment_number=${assessmentNumber}`;

  return (
    <Link href={href} className="block">
      <GlassCard
        padding={false}
        className="p-5 transition-all duration-200 hover:border-accent-green/70 hover:bg-[#243111] hover:shadow-[0_0_0_1px_rgba(163,230,53,0.2)]"
      >
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-text-primary">
              {item.title}
            </span>
            <span className="text-xs text-text-secondary">
              Created {formatDate(item.created_at)}
            </span>
            <span className="inline-flex items-center gap-1 text-xs font-medium text-accent-green">
              <PlayCircle size={13} />
              {primaryAction(item)}
            </span>
          </div>

          <p className="text-sm text-text-secondary">
            {item.question_count} questions
            {item.time_limit_minutes ? ` · ${item.time_limit_minutes} min` : " · Flexible"}
          </p>

          <div className="flex flex-wrap gap-2">
            {item.sources.map((source) => (
              <span
                key={source.source}
                className="rounded-full bg-accent-blue/10 px-3 py-1 text-xs text-accent-blue"
              >
                {source.label}
              </span>
            ))}
          </div>

          <div className="flex flex-wrap gap-2 text-xs">
            <StatChip
              label={`Best ${scoreLabel(item.best_score_pct)}`}
              tone={scoreTone(item.best_score_pct)}
            />
            <StatChip
              label={`Latest ${scoreLabel(item.latest_score_pct)}`}
              tone={scoreTone(item.latest_score_pct)}
            />
            <StatChip
              label={`Predicted ${predicted.letter}`}
              tone={predicted.textClass}
            />
            <StatChip
              label={item.has_active_attempt ? "Uncompleted" : `${item.completed_attempts} completed`}
              tone={item.has_active_attempt ? "text-accent-orange" : "text-text-secondary"}
            />
          </div>

          {item.active_attempt ? (
            <MockExamCountdown
              expiresAt={item.active_attempt.expires_at}
              label="Active timer"
              onExpire={onTimerExpire}
              className="rounded-full border border-accent-orange/30 bg-accent-orange/10 px-3 py-2 text-xs font-semibold text-accent-orange"
            />
          ) : null}
        </div>
      </GlassCard>
    </Link>
  );
}

function StatChip({
  label,
  tone,
}: {
  label: string;
  tone: string;
}) {
  return (
    <span className={`rounded-full bg-white/[0.05] px-3 py-1 ${tone}`}>
      {label}
    </span>
  );
}
