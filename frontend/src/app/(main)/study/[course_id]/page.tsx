"use client";

import Link from "next/link";
import { use, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, GitFork, Layers } from "lucide-react";

import { MockExamCountdown } from "@/components/study/mock-exam-countdown";
import { CourseMindmapsPanel } from "@/components/courses/course-mindmaps-panel";
import { FlashcardExamPicker } from "@/components/flashcards/flashcard-exam-picker";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { predictedGradeBadge } from "@/lib/predicted-grade";
import { findStudyGroupByRouteCourseId } from "@/lib/study-course-route";
import { groupMockExamFamilies } from "@/lib/study-mock-families";
import type { ApiResponse, EnrollmentItem, MockExamCourseGroup } from "@/types";

type PageParams = Promise<{ course_id: string }>;
type StudyTab = "mock_exams" | "flashcards" | "mindmaps";

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

  const families = useMemo(
    () => (group ? groupMockExamFamilies(group.exams) : []),
    [group],
  );

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
                key={family.key}
                courseId={courseId}
                family={family}
                onTimerExpire={() => void loadCourseData(true)}
              />
            ))}
          </div>
        )
      ) : activeTab === "flashcards" ? (
        <FlashcardExamPicker exams={group.exams} />
      ) : enrollment ? (
        <CourseMindmapsPanel enrollment={enrollment} />
      ) : (
        <FlashcardExamPicker exams={group.exams} />
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
  family: ReturnType<typeof groupMockExamFamilies>[number];
  onTimerExpire: () => void;
}) {
  const predicted = predictedGradeBadge(
    family.predictedLetter,
    family.predictedScore,
  );
  const bestScore = family.bestScore == null ? "—" : `${family.bestScore}%`;
  const latestScore = family.latestScore == null ? "—" : `${family.latestScore}%`;

  return (
    <Link
      href={`/study/${courseId}/${family.assessmentType}/${family.assessmentNumber}`}
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
            <span className="text-xs text-text-secondary">
              Latest {formatDate(family.latestCreatedAt)}
            </span>
          </div>

          <p className="text-sm text-text-secondary">
            {family.mocksCount} mock{family.mocksCount === 1 ? "" : "s"} available
            {" · "}
            {family.hasActiveAttempt ? "Uncompleted active attempt" : `${family.completedAttempts} completed attempt${family.completedAttempts === 1 ? "" : "s"}`}
          </p>

          <div className="flex flex-wrap gap-2 text-xs">
            <StatChip
              label={`Best ${bestScore}`}
              tone={scoreTone(family.bestScore)}
            />
            <StatChip
              label={`Latest ${latestScore}`}
              tone={scoreTone(family.latestScore)}
            />
            <StatChip
              label={`Predicted ${predicted.letter}`}
              tone={predicted.textClass}
            />
            <StatChip
              label={family.hasActiveAttempt ? "Active attempt" : "No active attempt"}
              tone={family.hasActiveAttempt ? "text-accent-green" : "text-text-secondary"}
            />
          </div>

          {family.activeAttempt ? (
            <MockExamCountdown
              expiresAt={family.activeAttempt.expires_at}
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
