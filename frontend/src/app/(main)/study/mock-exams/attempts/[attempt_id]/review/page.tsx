"use client";

import { use, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, CheckCircle2, CircleAlert, RotateCcw, XCircle } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  MockExamAttemptReview,
  MockExamQuestionItem,
  MockExamReviewQuestion,
} from "@/types";

type PageParams = Promise<{ attempt_id: string }>;
const QUESTIONS_PER_PAGE = 5;

function answerOptions(question: MockExamQuestionItem) {
  return [1, 2, 3, 4, 5, 6]
    .map((index) => ({
      index,
      value: question[`answer_variant_${index}` as keyof MockExamQuestionItem],
    }))
    .filter((item) => typeof item.value === "string");
}

function sourceBadge(question: MockExamQuestionItem) {
  if (!question.historical_course_offering_label) {
    return question.source_label;
  }
  return `${question.source_label} · ${question.historical_course_offering_label}`;
}

function scoreLabel(score: number | null) {
  return score == null ? "—" : `${score}%`;
}

function optionClasses(item: MockExamReviewQuestion, optionIndex: number) {
  const selected = item.selected_option_index === optionIndex;
  const correct = item.question.correct_option_index === optionIndex;
  const skipped = item.selected_option_index == null;

  if (selected && correct) {
    return "border-accent-green/60 bg-accent-green/10";
  }
  if (selected) {
    return "border-accent-red/60 bg-accent-red/10";
  }
  if (skipped && correct) {
    return "border-yellow-400/50 bg-yellow-500/10";
  }
  if (correct) {
    return "border-accent-green/40 bg-accent-green/5";
  }
  return "border-border-primary bg-white/[0.03]";
}

function optionHelper(item: MockExamReviewQuestion, optionIndex: number) {
  const selected = item.selected_option_index === optionIndex;
  const correct = item.question.correct_option_index === optionIndex;

  if (selected && correct) return "Your answer · Correct";
  if (selected) return "Your answer";
  if (correct) return "Correct answer";
  return null;
}

function questionState(item: MockExamReviewQuestion) {
  if (item.selected_option_index == null) return "Skipped";
  return item.is_correct ? "Correct" : "Incorrect";
}

export default function MockExamReviewPage({ params }: { params: PageParams }) {
  const { attempt_id } = use(params);
  const router = useRouter();
  const attemptId = Number(attempt_id);
  const [review, setReview] = useState<MockExamAttemptReview | null>(null);
  const [questionPage, setQuestionPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await api.get<ApiResponse<MockExamAttemptReview>>(
          `/study/mock-exams/attempts/${attemptId}/review`,
        );
        setReview(response.data);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load attempt review";
        setError(message);
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [attemptId]);

  const summary = useMemo(() => {
    if (!review) return null;
    return {
      correct: review.correct_count,
      incorrect: review.answered_count - review.correct_count,
      skipped: review.question_count - review.answered_count,
    };
  }, [review]);
  const totalQuestionPages = Math.max(
    1,
    Math.ceil((review?.review_questions.length ?? 0) / QUESTIONS_PER_PAGE),
  );
  const paginatedQuestions = useMemo(() => {
    if (!review) return [];
    const start = (questionPage - 1) * QUESTIONS_PER_PAGE;
    return review.review_questions.slice(start, start + QUESTIONS_PER_PAGE);
  }, [questionPage, review]);

  useEffect(() => {
    setQuestionPage(1);
  }, [attemptId]);

  useEffect(() => {
    setQuestionPage((page) => Math.min(page, totalQuestionPages));
  }, [totalQuestionPages]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading review..." />
      </div>
    );
  }

  if (error || !review || !summary) {
    return (
      <GlassCard className="space-y-3">
        <p className="text-sm text-accent-red">{error ?? "Review not found"}</p>
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
        onClick={() => router.push(`/study/mock-exams/${review.mock_exam_id}?view=review`)}
        className="inline-flex items-center gap-1.5 text-sm text-text-secondary"
      >
        <ArrowLeft size={14} />
        Back to Attempt History
      </button>

      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="font-mono text-sm font-semibold text-accent-green">
            {review.course_code}
          </p>
          <h1 className="mt-1 text-2xl font-bold text-text-primary">{review.title}</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Attempt #{review.id} review · scroll through every question and inspect mistakes.
          </p>
        </div>
        <div className="rounded-2xl border border-border-primary bg-white/[0.03] px-4 py-3 text-center">
          <p className="text-xs uppercase tracking-wide text-text-secondary">Score</p>
          <p className="mt-1 text-xl font-semibold text-text-primary">
            {scoreLabel(review.score_pct)}
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Correct" value={String(summary.correct)} icon={<CheckCircle2 size={16} />} tone="text-accent-green" />
        <SummaryCard label="Incorrect" value={String(summary.incorrect)} icon={<XCircle size={16} />} tone="text-accent-red" />
        <SummaryCard label="Skipped" value={String(summary.skipped)} icon={<CircleAlert size={16} />} tone="text-accent-orange" />
        <SummaryCard label="Questions" value={String(review.question_count)} icon={<RotateCcw size={16} />} />
      </div>

      <div className="space-y-4">
        {paginatedQuestions.map((item) => (
          <ReviewQuestionCard key={item.id} item={item} />
        ))}
      </div>

      {review.review_questions.length > QUESTIONS_PER_PAGE ? (
        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setQuestionPage((page) => Math.max(page - 1, 1))}
            disabled={questionPage === 1}
            className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
          >
            Back
          </button>
          <p className="min-w-6 text-center text-sm text-text-secondary">
            {questionPage}
          </p>
          <button
            type="button"
            onClick={() =>
              setQuestionPage((page) => Math.min(page + 1, totalQuestionPages))
            }
            disabled={questionPage >= totalQuestionPages}
            className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
          >
            Next
          </button>
        </div>
      ) : null}

      <div className="flex justify-center pt-2">
        <button
          type="button"
          onClick={() => router.push(`/study/mock-exams/${review.mock_exam_id}?view=review`)}
          className="btn-secondary rounded-full px-5 py-3 text-sm"
        >
          Return Back
        </button>
      </div>
    </div>
  );
}

function SummaryCard({
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
    <GlassCard padding={false} className="space-y-2 p-4">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-text-secondary">
        <span className="text-accent-green">{icon}</span>
        {label}
      </div>
      <p className={`text-lg font-semibold ${tone ?? "text-text-primary"}`}>{value}</p>
    </GlassCard>
  );
}

function ReviewQuestionCard({ item }: { item: MockExamReviewQuestion }) {
  return (
    <GlassCard className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-accent-blue/10 px-3 py-1 text-xs font-semibold text-accent-blue">
          {sourceBadge(item.question)}
        </span>
        <span className="rounded-full bg-white/[0.05] px-3 py-1 text-xs text-text-secondary">
          Question {item.position}
        </span>
        <span className="rounded-full bg-white/[0.05] px-3 py-1 text-xs text-text-secondary">
          {item.points} pt
        </span>
        <span className="rounded-full bg-white/[0.05] px-3 py-1 text-xs text-text-secondary">
          {questionState(item)}
        </span>
      </div>

      <div>
        <p className="text-lg font-semibold leading-8 text-text-primary">
          {item.question.question_text}
        </p>
      </div>

      <div className="grid gap-3">
        {answerOptions(item.question).map((option) => {
          const helper = optionHelper(item, option.index);
          return (
            <div
              key={option.index}
              className={`rounded-2xl border px-4 py-3 ${optionClasses(item, option.index)}`}
            >
              <p className="text-sm text-text-primary">
                {option.index}. {option.value as string}
              </p>
              {helper ? (
                <p className="mt-2 text-xs font-medium text-text-secondary">{helper}</p>
              ) : null}
            </div>
          );
        })}
      </div>

      {item.question.explanation ? (
        <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4">
          <p className="text-xs uppercase tracking-wide text-text-secondary">Explanation</p>
          <p className="mt-2 text-sm text-text-secondary">{item.question.explanation}</p>
        </div>
      ) : null}
    </GlassCard>
  );
}
