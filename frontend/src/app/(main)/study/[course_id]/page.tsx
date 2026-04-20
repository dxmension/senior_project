"use client";

import Link from "next/link";
import { use, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Brain, GitFork, Layers, LoaderCircle, PlayCircle, Trash2 } from "lucide-react";

import { MockExamCountdown } from "@/components/study/mock-exam-countdown";
import { CourseMindmapsPanel } from "@/components/courses/course-mindmaps-panel";
import { GenerateFlashcardPopup } from "@/components/study/generate-flashcard-popup";
import { StudyHelperPanel } from "@/components/study/study-helper-panel";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { predictedGradeBadge } from "@/lib/predicted-grade";
import { findStudyGroupByRouteCourseId } from "@/lib/study-course-route";
import { sortMockExamFamilies } from "@/lib/study-mock-families";
import type {
  ApiResponse,
  EnrollmentItem,
  FlashcardDeckListItem,
  FlashcardSession,
  GenerateFlashcardOptions,
  MockExamCourseGroup,
  MockExamFamily,
} from "@/types";

type PageParams = Promise<{ course_id: string }>;
type StudyTab = "mock_exams" | "flashcards" | "mindmaps" | "study_helper";

function scoreTone(score: number | null) {
  if (score == null) return "text-text-secondary";
  if (score < 60) return "text-accent-red";
  if (score < 80) return "text-accent-orange";
  return "text-accent-green";
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function StudyCoursePage({ params }: { params: PageParams }) {
  const { course_id } = use(params);
  const router = useRouter();
  const courseId = Number(course_id);
  const [group, setGroup] = useState<MockExamCourseGroup | null>(null);
  const [enrollment, setEnrollment] = useState<EnrollmentItem | null>(null);
  const [activeTab, setActiveTab] = useState<StudyTab>("mock_exams");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadCourseData(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const [studyResponse, enrollmentResponse] = await Promise.all([
        api.get<ApiResponse<MockExamCourseGroup[]>>("/mock-exams"),
        api.get<ApiResponse<EnrollmentItem[]>>("/enrollments?status=in_progress"),
      ]);
      const enrollments = enrollmentResponse.data ?? [];
      const next = findStudyGroupByRouteCourseId(
        studyResponse.data ?? [],
        enrollments,
        courseId,
      );
      if (!next) {
        throw new Error("Study course not found");
      }
      setGroup(next);
      const foundEnrollment = enrollments.find((e) => e.course_id === courseId) ?? null;
      setEnrollment(foundEnrollment);
    } catch (err) {
      const message = err instanceof Error
        ? err.message
        : "Failed to load course study data";
      setError(message);
    } finally {
      if (!silent) setLoading(false);
    }
  }

  useEffect(() => {
    void loadCourseData();
  }, [courseId]);

  const families = useMemo(() => (
    group ? sortMockExamFamilies(group.families) : []
  ), [group]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading course mock exams..." />
      </div>
    );
  }

  if (error || !group) {
    return (
      <GlassCard className="space-y-3">
        <p className="text-sm text-accent-red">
          {error ?? "Study course not found"}
        </p>
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
    <div className="mx-auto max-w-6xl space-y-6">
      <button
        type="button"
        onClick={() => router.push("/study")}
        className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary"
      >
        <ArrowLeft size={14} />
        Back to Study
      </button>

      <div>
        <p className="font-mono text-sm font-semibold text-accent-green">
          {group.course_code}
        </p>
        <h1 className="mt-1 text-2xl font-bold text-text-primary">
          {group.course_title}
        </h1>
        <p className="mt-2 text-sm text-text-secondary">
          Choose an assessment family to open its mock exams and family stats.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <TabButton
          active={activeTab === "mock_exams"}
          label="Mock Exams"
          onClick={() => setActiveTab("mock_exams")}
        />
        <TabButton
          active={activeTab === "flashcards"}
          label="Flashcards"
          onClick={() => setActiveTab("flashcards")}
        />
        <TabButton
          active={activeTab === "mindmaps"}
          label="Mindmaps"
          onClick={() => setActiveTab("mindmaps")}
        />
        <TabButton
          active={activeTab === "study_helper"}
          label="Study Helper"
          onClick={() => setActiveTab("study_helper")}
        />
      </div>

      {activeTab === "mock_exams" ? (
        families.length === 0 ? (
          <GlassCard className="py-14 text-center">
            <p className="text-lg font-semibold text-text-primary">
              No mock exams available yet
            </p>
            <p className="mt-2 text-sm text-text-secondary">
              This course is in your study list, but there are no eligible mock exams ready right now.
            </p>
          </GlassCard>
        ) : (
          <div className="space-y-4">
            {families.map((family) => (
              <AssessmentFamilyCard
                key={`${family.assessment_type}:${family.assessment_number}`}
                courseId={courseId}
                family={family}
                onTimerExpire={() => void loadCourseData(true)}
              />
            ))}
          </div>
        )
      ) : activeTab === "flashcards" ? (
        <FlashcardsTabPanel courseId={courseId} />
      ) : activeTab === "mindmaps" ? (
        enrollment ? (
          <CourseMindmapsPanel enrollment={enrollment} />
        ) : (
          <GlassCard className="py-14 text-center">
            <p className="text-sm text-text-secondary">
              Enrollment data not available for mindmaps.
            </p>
          </GlassCard>
        )
      ) : enrollment ? (
        <StudyHelperPanel enrollment={enrollment} />
      ) : (
        <GlassCard className="py-14 text-center">
          <p className="text-sm text-text-secondary">
            Enrollment data not available for Study Helper.
          </p>
        </GlassCard>
      )}
    </div>
  );
}

function TabButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm transition-colors ${
        active
          ? "bg-accent-green text-bg-primary"
          : "border border-border-primary bg-white/[0.03] text-text-secondary hover:border-accent-green/40 hover:text-text-primary"
      }`}
    >
      {label === "Flashcards" ? <Layers size={15} /> : label === "Mindmaps" ? <GitFork size={15} /> : null}
      {label}
    </button>
  );
}

function AssessmentFamilyCard({
  courseId,
  family,
  onTimerExpire,
}: {
  courseId: number;
  family: MockExamFamily;
  onTimerExpire: () => void;
}) {
  const predicted = predictedGradeBadge(
    family.predicted_letter,
    family.predicted_score,
  );
  const bestScore = family.best_score == null ? "—" : `${family.best_score}%`;
  const latestScore = family.latest_score == null ? "—" : `${family.latest_score}%`;
  const hasMocks = family.mocks_count > 0;

  return (
    <Link
      href={`/study/${courseId}/${family.assessment_type}/${family.assessment_number}`}
      className="block"
    >
      <GlassCard
        padding={false}
        className="p-5 transition-all duration-200 hover:border-accent-green/70 hover:bg-[#243111] hover:shadow-[0_0_0_1px_rgba(163,230,53,0.2)]"
      >
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-lg font-semibold text-text-primary">
              {family.label}
            </span>
            {family.latest_created_at ? (
              <span className="text-xs text-text-secondary">
                Latest {formatDate(family.latest_created_at)}
              </span>
            ) : null}
          </div>

          <p className="text-sm text-text-secondary">
            {hasMocks
              ? `${family.mocks_count} mock${family.mocks_count === 1 ? "" : "s"} available · ${
                family.has_active_attempt
                  ? "Uncompleted active attempt"
                  : `${family.completed_attempts} completed attempt${
                    family.completed_attempts === 1 ? "" : "s"
                  }`
              }`
              : "No mocks available yet. Open this family to generate an AI mock."}
          </p>

          <div className="flex flex-wrap gap-2 text-xs">
            <StatChip
              label={`Best ${bestScore}`}
              tone={scoreTone(family.best_score)}
            />
            <StatChip
              label={`Latest ${latestScore}`}
              tone={scoreTone(family.latest_score)}
            />
            <StatChip
              label={`Predicted ${predicted.letter}`}
              tone={predicted.textClass}
            />
            <StatChip
              label={hasMocks ? "Open family" : "Generate AI Mock"}
              tone={hasMocks ? "text-text-secondary" : "text-accent-green"}
            />
          </div>

          {family.active_attempt ? (
            <MockExamCountdown
              expiresAt={family.active_attempt.expires_at}
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

function FlashcardsTabPanel({ courseId }: { courseId: number }) {
  const router = useRouter();
  const [decks, setDecks] = useState<FlashcardDeckListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [starting, setStarting] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [showPopup, setShowPopup] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDecks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ApiResponse<FlashcardDeckListItem[]>>(
        `/flashcards/decks?course_id=${courseId}`,
      );
      setDecks(res.data ?? []);
    } catch {
      setError("Failed to load flashcard decks");
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    void loadDecks();
  }, [loadDecks]);

  async function handleGenerate(opts: GenerateFlashcardOptions) {
    setShowPopup(false);
    setGenerating(true);
    try {
      await api.post("/flashcards/generate", opts);
      await loadDecks();
    } catch {
      setError("Failed to generate flashcard deck");
    } finally {
      setGenerating(false);
    }
  }

  async function handleStart(deckId: number) {
    setStarting(deckId);
    try {
      const res = await api.post<ApiResponse<FlashcardSession>>(
        `/flashcards/decks/${deckId}/sessions`,
        {},
      );
      if (res.data?.id) {
        router.push(`/flashcards/sessions/${res.data.id}`);
      }
    } catch {
      setError("Failed to start flashcard session");
      setStarting(null);
    }
  }

  async function handleDelete(deckId: number) {
    setDeleting(deckId);
    try {
      await api.delete(`/flashcards/decks/${deckId}`);
      setDecks((prev) => prev.filter((d) => d.id !== deckId));
    } catch {
      setError("Failed to delete deck");
    } finally {
      setDeleting(null);
    }
  }

  const difficultyColor = (d: string) => {
    if (d === "easy") return "text-accent-green";
    if (d === "hard") return "text-accent-red";
    return "text-accent-orange";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-secondary">
          Study with AI-generated flashcard decks for this course.
        </p>
        <button
          type="button"
          onClick={() => setShowPopup(true)}
          disabled={generating}
          className="inline-flex items-center gap-2 rounded-full bg-accent-green px-4 py-2 text-sm font-medium text-bg-primary disabled:opacity-60"
        >
          {generating ? (
            <>
              <LoaderCircle size={14} className="animate-spin" />
              Generating…
            </>
          ) : (
            <>
              <Brain size={14} />
              Generate AI Flashcards
            </>
          )}
        </button>
      </div>

      {error && (
        <p className="text-sm text-accent-red">{error}</p>
      )}

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Spinner text="Loading decks…" />
        </div>
      ) : decks.length === 0 ? (
        <GlassCard className="py-14 text-center">
          <Layers size={32} className="mx-auto mb-3 text-text-secondary/40" />
          <p className="text-lg font-semibold text-text-primary">No flashcard decks yet</p>
          <p className="mt-2 text-sm text-text-secondary">
            Generate an AI flashcard deck to start studying.
          </p>
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {decks.map((deck) => (
            <div key={deck.id} className="group relative">
              <button
                type="button"
                onClick={() => handleStart(deck.id)}
                disabled={starting === deck.id}
                className="block w-full text-left"
              >
                <GlassCard
                  padding={false}
                  className="p-5 transition-all duration-200 hover:border-accent-green/70 hover:bg-[#243111] hover:shadow-[0_0_0_1px_rgba(163,230,53,0.2)]"
                >
                  <div className="space-y-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-lg font-semibold text-text-primary">
                        {deck.title}
                      </span>
                      <span className={`text-xs font-medium ${difficultyColor(deck.difficulty)}`}>
                        {deck.difficulty}
                      </span>
                    </div>

                    <p className="text-sm text-text-secondary">
                      {deck.card_count} card{deck.card_count === 1 ? "" : "s"}
                      {" · "}
                      {deck.completed_sessions === 0
                        ? "No completed sessions yet"
                        : `${deck.completed_sessions} completed session${deck.completed_sessions === 1 ? "" : "s"}`}
                    </p>

                    <div className="flex flex-wrap gap-2 text-xs">
                      <StatChip
                        label={
                          deck.latest_grade_pct != null
                            ? `Latest ${deck.latest_grade_letter} (${deck.latest_grade_pct}%)`
                            : "Latest —"
                        }
                        tone={scoreTone(deck.latest_grade_pct)}
                      />
                      <StatChip
                        label={
                          deck.average_grade_pct != null
                            ? `Avg ${deck.average_grade_pct}%`
                            : "Avg —"
                        }
                        tone={scoreTone(deck.average_grade_pct)}
                      />
                      <StatChip
                        label={
                          deck.best_grade_pct != null
                            ? `Best ${deck.best_grade_pct}%`
                            : "Best —"
                        }
                        tone={scoreTone(deck.best_grade_pct)}
                      />
                      <StatChip
                        label={starting === deck.id ? "Starting…" : "Study now"}
                        tone={starting === deck.id ? "text-text-secondary" : "text-accent-green"}
                      />
                    </div>
                  </div>
                </GlassCard>
              </button>

              {deck.latest_completed_session_id != null && (
                <Link
                  href={`/flashcards/sessions/${deck.latest_completed_session_id}/review`}
                  onClick={(e) => e.stopPropagation()}
                  className="absolute right-14 top-3.5 rounded-lg px-2.5 py-1.5 text-xs text-text-secondary opacity-0 transition-opacity group-hover:opacity-100 hover:text-accent-green border border-border-primary hover:border-accent-green/40"
                >
                  Last Review
                </Link>
              )}

              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); void handleDelete(deck.id); }}
                disabled={deleting === deck.id}
                className="absolute right-4 top-4 rounded-lg p-1.5 text-text-secondary opacity-0 transition-opacity group-hover:opacity-100 hover:text-accent-red disabled:opacity-40"
                aria-label="Delete deck"
              >
                {deleting === deck.id ? (
                  <LoaderCircle size={15} className="animate-spin" />
                ) : (
                  <Trash2 size={15} />
                )}
              </button>
            </div>
          ))}
        </div>
      )}

      <GenerateFlashcardPopup
        isOpen={showPopup}
        courseId={courseId}
        onClose={() => setShowPopup(false)}
        onGenerate={handleGenerate}
      />
    </div>
  );
}
