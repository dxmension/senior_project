"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Brain,
  Layers,
  LoaderCircle,
  PlayCircle,
  Trash2,
} from "lucide-react";

import { GenerateFlashcardPopup } from "@/components/study/generate-flashcard-popup";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  EnrollmentItem,
  FlashcardDeck,
  FlashcardDeckListItem,
  FlashcardSession,
  GenerateFlashcardOptions,
} from "@/types";

type PageParams = Promise<{ course_id: string }>;

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "text-accent-green bg-accent-green/10",
  medium: "text-accent-orange bg-accent-orange/10",
  hard: "text-accent-red bg-accent-red/10",
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function FlashcardCoursePage({ params }: { params: PageParams }) {
  const { course_id } = use(params);
  const router = useRouter();
  const courseId = Number(course_id);

  const [decks, setDecks] = useState<FlashcardDeckListItem[]>([]);
  const [enrollment, setEnrollment] = useState<EnrollmentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [startingDeckId, setStartingDeckId] = useState<number | null>(null);

  async function loadDecks(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const [decksRes, enrollRes] = await Promise.all([
        api.get<ApiResponse<FlashcardDeckListItem[]>>(
          `/flashcards/decks?course_id=${courseId}`
        ),
        api.get<ApiResponse<EnrollmentItem[]>>("/enrollments?status=in_progress"),
      ]);
      setDecks(decksRes.data ?? []);
      const found = (enrollRes.data ?? []).find((e) => e.course_id === courseId);
      setEnrollment(found ?? null);
    } catch {
      setError("Failed to load flashcard decks.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDecks();
  }, [courseId]);

  async function handleGenerate(opts: GenerateFlashcardOptions) {
    setIsPopupOpen(false);
    setIsGenerating(true);
    setError(null);
    try {
      await api.post<ApiResponse<FlashcardDeck>>("/flashcards/generate", opts);
      await loadDecks(true);
    } catch {
      setError("Failed to generate flashcards. Make sure you have course materials uploaded.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleStartSession(deckId: number) {
    setStartingDeckId(deckId);
    try {
      const res = await api.post<ApiResponse<FlashcardSession>>(
        `/flashcards/decks/${deckId}/sessions`
      );
      if (res.data) {
        router.push(`/flashcards/sessions/${res.data.id}`);
      }
    } catch {
      setError("Failed to start session.");
      setStartingDeckId(null);
    }
  }

  async function handleDeleteDeck(deckId: number) {
    try {
      await api.delete(`/flashcards/decks/${deckId}`);
      setDecks((prev) => prev.filter((d) => d.id !== deckId));
    } catch {
      setError("Failed to delete deck.");
    }
  }

  const courseLabel = enrollment
    ? `${enrollment.course_code} - ${enrollment.course_title}`
    : `Course ${courseId}`;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Back nav */}
      <div className="mb-6">
        <Link
          href={`/study/${courseId}`}
          className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
        >
          <ArrowLeft size={14} />
          Back to Study
        </Link>
      </div>

      {/* Header */}
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-text-primary flex items-center gap-2">
            <Layers size={20} className="text-accent-green" />
            Flashcards
          </h1>
          <p className="mt-1 text-sm text-text-secondary">{courseLabel}</p>
        </div>
        <button
          type="button"
          onClick={() => setIsPopupOpen(true)}
          disabled={isGenerating}
          className="inline-flex items-center gap-2 rounded-lg bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {isGenerating ? (
            <LoaderCircle size={14} className="animate-spin" />
          ) : (
            <Brain size={14} />
          )}
          {isGenerating ? "Generating..." : "Generate AI Flashcards"}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-accent-red/30 bg-accent-red/5 px-4 py-3 text-sm text-accent-red">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner text="Loading decks..." />
        </div>
      ) : decks.length === 0 ? (
        <GlassCard className="py-16 text-center">
          <Layers size={32} className="mx-auto mb-3 text-text-muted" />
          <p className="text-lg font-semibold text-text-primary">No flashcard decks yet</p>
          <p className="mt-2 text-sm text-text-secondary">
            Generate AI flashcards from your course materials to get started.
          </p>
          <button
            type="button"
            onClick={() => setIsPopupOpen(true)}
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-accent-green px-5 py-2.5 text-sm font-semibold text-bg-primary transition-opacity hover:opacity-90"
          >
            <Brain size={14} />
            Generate AI Flashcards
          </button>
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {decks.map((deck) => (
            <GlassCard
              key={deck.id}
              padding={false}
              className="flex items-center justify-between gap-4 px-5 py-4"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-text-primary">{deck.title}</p>
                <div className="mt-1 flex items-center gap-3 text-xs text-text-muted">
                  <span>{deck.card_count} cards</span>
                  <span
                    className={`rounded-full px-2 py-0.5 font-medium capitalize ${
                      DIFFICULTY_COLORS[deck.difficulty] ?? "text-text-secondary"
                    }`}
                  >
                    {deck.difficulty}
                  </span>
                  <span>{formatDate(deck.created_at)}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  type="button"
                  onClick={() => handleDeleteDeck(deck.id)}
                  className="rounded p-1.5 text-text-muted transition-colors hover:bg-white/5 hover:text-accent-red"
                  title="Delete deck"
                >
                  <Trash2 size={14} />
                </button>
                <button
                  type="button"
                  onClick={() => handleStartSession(deck.id)}
                  disabled={startingDeckId === deck.id}
                  className="inline-flex items-center gap-2 rounded-lg bg-accent-green/10 px-3 py-1.5 text-sm font-medium text-accent-green transition-colors hover:bg-accent-green/20 disabled:opacity-50"
                >
                  {startingDeckId === deck.id ? (
                    <LoaderCircle size={14} className="animate-spin" />
                  ) : (
                    <PlayCircle size={14} />
                  )}
                  Study
                </button>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      <GenerateFlashcardPopup
        isOpen={isPopupOpen}
        onClose={() => setIsPopupOpen(false)}
        courseId={courseId}
        onGenerate={handleGenerate}
      />
    </div>
  );
}
