"use client";

import Link from "next/link";
import { use, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  BarChart3,
  Brain,
  Clock3,
  PlayCircle,
  Trophy,
} from "lucide-react";

import { MockExamCountdown } from "@/components/study/mock-exam-countdown";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { predictedGradeBadge } from "@/lib/predicted-grade";
import { resolveStudyRouteCourseId } from "@/lib/study-course-route";
import type {
  ApiResponse,
  MockExamAttempt,
  MockExamAttemptSummary,
  MockExamDashboard,
  MockExamTrendPoint,
  EnrollmentItem,
} from "@/types";

type PageParams = Promise<{ mock_exam_id: string }>;
const ATTEMPTS_PER_PAGE = 5;

function scoreTone(score: number | null) {
  if (score == null) return "text-text-secondary";
  if (score < 60) return "text-accent-red";
  if (score < 80) return "text-accent-orange";
  return "text-accent-green";
}

function valueLabel(value: number | null) {
  return value == null ? "—" : `${value}%`;
}

function formatDate(iso: string | null) {
  if (!iso) return "Not submitted";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function primaryLabel(data: MockExamDashboard) {
  return data.active_attempt ? "Resume Mock Exam" : "Start New Attempt";
}

function primaryIcon(data: MockExamDashboard) {
  return data.active_attempt ? <PlayCircle size={16} /> : <Brain size={16} />;
}

export default function MockExamDetailPage({ params }: { params: PageParams }) {
  const { mock_exam_id } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const reviewMode = searchParams.get("view") === "review";
  const familyCourseId = searchParams.get("course_id");
  const familyAssessmentType = searchParams.get("assessment_type");
  const familyAssessmentNumber = searchParams.get("assessment_number");
  const mockExamId = Number(mock_exam_id);
  const [data, setData] = useState<MockExamDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attemptMessage, setAttemptMessage] = useState<string | null>(null);
  const [attemptPage, setAttemptPage] = useState(1);
  const [starting, setStarting] = useState(false);
  const [studyCourseId, setStudyCourseId] = useState<number | null>(null);
  const predicted = predictedGradeBadge(
    data?.predicted_grade_letter ?? null,
    data?.predicted_score_pct ?? null,
  );

  async function loadDashboard(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    setStudyCourseId(null);
    try {
      const [dashboardResponse, enrollmentResponse] = await Promise.all([
        api.get<ApiResponse<MockExamDashboard>>(`/mock-exams/${mockExamId}`),
        api.get<ApiResponse<EnrollmentItem[]>>("/enrollments?status=in_progress"),
      ]);
      setData(dashboardResponse.data);
      setStudyCourseId(
        resolveStudyRouteCourseId(
          enrollmentResponse.data ?? [],
          dashboardResponse.data.course_id,
        ),
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load mock exam";
      setError(message);
    } finally {
      if (!silent) setLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, [mockExamId]);

  const totalAttemptPages = Math.max(
    1,
    Math.ceil((data?.attempts.length ?? 0) / ATTEMPTS_PER_PAGE),
  );
  const paginatedAttempts = useMemo(() => {
    if (!data) return [];
    const start = (attemptPage - 1) * ATTEMPTS_PER_PAGE;
    return data.attempts.slice(start, start + ATTEMPTS_PER_PAGE);
  }, [attemptPage, data]);

  useEffect(() => {
    setAttemptPage(1);
  }, [mockExamId]);

  useEffect(() => {
    setAttemptPage((page) => Math.min(page, totalAttemptPages));
  }, [totalAttemptPages]);

  async function handleStart() {
    setStarting(true);
    setAttemptMessage(null);
    try {
      const response = await api.post<ApiResponse<MockExamAttempt>>(
        `/mock-exams/${mockExamId}/attempts`,
      );
      router.push(`/study/mock-exams/attempts/${response.data.id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Could not prepare the attempt.";
      setAttemptMessage(message);
    } finally {
      setStarting(false);
    }
  }

  const familyBackPath = (
    familyCourseId &&
    familyAssessmentType &&
    familyAssessmentNumber
  )
    ? `/study/${familyCourseId}/${familyAssessmentType}/${familyAssessmentNumber}`
    : null;

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading mock exam..." />
      </div>
    );
  }

  if (error || !data) {
    return (
      <GlassCard className="space-y-3">
        <p className="text-sm text-accent-red">{error ?? "Mock exam not found"}</p>
        <button
          type="button"
          onClick={() => router.push("/study")}
          className="btn-secondary rounded-lg px-4 py-2 text-sm"
        >
          Back to Study
        </button>
      </GlassCard>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <button
        type="button"
        onClick={() =>
          router.push(familyBackPath ?? `/study/${studyCourseId ?? data.course_id}`)
        }
        className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
      >
        <ArrowLeft size={14} />
        {familyBackPath ? "Back to Assessment Mocks" : "Back to Course Mock Exams"}
      </button>

      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-sm font-semibold text-accent-green">
              {data.course_code}
            </span>
            <span className="rounded-full bg-white/[0.05] px-2.5 py-1 text-[11px] uppercase tracking-wide text-text-secondary">
              {data.assessment_type}
            </span>
          </div>
          <h1 className="mt-2 text-2xl font-bold text-text-primary">{data.title}</h1>
          <p className="mt-1 text-sm text-text-secondary">{data.course_title}</p>
          {data.instructions ? (
            <p className="mt-3 max-w-2xl text-sm text-text-secondary">
              {data.instructions}
            </p>
          ) : null}
          <div className="mt-4 flex flex-wrap gap-2">
            {data.sources.map((source) => (
              <span
                key={source.source}
                className="rounded-full bg-accent-blue/10 px-3 py-1 text-xs text-accent-blue"
              >
                {source.label}
              </span>
            ))}
          </div>
        </div>

        <GlassCard className="min-w-[280px] p-5">
          <div className="space-y-3 text-center">
            <p className="text-sm font-semibold text-text-primary">Mock Exam Entry</p>
            <p className="text-sm text-text-secondary">
              {data.active_attempt
                ? "You have an active saved attempt ready to resume."
                : "Start a new saved attempt. Review stays available after submission."}
            </p>
            {data.active_attempt ? (
              <MockExamCountdown
                expiresAt={data.active_attempt.expires_at}
                label="Time left"
                onExpire={() => void loadDashboard(true)}
                className="justify-center rounded-full border border-accent-orange/30 bg-accent-orange/10 px-3 py-2 text-xs font-semibold text-accent-orange"
              />
            ) : null}
            <button
              type="button"
              onClick={() => void handleStart()}
              disabled={starting}
              className="inline-flex w-full items-center justify-center gap-2
                rounded-full bg-accent-green px-4 py-3 text-sm
                font-semibold text-bg-primary disabled:opacity-60"
            >
              {primaryIcon(data)}
              {starting ? "Preparing..." : primaryLabel(data)}
            </button>
            {attemptMessage ? (
              <p className="rounded-xl bg-white/[0.04] px-3 py-2 text-xs text-text-secondary">
                {attemptMessage}
              </p>
            ) : null}
          </div>
        </GlassCard>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <MetricCard label="Attempts" value={String(data.attempts_count)} icon={<BarChart3 size={16} />} />
        <MetricCard label="Best" value={valueLabel(data.best_score_pct)} tone={scoreTone(data.best_score_pct)} icon={<Trophy size={16} />} />
        <MetricCard label="Average" value={valueLabel(data.average_score_pct)} tone={scoreTone(data.average_score_pct)} icon={<BarChart3 size={16} />} />
        <MetricCard label="Latest" value={valueLabel(data.latest_score_pct)} tone={scoreTone(data.latest_score_pct)} icon={<Brain size={16} />} />
        <MetricCard label="Predicted" value={predicted.letter} tone={predicted.textClass} icon={<Trophy size={16} />} />
        <MetricCard label="Time Limit" value={data.time_limit_minutes ? `${data.time_limit_minutes} min` : "Flexible"} icon={<Clock3 size={16} />} />
      </div>

      {reviewMode ? (
        <GlassCard className="space-y-2 border-accent-blue/30 bg-accent-blue/5">
          <p className="text-sm font-semibold text-text-primary">Choose an attempt to review</p>
          <p className="text-sm text-text-secondary">
            Review is only available for completed attempts. Open any completed attempt below to inspect your answers.
          </p>
        </GlassCard>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <GlassCard className="space-y-5">
          <div className="flex items-center gap-2">
            <BarChart3 size={18} className="text-accent-green" />
            <h2 className="text-lg font-semibold text-text-primary">Performance Trend</h2>
          </div>
          <TrendChart points={data.trend} />
        </GlassCard>

        <GlassCard className="space-y-4">
          <h2 className="text-lg font-semibold text-text-primary">Attempt History</h2>
          {data.attempts.length === 0 ? (
            <p className="text-sm text-text-secondary">
              No attempts yet. Start this mock exam to create your first saved session.
            </p>
          ) : (
            <div className="space-y-3">
              {paginatedAttempts.map((attempt) => (
                <AttemptCard
                  key={attempt.id}
                  attempt={attempt}
                  mockExamId={data.id}
                  onTimerExpire={() => void loadDashboard(true)}
                />
              ))}
              {data.attempts.length > ATTEMPTS_PER_PAGE ? (
                <div className="flex items-center justify-between gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setAttemptPage((page) => Math.max(page - 1, 1))}
                    disabled={attemptPage === 1}
                    className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
                  >
                    Back
                  </button>
                  <p className="min-w-6 text-center text-sm text-text-secondary">
                    {attemptPage}
                  </p>
                  <button
                    type="button"
                    onClick={() =>
                      setAttemptPage((page) => Math.min(page + 1, totalAttemptPages))
                    }
                    disabled={attemptPage >= totalAttemptPages}
                    className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
                  >
                    Next
                  </button>
                </div>
              ) : null}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon,
  tone,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  tone?: string;
}) {
  return (
    <GlassCard padding={false} className="p-4">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-text-secondary">
        <span className="text-accent-green">{icon}</span>
        {label}
      </div>
      <p className={`mt-3 text-2xl font-bold ${tone ?? "text-text-primary"}`}>{value}</p>
    </GlassCard>
  );
}

function AttemptCard({
  attempt,
  mockExamId,
  onTimerExpire,
}: {
  attempt: MockExamAttemptSummary;
  mockExamId: number;
  onTimerExpire: () => void;
}) {
  const action = attempt.status === "completed" ? "Review Attempt" : "Resume Attempt";
  const href =
    attempt.status === "completed"
      ? `/study/mock-exams/attempts/${attempt.id}/review`
      : `/study/mock-exams/attempts/${attempt.id}`;
  const helper =
    attempt.status === "completed"
      ? "Open review"
      : attempt.status === "in_progress"
        ? "Continue attempt"
        : "View attempt";

  return (
    <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold text-text-primary">Attempt #{attempt.id}</p>
          <p className="mt-1 text-xs text-text-secondary">
            {formatDate(attempt.submitted_at ?? attempt.started_at)}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className={`text-sm font-semibold ${scoreTone(attempt.score_pct)}`}>
              {valueLabel(attempt.score_pct)}
            </p>
            <p className="mt-1 text-xs uppercase tracking-wide text-text-secondary">
              {attempt.status.replace("_", " ")}
            </p>
            {attempt.expires_at ? (
              <MockExamCountdown
                expiresAt={attempt.expires_at}
                label="Time left"
                onExpire={onTimerExpire}
                className="mt-2 justify-end text-xs font-semibold text-accent-orange"
              />
            ) : null}
          </div>
          {attempt.status === "abandoned" ? (
            <Link
              href={`/study/mock-exams/${mockExamId}`}
              className="btn-secondary rounded-full px-4 py-2 text-sm"
            >
              {helper}
            </Link>
          ) : (
            <Link href={href} className="btn-secondary rounded-full px-4 py-2 text-sm">
              {action}
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

function TrendChart({ points }: { points: MockExamTrendPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border-primary p-8 text-center text-sm text-text-secondary">
        Your score trend will appear here after the first completed attempt.
      </div>
    );
  }

  const width = 640;
  const height = 240;
  const left = 40;
  const right = width - 20;
  const top = 20;
  const bottom = height - 36;
  const step = points.length === 1 ? 0 : (right - left) / (points.length - 1);
  const path = points
    .map((point, index) => {
      const x = left + step * index;
      const y = bottom - ((point.best_score_pct / 100) * (bottom - top));
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="min-w-[640px]">
        {[0, 25, 50, 75, 100].map((tick) => {
          const y = bottom - ((tick / 100) * (bottom - top));
          return (
            <g key={tick}>
              <line
                x1={left}
                y1={y}
                x2={right}
                y2={y}
                stroke="rgba(255,255,255,0.08)"
                strokeDasharray="4 4"
              />
              <text x={10} y={y + 4} className="fill-text-secondary text-[11px]">
                {tick}%
              </text>
            </g>
          );
        })}

        <path d={path} fill="none" stroke="#a3e635" strokeWidth={3} />
        {points.map((point, index) => {
          const x = left + step * index;
          const y = bottom - ((point.best_score_pct / 100) * (bottom - top));
          return (
            <g key={`${point.date_label}-${index}`}>
              <circle cx={x} cy={y} r={5} fill="#a3e635" />
              <text x={x} y={height - 12} textAnchor="middle" className="fill-text-secondary text-[11px]">
                {point.date_label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
