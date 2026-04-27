"use client";

import { useRef, useState } from "react";
import { X, BookOpen } from "lucide-react";

import { api } from "@/lib/api";
import type { ApiResponse, MockExamQuestionSource, UserSubmittedQuestion } from "@/types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  courseId: number;
  onSubmitted: (question: UserSubmittedQuestion) => void;
}

export function SubmitQuestionModal({ isOpen, onClose, courseId, onSubmitted }: Props) {
  const backdropRef = useRef<HTMLDivElement>(null);
  const [source, setSource] = useState<"rumored" | "historic">("rumored");
  const [historicSection, setHistoricSection] = useState("");
  const [historicYear, setHistoricYear] = useState("");
  const [questionText, setQuestionText] = useState("");
  const [answers, setAnswers] = useState(["", "", "", "", "", ""]);
  const [correctIndex, setCorrectIndex] = useState(1);
  const [explanation, setExplanation] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setSource("rumored");
    setHistoricSection("");
    setHistoricYear("");
    setQuestionText("");
    setAnswers(["", "", "", "", "", ""]);
    setCorrectIndex(1);
    setExplanation("");
    setError(null);
  }

  function handleClose() {
    reset();
    onClose();
  }

  async function handleSubmit() {
    setError(null);
    setSaving(true);
    try {
      const body: Record<string, unknown> = {
        course_id: courseId,
        source: source as MockExamQuestionSource,
        question_text: questionText,
        answer_variant_1: answers[0],
        answer_variant_2: answers[1],
        answer_variant_3: answers[2] || undefined,
        answer_variant_4: answers[3] || undefined,
        answer_variant_5: answers[4] || undefined,
        answer_variant_6: answers[5] || undefined,
        correct_option_index: correctIndex,
        explanation: explanation || undefined,
      };
      if (source === "historic") {
        if (historicSection) body.historic_section = historicSection;
        if (historicYear) body.historic_year = Number(historicYear);
      }
      const res = await api.post<ApiResponse<UserSubmittedQuestion>>(
        "/mock-exams/questions/submit",
        body,
      );
      onSubmitted(res.data!);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit question");
    } finally {
      setSaving(false);
    }
  }

  if (!isOpen) return null;

  const filledAnswers = answers.filter((a) => a.trim()).length;

  return (
    <div
      ref={backdropRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => { if (e.target === backdropRef.current) handleClose(); }}
    >
      <div className="relative mx-4 flex w-full max-w-xl flex-col rounded-2xl border border-border-primary bg-[rgba(18,18,18,0.98)] shadow-2xl max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border-primary px-6 py-4">
          <div className="flex items-center gap-2">
            <BookOpen size={18} className="text-accent-green" />
            <h2 className="text-base font-semibold text-text-primary">Submit a Question</h2>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="rounded p-1 text-text-secondary hover:bg-white/5 hover:text-text-primary"
          >
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {/* Source */}
          <div className="flex gap-3">
            {(["rumored", "historic"] as const).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setSource(s)}
                className={`flex-1 rounded-lg border py-2 text-sm font-medium capitalize transition-colors ${
                  source === s
                    ? "border-accent-green/50 bg-accent-green/10 text-accent-green"
                    : "border-border-primary bg-white/[0.03] text-text-secondary hover:border-border-light"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Historic fields */}
          {source === "historic" && (
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs text-text-secondary">Section (optional)</label>
                <input
                  type="text"
                  value={historicSection}
                  onChange={(e) => setHistoricSection(e.target.value)}
                  placeholder="e.g. Section A"
                  className="glass-input px-3 py-2 text-sm"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-text-secondary">Year (optional)</label>
                <input
                  type="number"
                  value={historicYear}
                  onChange={(e) => setHistoricYear(e.target.value)}
                  placeholder="e.g. 2023"
                  className="glass-input px-3 py-2 text-sm"
                />
              </div>
            </div>
          )}

          {/* Question text */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary">Question</label>
            <textarea
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              placeholder="Enter the question text..."
              className="glass-input min-h-20 px-3 py-2 text-sm"
            />
          </div>

          {/* Answers */}
          <div className="space-y-2">
            <label className="text-xs text-text-secondary">Answer options (at least 2 required)</label>
            {answers.map((val, i) => (
              <input
                key={i}
                type="text"
                value={val}
                onChange={(e) => {
                  const next = [...answers];
                  next[i] = e.target.value;
                  setAnswers(next);
                }}
                placeholder={`Option ${i + 1}${i >= 2 ? " (optional)" : ""}`}
                className="glass-input w-full px-3 py-2 text-sm"
              />
            ))}
          </div>

          {/* Correct option */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary">Correct option</label>
            <select
              value={correctIndex}
              onChange={(e) => setCorrectIndex(Number(e.target.value))}
              className="glass-input px-3 py-2 text-sm"
            >
              {answers.map((val, i) =>
                val.trim() ? (
                  <option key={i} value={i + 1}>
                    Option {i + 1}: {val.slice(0, 40)}{val.length > 40 ? "…" : ""}
                  </option>
                ) : null,
              )}
            </select>
          </div>

          {/* Explanation */}
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary">Explanation (optional)</label>
            <input
              type="text"
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
              placeholder="Why is this the correct answer?"
              className="glass-input px-3 py-2 text-sm"
            />
          </div>

          {error && (
            <p className="text-xs text-accent-red">{error}</p>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border-primary px-6 py-4">
          <p className="text-xs text-text-muted">
            {filledAnswers} option{filledAnswers !== 1 ? "s" : ""} filled
          </p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleClose}
              className="rounded-lg border border-border-primary px-4 py-2 text-sm text-text-secondary hover:border-border-light hover:text-text-primary"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => void handleSubmit()}
              disabled={saving || !questionText.trim() || filledAnswers < 2}
              className="inline-flex items-center gap-2 rounded-lg bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary disabled:opacity-60"
            >
              {saving ? "Submitting..." : "Submit for Review"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
