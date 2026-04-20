"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  BookOpen,
  Brain,
  Layers,
  Star,
  TrendingUp,
} from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  FlashcardDeckHistory,
  FlashcardItem,
  FlashcardSessionHistoryItem,
  FlashcardSessionReview,
} from "@/types";

type PageParams = Promise<{ session_id: string }>;

const GRADE_COLORS: Record<string, string> = {
  A: "text-accent-green",
  B: "text-accent-green",
  C: "text-accent-orange",
  D: "text-accent-orange",
  F: "text-accent-red",
};

const GRADE_BG: Record<string, string> = {
  A: "bg-accent-green/10 border-accent-green/30",
  B: "bg-accent-green/10 border-accent-green/30",
  C: "bg-accent-orange/10 border-accent-orange/30",
  D: "bg-accent-orange/10 border-accent-orange/30",
  F: "bg-accent-red/10 border-accent-red/30",
};

function scoreTone(score: number | null) {
  if (score == null) return "text-text-secondary";
  if (score < 60) return "text-accent-red";
  if (score < 80) return "text-accent-orange";
  return "text-accent-green";
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-xl border border-border-primary bg-white/[0.03] px-5 py-4">
      <span className={`text-2xl font-bold ${color ?? "text-text-primary"}`}>
        {value}
      </span>
      <span className="text-xs text-text-muted">{label}</span>
    </div>
  );
}

function StruggleCard({ card, rank }: { card: FlashcardItem; rank: number }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <button
      type="button"
      onClick={() => setExpanded((p) => !p)}
      className="w-full rounded-xl border border-border-primary bg-white/[0.02] px-4 py-3 text-left transition-colors hover:border-border-light"
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent-red/10 text-xs font-semibold text-accent-red">
          {rank}
        </span>
        <div className="min-w-0 flex-1">
          {card.topic && (
            <p className="mb-1 text-xs text-text-muted">{card.topic}</p>
          )}
          <p className="text-sm text-text-primary">{card.question}</p>
          {expanded && (
            <p className="mt-2 text-sm leading-relaxed text-text-secondary">
              {card.answer}
            </p>
          )}
          <p className="mt-1 text-xs text-text-muted">
            {expanded ? "Click to collapse" : "Click to see answer"}
          </p>
        </div>
      </div>
    </button>
  );
}

function SessionHistoryRow({
  item,
  isCurrent,
}: {
  item: FlashcardSessionHistoryItem;
  isCurrent: boolean;
}) {
  const gradeColor = GRADE_COLORS[item.grade_letter] ?? "text-text-primary";
  const gradeBg = GRADE_BG[item.grade_letter] ?? "bg-white/[0.04] border-border-primary";
  const easyPct = item.total_responses > 0 ? (item.easy_count / item.total_responses) * 100 : 0;
  const medPct = item.total_responses > 0 ? (item.medium_count / item.total_responses) * 100 : 0;
  const hardPct = item.total_responses > 0 ? (item.hard_count / item.total_responses) * 100 : 0;

  const date = new Date(item.completed_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const inner = (
    <div
      className={`rounded-xl border px-4 py-3 transition-colors ${
        isCurrent
          ? "border-accent-green/40 bg-accent-green/5"
          : "border-border-primary bg-white/[0.02] hover:border-border-light"
      }`}
    >
      <div className="flex items-center gap-3">
        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-sm font-bold ${gradeBg} ${gradeColor}`}
        >
          {item.grade_letter}
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold ${gradeColor}`}>
              {item.grade_pct}%
            </span>
            <span className="text-xs text-text-muted">{date}</span>
            {isCurrent && (
              <span className="rounded-full bg-accent-green/10 px-2 py-0.5 text-[10px] font-semibold text-accent-green">
                this session
              </span>
            )}
          </div>

          <div className="mt-1.5 flex h-1.5 w-full overflow-hidden rounded-full bg-white/[0.08]">
            <div
              className="h-full bg-accent-green"
              style={{ width: `${easyPct}%` }}
            />
            <div
              className="h-full bg-accent-orange"
              style={{ width: `${medPct}%` }}
            />
            <div
              className="h-full bg-accent-red"
              style={{ width: `${hardPct}%` }}
            />
          </div>

          <div className="mt-1 flex gap-3 text-[10px] text-text-muted">
            <span className="text-accent-green">{item.easy_count} easy</span>
            <span className="text-accent-orange">{item.medium_count} medium</span>
            <span className="text-accent-red">{item.hard_count} hard</span>
          </div>
        </div>
      </div>
    </div>
  );

  if (isCurrent) return inner;
  return (
    <Link href={`/flashcards/sessions/${item.session_id}/review`} className="block">
      {inner}
    </Link>
  );
}

export default function FlashcardReviewPage({
  params,
}: {
  params: PageParams;
}) {
  const { session_id } = use(params);
  const sessionId = Number(session_id);

  const [review, setReview] = useState<FlashcardSessionReview | null>(null);
  const [history, setHistory] = useState<FlashcardDeckHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const reviewRes = await api.get<ApiResponse<FlashcardSessionReview>>(
          `/flashcards/sessions/${sessionId}/review`,
        );
        const rev = reviewRes.data ?? null;
        setReview(rev);

        if (rev) {
          const histRes = await api.get<ApiResponse<FlashcardDeckHistory>>(
            `/flashcards/decks/${rev.deck_id}/history`,
          ).catch(() => null);
          setHistory(histRes?.data ?? null);
        }
      } catch {
        setError("Failed to load review.");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
        <Brain size={36} className="animate-pulse text-accent-green" />
        <p className="text-base font-semibold text-text-primary">
          AI is reviewing your answers...
        </p>
        <p className="text-sm text-text-secondary">
          Generating your personalised study plan
        </p>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 text-center">
        <p className="text-sm text-accent-red">{error ?? "Review not found."}</p>
        <Link
          href="/study"
          className="mt-4 inline-block text-sm text-accent-green hover:underline"
        >
          Back to Study
        </Link>
      </div>
    );
  }

  const gradeColor = GRADE_COLORS[review.grade_letter] ?? "text-text-primary";
  const studyPlanPoints = review.ai_study_plan
    .split(/•\s+/)
    .map((s) => s.trim())
    .filter(Boolean);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="mb-6">
        <button
          type="button"
          onClick={() => window.history.back()}
          className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
        >
          <ArrowLeft size={14} />
          Back
        </button>
      </div>

      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-text-primary">Session Review</h1>
        <p className="mt-1 text-sm text-text-secondary">{review.deck_title}</p>
      </div>

      {/* Score stats */}
      <div className="mb-8 grid grid-cols-4 gap-3">
        <StatCard label="Grade" value={review.grade_letter} color={gradeColor} />
        <StatCard label="Easy" value={review.easy_count} color="text-accent-green" />
        <StatCard label="Medium" value={review.medium_count} color="text-accent-orange" />
        <StatCard label="Hard" value={review.hard_count} color="text-accent-red" />
      </div>

      {/* Progress bar */}
      <GlassCard className="mb-6">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs text-text-muted">Mastery</span>
          <span className="text-xs font-semibold text-text-primary">
            {review.grade_pct}%
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-white/[0.08]">
          <div
            className="h-full rounded-full bg-accent-green transition-all"
            style={{ width: `${review.grade_pct}%` }}
          />
        </div>
        <p className="mt-2 text-xs text-text-muted">
          {review.easy_count} of {review.total_responses} responses were Easy
        </p>
      </GlassCard>

      {/* AI Summary */}
      {review.ai_summary && (
        <GlassCard className="mb-6">
          <div className="mb-3 flex items-center gap-2">
            <Brain size={16} className="text-accent-green" />
            <h2 className="text-sm font-semibold text-text-primary">AI Summary</h2>
          </div>
          <p className="text-sm leading-relaxed text-text-secondary">
            {review.ai_summary}
          </p>
        </GlassCard>
      )}

      {/* Top struggled cards */}
      {review.top_struggled_cards.length > 0 && (
        <div className="mb-6">
          <div className="mb-3 flex items-center gap-2">
            <Star size={16} className="text-accent-red" />
            <h2 className="text-sm font-semibold text-text-primary">
              Top Struggled Cards
            </h2>
          </div>
          <div className="space-y-2">
            {review.top_struggled_cards.map((card, i) => (
              <StruggleCard key={card.id} card={card} rank={i + 1} />
            ))}
          </div>
        </div>
      )}

      {/* Weak topics */}
      {review.ai_weak_topics.length > 0 && (
        <GlassCard className="mb-6">
          <div className="mb-3 flex items-center gap-2">
            <BookOpen size={16} className="text-accent-orange" />
            <h2 className="text-sm font-semibold text-text-primary">Topics to Review</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {review.ai_weak_topics.map((topic) => (
              <span
                key={topic}
                className="rounded-full border border-accent-orange/30 bg-accent-orange/5 px-3 py-1 text-xs text-accent-orange"
              >
                {topic}
              </span>
            ))}
          </div>
        </GlassCard>
      )}

      {/* AI Study Plan */}
      {studyPlanPoints.length > 0 && (
        <GlassCard className="mb-8">
          <div className="mb-3 flex items-center gap-2">
            <TrendingUp size={16} className="text-accent-green" />
            <h2 className="text-sm font-semibold text-text-primary">Study Plan</h2>
          </div>
          <ul className="space-y-2">
            {studyPlanPoints.map((point, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-text-secondary"
              >
                <span className="mt-1 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-accent-green/10 text-[10px] font-bold text-accent-green">
                  {i + 1}
                </span>
                {point}
              </li>
            ))}
          </ul>
        </GlassCard>
      )}

      {/* ── Performance History ── */}
      {history && (
        <>
          <div className="mb-4 border-t border-border-primary pt-8">
            <h2 className="text-lg font-bold text-text-primary">Performance History</h2>
            <p className="mt-1 text-sm text-text-secondary">
              Overall stats and all completed sessions for this deck.
            </p>
          </div>

          {/* Overall stats */}
          <div className="mb-6 grid grid-cols-4 gap-3">
            <StatCard
              label="Sessions"
              value={history.total_completed}
            />
            <StatCard
              label="Average"
              value={history.average_grade_pct != null ? `${history.average_grade_pct}%` : "—"}
              color={scoreTone(history.average_grade_pct)}
            />
            <StatCard
              label="Best"
              value={history.best_grade_pct != null ? `${history.best_grade_pct}%` : "—"}
              color={scoreTone(history.best_grade_pct)}
            />
            <StatCard
              label="Predicted"
              value={history.predicted_grade_letter ?? "—"}
              color={
                history.predicted_grade_letter
                  ? GRADE_COLORS[history.predicted_grade_letter]
                  : "text-text-secondary"
              }
            />
          </div>

          {/* Session history list */}
          {history.sessions.length > 0 && (
            <div className="mb-8 space-y-2">
              {[...history.sessions].reverse().map((item) => (
                <SessionHistoryRow
                  key={item.session_id}
                  item={item}
                  isCurrent={item.session_id === sessionId}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Actions */}
      <div className="flex justify-center gap-3">
        <button
          type="button"
          onClick={() => window.history.go(-2)}
          className="inline-flex items-center gap-2 rounded-lg border border-border-primary px-5 py-2.5 text-sm text-text-secondary transition-colors hover:border-border-light hover:text-text-primary"
        >
          <Layers size={14} />
          Back to Decks
        </button>
        <Link
          href="/flashcards"
          className="inline-flex items-center gap-2 rounded-lg bg-accent-green/10 px-5 py-2.5 text-sm font-semibold text-accent-green transition-colors hover:bg-accent-green/20"
        >
          <Brain size={14} />
          All Flashcard Decks
        </Link>
      </div>
    </div>
  );
}
