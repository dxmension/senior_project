"use client";

import { use, useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Brain, Check, Minus, X } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type { ApiResponse, FlashcardItem, FlashcardSession } from "@/types";

type PageParams = Promise<{ session_id: string }>;

function FlashcardCardView({
  card,
  isFlipped,
  onFlip,
  position,
  total,
}: {
  card: FlashcardItem;
  isFlipped: boolean;
  onFlip: () => void;
  position: number;
  total: number;
}) {
  return (
    <div className="flex flex-col items-center gap-4">
      <p className="text-xs text-text-muted">
        {position} / {total} remaining
      </p>
      <div
        className="w-full max-w-[600px] cursor-pointer"
        style={{ perspective: 1200 }}
        onClick={onFlip}
      >
        <div
          className="relative min-h-[300px] transition-transform duration-500"
          style={{
            transformStyle: "preserve-3d",
            transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)",
          }}
        >
          <div
            className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl border border-border-primary bg-[#1a1a1a] p-8"
            style={{ backfaceVisibility: "hidden" }}
          >
            {card.topic && (
              <span className="mb-4 rounded-full border border-border-primary px-3 py-0.5 text-xs text-text-muted">
                {card.topic}
              </span>
            )}
            <p className="text-center text-lg font-medium text-text-primary">
              {card.question}
            </p>
            <p className="mt-6 text-xs text-text-muted">
              Click or press Space to reveal answer
            </p>
          </div>
          <div
            className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl border border-border-primary bg-[#1a1a1a] p-8"
            style={{
              backfaceVisibility: "hidden",
              transform: "rotateY(180deg)",
            }}
          >
            {card.topic && (
              <span className="mb-4 rounded-full border border-border-primary px-3 py-0.5 text-xs text-text-muted">
                {card.topic}
              </span>
            )}
            <p className="text-center text-sm leading-relaxed text-text-secondary">
              {card.answer}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FlashcardSessionPage({
  params,
}: {
  params: PageParams;
}) {
  const { session_id } = use(params);
  const router = useRouter();
  const sessionId = Number(session_id);

  const [session, setSession] = useState<FlashcardSession | null>(null);
  const [stack, setStack] = useState<FlashcardItem[]>([]);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const respondingRef = useRef(false);

  useEffect(() => {
    void api
      .get<ApiResponse<FlashcardSession>>(`/flashcards/sessions/${sessionId}`)
      .then((res) => {
        const s = res.data;
        if (!s) return;
        setSession(s);
        // Build initial stack: cards not yet marked easy
        const initialStack = s.cards.filter((c) => {
          const stats = s.card_stats[c.id];
          return !stats || stats.last_response !== "easy";
        });
        setStack(initialStack);
      })
      .catch(() => setError("Failed to load session."))
      .finally(() => setLoading(false));
  }, [sessionId]);

  const handleComplete = useCallback(async () => {
    setCompleting(true);
    try {
      await api.post(`/flashcards/sessions/${sessionId}/complete`);
      router.push(`/flashcards/sessions/${sessionId}/review`);
    } catch {
      setError("Failed to complete session.");
      setCompleting(false);
    }
  }, [sessionId, router]);

  const respond = useCallback(
    async (response: "easy" | "medium" | "hard") => {
      if (!isFlipped || stack.length === 0 || respondingRef.current) return;
      respondingRef.current = true;

      const card = stack[0];

      // Optimistic UI update
      if (response === "easy") {
        setStack((prev) => prev.slice(1));
      } else {
        setStack((prev) => [...prev.slice(1), prev[0]]);
      }
      setIsFlipped(false);

      try {
        await api.post(
          `/flashcards/sessions/${sessionId}/cards/${card.id}/respond`,
          { response }
        );
      } catch {
        // Non-fatal: response still recorded locally
      } finally {
        respondingRef.current = false;
      }
    },
    [isFlipped, stack, sessionId]
  );

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (completing || stack.length === 0) return;
      if (e.key === " ") {
        e.preventDefault();
        setIsFlipped((f) => !f);
      }
      if (e.key === "1") void respond("easy");
      if (e.key === "2") void respond("medium");
      if (e.key === "3") void respond("hard");
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [completing, stack.length, respond]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner text="Loading flashcards..." />
      </div>
    );
  }

  if (completing) {
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

  if (error || !session) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 text-center">
        <p className="text-sm text-accent-red">{error ?? "Session not found."}</p>
        <Link
          href="/study"
          className="mt-4 inline-block text-sm text-accent-green hover:underline"
        >
          Back to Study
        </Link>
      </div>
    );
  }

  // Stack done
  if (stack.length === 0) {
    return (
      <div className="mx-auto max-w-xl px-4 py-8">
        <GlassCard className="flex flex-col items-center py-14">
          <Check size={40} className="mb-4 text-accent-green" />
          <h2 className="text-xl font-semibold text-text-primary">
            All cards reviewed!
          </h2>
          <p className="mt-2 text-sm text-text-secondary">
            You worked through all{" "}
            {session.cards.length} flashcard
            {session.cards.length !== 1 ? "s" : ""}.
          </p>
          <button
            type="button"
            onClick={() => void handleComplete()}
            className="mt-8 inline-flex items-center gap-2 rounded-lg bg-accent-green px-6 py-3 text-sm font-semibold text-bg-primary transition-opacity hover:opacity-90"
          >
            <Brain size={16} />
            See AI Review
          </button>
        </GlassCard>
      </div>
    );
  }

  const current = stack[0];

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <button
          type="button"
          onClick={() => router.back()}
          className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
        >
          <ArrowLeft size={14} />
          Exit
        </button>
        <p className="text-sm font-medium text-text-primary">{session.deck_title}</p>
        <span className="rounded-full bg-white/[0.06] px-3 py-1 text-xs text-text-muted">
          {stack.length} left
        </span>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-accent-red/30 bg-accent-red/5 px-4 py-3 text-sm text-accent-red">
          {error}
        </div>
      )}

      {/* Card */}
      <FlashcardCardView
        card={current}
        isFlipped={isFlipped}
        onFlip={() => setIsFlipped((f) => !f)}
        position={session.cards.length - stack.length + 1}
        total={session.cards.length}
      />

      {/* Difficulty buttons */}
      <div
        className={`mt-8 flex items-center justify-center gap-3 transition-opacity duration-300 ${
          isFlipped ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      >
        <button
          type="button"
          onClick={() => void respond("easy")}
          className="inline-flex items-center gap-2 rounded-lg bg-accent-green/10 px-6 py-3 text-sm font-semibold text-accent-green transition-transform active:scale-95 hover:bg-accent-green/20"
        >
          <Check size={16} />
          Easy
        </button>
        <button
          type="button"
          onClick={() => void respond("medium")}
          className="inline-flex items-center gap-2 rounded-lg bg-accent-orange/10 px-6 py-3 text-sm font-semibold text-accent-orange transition-transform active:scale-95 hover:bg-accent-orange/20"
        >
          <Minus size={16} />
          Medium
        </button>
        <button
          type="button"
          onClick={() => void respond("hard")}
          className="inline-flex items-center gap-2 rounded-lg bg-accent-red/10 px-6 py-3 text-sm font-semibold text-accent-red transition-transform active:scale-95 hover:bg-accent-red/20"
        >
          <X size={16} />
          Hard
        </button>
      </div>

      <p className="mt-4 text-center text-xs text-text-muted">
        Space to flip · 1 Easy · 2 Medium · 3 Hard
      </p>
    </div>
  );
}
