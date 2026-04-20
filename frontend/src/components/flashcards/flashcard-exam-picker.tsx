"use client";

import { useState } from "react";
import { Layers } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { FlashcardSession } from "./flashcard-session";
import type { Flashcard } from "./flashcard-data";
import type { ApiResponse, MockExamListItem } from "@/types";

interface FlashcardExamPickerProps {
  exams: MockExamListItem[];
}

export function FlashcardExamPicker({ exams }: FlashcardExamPickerProps) {
  const [selectedExamId, setSelectedExamId] = useState<number | null>(null);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedExam = exams.find((e) => e.id === selectedExamId);

  async function selectExam(examId: number) {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ApiResponse<Flashcard[]>>(
        `/flashcards/mock-exams/${examId}`,
      );
      setCards(res.data ?? []);
      setSelectedExamId(examId);
    } catch {
      setError("Failed to load flashcards for this exam.");
    } finally {
      setLoading(false);
    }
  }

  function backToPicker() {
    setSelectedExamId(null);
    setCards([]);
  }

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner text="Loading flashcards..." />
      </div>
    );
  }

  if (selectedExamId && cards.length > 0) {
    return (
      <FlashcardSession
        cards={cards}
        title={selectedExam?.title}
        onBack={backToPicker}
      />
    );
  }

  if (exams.length === 0) {
    return (
      <GlassCard className="py-14 text-center">
        <Layers size={32} className="mx-auto mb-3 text-text-muted" />
        <p className="text-lg font-semibold text-text-primary">
          No mock exams available
        </p>
        <p className="mt-2 text-sm text-text-secondary">
          Flashcards are generated from mock exam questions. Add mock exams to
          this course to unlock flashcards.
        </p>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-text-secondary">
        Pick a mock exam to study its questions as flashcards.
      </p>

      {error && <p className="text-sm text-accent-red">{error}</p>}

      <div className="grid gap-3 sm:grid-cols-2">
        {exams.map((exam) => (
          <button
            key={exam.id}
            type="button"
            onClick={() => selectExam(exam.id)}
            className="text-left"
          >
            <GlassCard
              padding={false}
              className="p-5 transition-all duration-200 hover:border-accent-green/40 hover:bg-white/[0.05]"
            >
              <p className="text-sm font-semibold text-text-primary">
                {exam.title}
              </p>
              <p className="mt-1 text-xs text-text-secondary">
                {exam.question_count} questions
              </p>
            </GlassCard>
          </button>
        ))}
      </div>
    </div>
  );
}
