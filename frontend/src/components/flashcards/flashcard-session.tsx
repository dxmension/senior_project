"use client";

import { useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { FlashcardCard } from "./flashcard-card";
import { DifficultyButtons } from "./difficulty-buttons";
import { ProgressBar } from "./progress-bar";
import type { Difficulty, Flashcard } from "./flashcard-data";

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

interface FlashcardSessionProps {
  cards: Flashcard[];
  title?: string;
  onBack?: () => void;
}

export function FlashcardSession({ cards: initialCards, title, onBack }: FlashcardSessionProps) {
  const totalOriginal = initialCards.length;
  const [deck, setDeck] = useState(() => shuffle(initialCards));
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [ratings, setRatings] = useState<Record<number, Difficulty>>({});
  const [sessionComplete, setSessionComplete] = useState(false);
  const [lastNavigationTime, setLastNavigationTime] = useState(0);

  useEffect(() => {
    setDeck(shuffle(initialCards));
    setCurrentIndex(0);
    setIsFlipped(false);
    setRatings({});
    setSessionComplete(false);
  }, [initialCards]);

  const goTo = useCallback(
    (index: number) => {
      if (index < 0 || index >= deck.length) return;
      setCurrentIndex(index);
      setIsFlipped(false);
    },
    [deck.length],
  );

  const rate = useCallback(
    (rating: Difficulty) => {
      if (!isFlipped) return;
      const card = deck[currentIndex];
      setRatings((prev) => (prev[card.id] ? prev : { ...prev, [card.id]: rating }));

      if (rating === "okay" || rating === "hard") {
        setDeck((prev) => [...prev, card]);
      }

      if (currentIndex < deck.length - 1) {
        goTo(currentIndex + 1);
      } else if (rating === "okay" || rating === "hard") {
        setCurrentIndex(currentIndex + 1);
        setIsFlipped(false);
      } else {
        setSessionComplete(true);
      }
    },
    [isFlipped, currentIndex, deck, goTo],
  );

  const restart = () => {
    setDeck(shuffle(initialCards));
    setCurrentIndex(0);
    setIsFlipped(false);
    setRatings({});
    setSessionComplete(false);
  };

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (sessionComplete) return;

      const now = Date.now();
      const NAVIGATION_DELAY = 200;

      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        if (now - lastNavigationTime < NAVIGATION_DELAY) return;

        const newIndex = e.key === "ArrowLeft" ? currentIndex - 1 : currentIndex + 1;
        goTo(newIndex);
        setLastNavigationTime(now);
      }

      if (e.key === " ") {
        e.preventDefault();
        setIsFlipped((f) => !f);
      }
      if (e.key === "1") rate("easy");
      if (e.key === "2") rate("okay");
      if (e.key === "3") rate("hard");
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [currentIndex, sessionComplete, goTo, rate, lastNavigationTime]);

  if (sessionComplete) {
    const easyCount = Object.values(ratings).filter((r) => r === "easy").length;
    const easyPct = Math.round((easyCount / totalOriginal) * 100);

    return (
      <div className="space-y-6">
        <GlassCard className="flex flex-col items-center py-12">
          <h2 className="text-xl font-semibold text-text-primary">
            Session Complete
          </h2>
          <p className="mt-2 text-sm text-text-secondary">
            You reviewed {totalOriginal} cards
          </p>
          <div className="mt-6 flex flex-col items-center gap-3">
            <span className="text-3xl font-bold text-accent-green">
              {easyPct}%
            </span>
            <p className="text-sm text-text-secondary">
              {easyCount} of {totalOriginal} cards were learned
            </p>
          </div>
          <div className="mt-8 flex gap-3">
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                className="inline-flex items-center gap-2 rounded-lg bg-white/[0.06] px-5 py-2.5 text-sm font-medium text-text-secondary transition-transform hover:bg-white/[0.1] active:scale-95"
              >
                Pick another exam
              </button>
            )}
            <button
              type="button"
              onClick={restart}
              className="inline-flex items-center gap-2 rounded-lg bg-accent-green/10 px-5 py-2.5 text-sm font-medium text-accent-green transition-transform hover:bg-accent-green/20 active:scale-95"
            >
              <RotateCcw size={16} />
              Restart
            </button>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          {title && (
            <p className="text-sm text-text-secondary">{title}</p>
          )}
        </div>
        <span className="rounded-full bg-white/[0.06] px-3 py-1 text-xs text-text-muted">
          {deck.length} cards
        </span>
      </div>

      <ProgressBar current={currentIndex} total={deck.length} />

      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={() => goTo(currentIndex - 1)}
          disabled={currentIndex === 0}
          className="rounded-full p-2 text-text-muted transition-colors hover:bg-white/[0.06] hover:text-text-primary disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <ChevronLeft size={24} />
        </button>

        <div className="flex-1">
          <FlashcardCard
            card={deck[currentIndex]}
            isFlipped={isFlipped}
            onFlip={() => setIsFlipped((f) => !f)}
          />
        </div>

        <button
          type="button"
          onClick={() => goTo(currentIndex + 1)}
          disabled={currentIndex === deck.length - 1}
          className="rounded-full p-2 text-text-muted transition-colors hover:bg-white/[0.06] hover:text-text-primary disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <ChevronRight size={24} />
        </button>
      </div>

      <DifficultyButtons visible={isFlipped} onRate={rate} />

      <p className="text-center text-xs text-text-muted">
        ← → navigate cards · 1 2 3 number buttons to rate difficulty
      </p>
    </div>
  );
}
