"use client";

import { use, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ChevronLeft, ChevronRight, Send } from "lucide-react";

import { MockExamCountdown } from "@/components/study/mock-exam-countdown";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  MockExamAttemptSession,
  MockExamQuestionStudentItem,
  MockExamQuestionStudentLink,
} from "@/types";

type PageParams = Promise<{ attempt_id: string }>;
const EXPIRED_MESSAGE = "Mock exam time limit has expired";

function answerOptions(question: MockExamQuestionStudentItem) {
  return [1, 2, 3, 4, 5, 6]
    .map((index) => ({
      index,
      value: question[`answer_variant_${index}` as keyof MockExamQuestionStudentItem],
    }))
    .filter((item) => typeof item.value === "string");
}

function sourceBadge(question: MockExamQuestionStudentItem) {
  if (!question.historical_course_offering_label) {
    return question.source_label;
  }
  return `${question.source_label} · ${question.historical_course_offering_label}`;
}

export default function MockExamAttemptPage({ params }: { params: PageParams }) {
  const { attempt_id } = use(params);
  const router = useRouter();
  const attemptId = Number(attempt_id);
  const autoSubmitRef = useRef(false);
  const [attempt, setAttempt] = useState<MockExamAttemptSession | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selected, setSelected] = useState<Record<number, number | null>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadAttempt();
  }, [attemptId]);

  const links = attempt?.questions ?? [];
  const current = links[currentIndex] ?? null;
  const progressLabel = useMemo(() => {
    if (!attempt) return "";
    return `${attempt.answered_count}/${attempt.question_count} answered`;
  }, [attempt]);

  async function loadAttempt(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const response = await api.get<ApiResponse<MockExamAttemptSession>>(
        `/mock-exams/attempts/${attemptId}`,
      );
      const next = response.data;
      setAttempt(next);
      setCurrentIndex(Math.max((next.current_position ?? 1) - 1, 0));
      setSelected(
        Object.fromEntries(
          next.answers.map((item) => [
            item.mock_exam_question_link_id,
            item.selected_option_index,
          ]),
        ),
      );
      return next;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load attempt";
      setError(message);
      return null;
    } finally {
      if (!silent) setLoading(false);
    }
  }

  async function syncExpiredAttempt() {
    const next = await loadAttempt(true);
    if (next?.status === "completed") {
      router.push(`/study/mock-exams/attempts/${attemptId}/review`);
    }
  }

  async function saveAnswer(
    link: MockExamQuestionStudentLink,
    option: number | null,
  ) {
    setSaving(true);
    setError(null);
    try {
      const previous = selected[link.id] ?? null;
      await api.put<ApiResponse>(
        `/mock-exams/attempts/${attemptId}/answers/${link.id}`,
        { selected_option_index: option },
      );
      setSelected((currentSelected) => ({ ...currentSelected, [link.id]: option }));
      setAttempt((currentAttempt) => {
        if (!currentAttempt) return currentAttempt;
        const answeredCount = nextAnsweredCount(
          currentAttempt.answered_count,
          previous,
          option,
        );
        return {
          ...currentAttempt,
          answered_count: answeredCount,
        };
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save answer";
      if (message === EXPIRED_MESSAGE) {
        await syncExpiredAttempt();
        return;
      }
      setError(message);
    } finally {
      setSaving(false);
    }
  }

  function nextAnsweredCount(
    answeredCount: number,
    previous: number | null,
    next: number | null,
  ) {
    if (previous == null && next != null) return answeredCount + 1;
    if (previous != null && next == null) return Math.max(answeredCount - 1, 0);
    return answeredCount;
  }

  async function submitAttempt() {
    setSubmitting(true);
    setError(null);
    try {
      await api.post<ApiResponse>(`/mock-exams/attempts/${attemptId}/submit`);
      router.push(`/study/mock-exams/attempts/${attemptId}/review`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to submit attempt";
      if (message === EXPIRED_MESSAGE || message === "Only active attempts can be changed") {
        router.push(`/study/mock-exams/attempts/${attemptId}/review`);
        return;
      }
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading attempt..." />
      </div>
    );
  }

  if (error || !attempt || !current) {
    return (
      <GlassCard className="space-y-3">
        <p className="text-sm text-accent-red">{error ?? "Attempt not found"}</p>
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

  if (attempt.status !== "in_progress") {
    return (
      <GlassCard className="space-y-3">
        <p className="text-sm text-text-secondary">
          This attempt is already completed. Open the review screen to inspect your answers.
        </p>
        <button
          type="button"
          onClick={() => router.push(`/study/mock-exams/attempts/${attempt.id}/review`)}
          className="btn-secondary rounded-lg px-4 py-2 text-sm"
        >
          Open Review
        </button>
      </GlassCard>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <button
        type="button"
        onClick={() => router.push(`/study/mock-exams/${attempt.mock_exam_id}`)}
        className="inline-flex items-center gap-1.5 text-sm text-text-secondary"
      >
        <ArrowLeft size={14} />
        Back to Mock Exam
      </button>

      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="font-mono text-sm font-semibold text-accent-green">
            {attempt.course_code}
          </p>
          <h1 className="mt-1 text-2xl font-bold text-text-primary">{attempt.title}</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Attempt #{attempt.id} · {progressLabel}
          </p>
        </div>
        <div className="flex flex-col items-start gap-3 lg:items-end">
          <MockExamCountdown
            expiresAt={attempt.expires_at}
            label="Time left"
            onExpire={() => {
              if (autoSubmitRef.current) return;
              autoSubmitRef.current = true;
              void submitAttempt();
            }}
            className="rounded-full border border-accent-orange/30 bg-accent-orange/10 px-4 py-2 text-sm font-semibold text-accent-orange"
          />
          <button
            type="button"
            onClick={() => void submitAttempt()}
            disabled={submitting}
            className="inline-flex items-center justify-center gap-2 rounded-full bg-accent-green px-5 py-3 text-sm font-semibold text-bg-primary disabled:opacity-60"
          >
            <Send size={15} />
            {submitting ? "Submitting..." : "Submit Mock Exam"}
          </button>
        </div>
      </div>

      <GlassCard className="space-y-5 p-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-accent-blue/10 px-3 py-1 text-xs font-semibold text-accent-blue">
            {sourceBadge(current.question)}
          </span>
          <span className="rounded-full bg-white/[0.05] px-3 py-1 text-xs text-text-secondary">
            Question {current.position} of {attempt.question_count}
          </span>
          <span className="rounded-full bg-white/[0.05] px-3 py-1 text-xs text-text-secondary">
            {current.points} pt
          </span>
        </div>

        <div>
          <p className="text-lg font-semibold leading-8 text-text-primary">
            {current.question.question_text}
          </p>
          {attempt.instructions ? (
            <p className="mt-2 text-sm text-text-secondary">{attempt.instructions}</p>
          ) : null}
        </div>

        <div className="grid gap-3">
          {answerOptions(current.question).map((option) => {
            const active = selected[current.id] === option.index;
            return (
              <button
                key={option.index}
                type="button"
                onClick={() => void saveAnswer(current, option.index)}
                disabled={saving || submitting}
                className={`rounded-2xl border px-4 py-3 text-left transition-colors ${
                  active
                    ? "border-accent-green/60 bg-accent-green/8"
                    : "border-border-primary bg-white/[0.03]"
                }`}
              >
                <span className="text-sm text-text-primary">
                  {option.index}. {option.value as string}
                </span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => void saveAnswer(current, null)}
            disabled={saving || submitting || selected[current.id] == null}
            className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
          >
            Mark as Skipped
          </button>
        </div>

        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setCurrentIndex((index) => Math.max(index - 1, 0))}
            disabled={currentIndex === 0}
            className="btn-secondary inline-flex items-center gap-2 px-4 py-2 text-sm disabled:opacity-60"
          >
            <ChevronLeft size={14} />
            Previous
          </button>
          <button
            type="button"
            onClick={() =>
              setCurrentIndex((index) => Math.min(index + 1, links.length - 1))
            }
            disabled={currentIndex >= links.length - 1}
            className="btn-secondary inline-flex items-center gap-2 px-4 py-2 text-sm disabled:opacity-60"
          >
            Next
            <ChevronRight size={14} />
          </button>
        </div>
      </GlassCard>
    </div>
  );
}
