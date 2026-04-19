"use client";

import {
  ArrowLeft,
  Brain,
  CheckSquare,
  Edit2,
  Plus,
  Square,
  Trash2,
} from "lucide-react";
import { Fragment, use, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { AddAssessmentModal } from "@/components/courses/add-assessment-modal";
import { CourseMaterialsPanel } from "@/components/courses/course-materials-panel";
import { CourseMindmapsPanel } from "@/components/courses/course-mindmaps-panel";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { predictedGradeBadge } from "@/lib/predicted-grade";
import { useAssessmentsStore } from "@/stores/assessments";
import type {
  ApiResponse,
  Assessment,
  AssessmentType,
  EnrollmentItem,
  MockExamCourseGroup,
  UpdateAssessmentPayload 
} from "@/types";

// ─── Helpers ────────────────────────────────────────────────────────────────

const ASSESSMENT_LABELS: Record<AssessmentType, string> = {
  homework: "Homework",
  quiz: "Quiz",
  midterm: "Midterm",
  final: "Final Exam",
  project: "Project",
  lab: "Lab",
  presentation: "Presentation",
  other: "Other",
};

const BADGE_STYLES: Record<AssessmentType, { bg: string; text: string }> = {
  midterm: { bg: "#3d1515", text: "#f87171" },
  final: { bg: "#3d1515", text: "#f87171" },
  project: { bg: "#1e1535", text: "#c084fc" },
  homework: { bg: "#0f2035", text: "#60a5fa" },
  quiz: { bg: "#2d1a00", text: "#fb923c" },
  lab: { bg: "#0d2620", text: "#34d399" },
  presentation: { bg: "#2a2000", text: "#fbbf24" },
  other: { bg: "#1e1e1e", text: "#a0a0a0" },
};

function relativeTime(isoString: string): string {
  const diff = new Date(isoString).getTime() - Date.now();
  const days = Math.floor(Math.abs(diff) / 86400000);
  if (diff > 0) return days === 0 ? "today" : `in ${days}d`;
  return days === 0 ? "today" : `${days}d ago`;
}

function formatDeadline(isoString: string): string {
  const d = new Date(isoString);
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  }) + ", " + d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

// Inline score slot — empty state or double-click to re-edit
function ScoreInput({
  initialScore,
  assessment,
  onSaved,
}: {
  initialScore: number | null;
  assessment: Assessment;
  onSaved: (id: number, score: number) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(initialScore != null ? String(initialScore) : "");
  const [focused, setFocused] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { updateAssessment } = useAssessmentsStore();

  function openEdit() {
    setSaveError(null);
    setEditing(true);
    setTimeout(() => { inputRef.current?.focus(); inputRef.current?.select(); }, 20);
  }

  async function submit() {
    const num = parseFloat(value);
    if (isNaN(num) || num < 0) { setEditing(false); return; }
    setSaving(true);
    setSaveError(null);
    const STUDY_TYPES = new Set(["quiz", "midterm", "final", "presentation"]);
    const isStudy = STUDY_TYPES.has(assessment.assessment_type);
    try {
      const patch: UpdateAssessmentPayload = { score: num };
      if (isStudy) patch.is_completed = true;
      await updateAssessment(assessment.id, patch);
      onSaved(assessment.id, num);
      setEditing(false);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "Enter") void submit();
    if (e.key === "Escape") { setValue(initialScore != null ? String(initialScore) : ""); setEditing(false); }
  }

  // Not editing — show filled value or clickable placeholder
  if (!editing) {
    if (initialScore != null) {
      return (
        <div
          onDoubleClick={openEdit}
          title="Double-click to edit"
          style={{ display: "inline-flex", alignItems: "center", gap: 4, cursor: "default", userSelect: "none" }}
        >
          <span style={{
            fontSize: 12, fontWeight: 500, color: "#f5f5f5",
            padding: "2px 6px", borderRadius: 5,
            border: "1px solid rgba(255,255,255,0.07)",
            background: "rgba(255,255,255,0.04)",
          }}>
            {initialScore}
          </span>
          {assessment.max_score != null && (
            <span style={{ fontSize: 11, color: "#555" }}>/ {assessment.max_score}</span>
          )}
        </div>
      );
    }
    return (
      <button
        type="button"
        onClick={openEdit}
        title="Click to enter score"
        style={{
          fontSize: 12, color: "#444", cursor: "pointer",
          padding: "2px 6px", borderRadius: 5,
          border: "1px dashed rgba(255,255,255,0.08)",
          background: "transparent",
        }}
      >
        —
      </button>
    );
  }

  // Editing
  return (
    <>
      <style>{`.score-no-arrows::-webkit-outer-spin-button,.score-no-arrows::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}.score-no-arrows{-moz-appearance:textfield}`}</style>
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-1.5">
          <div
            onClick={() => inputRef.current?.focus()}
            style={{
              display: "inline-flex", alignItems: "center",
              padding: "3px 8px", borderRadius: 6,
              border: focused ? "1px solid rgba(163,230,53,0.5)" : "1px dashed rgba(163,230,53,0.25)",
              background: focused ? "rgba(163,230,53,0.06)" : "rgba(163,230,53,0.03)",
              cursor: "text", transition: "all 0.15s ease",
              boxShadow: focused ? "0 0 0 3px rgba(163,230,53,0.06)" : "none",
            }}
          >
            <input
              ref={inputRef}
              className="score-no-arrows"
              type="number"
              min={0}
              max={assessment.max_score ?? undefined}
              step="any"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => { setFocused(false); void submit(); }}
              onKeyDown={handleKey}
              placeholder="—"
              disabled={saving}
              autoFocus
              style={{
                appearance: "textfield", background: "transparent",
                border: "none", outline: "none",
                width: `${String(assessment.max_score ?? "—").length + 0.5}ch`,
                fontSize: 12, fontWeight: 500,
                color: value ? "#f5f5f5" : "#a3e635",
                textAlign: "center", opacity: saving ? 0.5 : 1,
              }}
            />
          </div>
          {assessment.max_score != null && (
            <span style={{ fontSize: 11, color: "#555", userSelect: "none" }}>/ {assessment.max_score}</span>
          )}
        </div>
        {saveError && (
          <span style={{ fontSize: 10, color: "#f87171" }}>{saveError}</span>
        )}
      </div>
    </>
  );
}

type FilterTab = "all" | "upcoming" | "completed" | "overdue";
type CoursePageTab = "deadlines" | "materials" | "mindmaps";

function findStudyGroup(
  groups: MockExamCourseGroup[],
  catalogCourseId: number | null,
) {
  if (catalogCourseId == null) return null;
  return groups.find((item) => item.course_id === catalogCourseId) ?? null;
}

function findAssessmentPrediction(
  group: MockExamCourseGroup | null,
  assessmentType: AssessmentType,
) {
  if (!group) return null;
  return (
    group.assessment_predictions.find((item) => item.assessment_type === assessmentType)
    ?? null
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

type PageParams = Promise<{ course_id: string }>;

export default function CourseDetailPage({ params }: { params: PageParams }) {
  const { course_id } = use(params);
  const courseId = Number(course_id);
  const router = useRouter();

  const [enrollment, setEnrollment] = useState<EnrollmentItem | null>(null);
  const [enrollmentLoading, setEnrollmentLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const [filter, setFilter] = useState<FilterTab>("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [pageTab, setPageTab] = useState<CoursePageTab>("deadlines");
  const [editingAssessment, setEditingAssessment] =
    useState<Assessment | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [studyGroup, setStudyGroup] = useState<MockExamCourseGroup | null>(null);

  const { byCourse, loadingCourseIds, fetchForCourse, toggleComplete, deleteAssessment } =
    useAssessmentsStore();

  const assessments = byCourse[courseId] ?? [];
  const assessmentsLoading = loadingCourseIds.has(courseId);
  const catalogCourseId = enrollment?.catalog_course_id ?? null;

  // Load enrollment
  useEffect(() => {
    async function load() {
      try {
        const res = await api.get<ApiResponse<EnrollmentItem[]>>(
          "/enrollments?status=in_progress"
        );
        const found = (res.data ?? []).find((e) => e.course_id === courseId);
        if (found) {
          setEnrollment(found);
        } else {
          setNotFound(true);
        }
      } catch {
        setNotFound(true);
      } finally {
        setEnrollmentLoading(false);
      }
    }
    void load();
  }, [courseId]);

  // Load assessments
  useEffect(() => {
    if (!byCourse[courseId]) {
      void fetchForCourse(courseId);
    }
  }, [courseId, byCourse, fetchForCourse]);

  useEffect(() => {
    async function loadStudyGroup() {
      if (catalogCourseId == null) {
        setStudyGroup(null);
        return;
      }
      try {
        const response = await api.get<ApiResponse<MockExamCourseGroup[]>>(
          "/study/mock-exams",
        );
        setStudyGroup(findStudyGroup(response.data ?? [], catalogCourseId));
      } catch {
        setStudyGroup(null);
      }
    }

    void loadStudyGroup();
  }, [catalogCourseId]);

  const now = new Date();

  function filterAssessments(list: Assessment[]): Assessment[] {
    switch (filter) {
      case "upcoming":
        return list.filter(
          (a) => !a.is_completed && new Date(a.deadline) >= now
        );
      case "completed":
        return list.filter((a) => a.is_completed);
      case "overdue":
        return list.filter(
          (a) => !a.is_completed && new Date(a.deadline) < now
        );
      default:
        return list;
    }
  }

  const filtered = filterAssessments(assessments).sort(
    (a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
  );

  const totalCount = assessments.length;
  const upcomingCount = assessments.filter(
    (a) => !a.is_completed && new Date(a.deadline) >= now
  ).length;
  const overdueCount = assessments.filter(
    (a) => !a.is_completed && new Date(a.deadline) < now
  ).length;

  async function handleDelete(id: number) {
    setDeletingId(id);
    try {
      await deleteAssessment(id, courseId);
      setConfirmDeleteId(null);
    } catch {
      // error ignored, store keeps state
    } finally {
      setDeletingId(null);
    }
  }

  // ── Loading / not found states ──────────────────────────────────────────

  if (enrollmentLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading course..." />
      </div>
    );
  }

  if (notFound || !enrollment) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-4 py-20 text-center">
        <p className="text-lg font-semibold text-text-primary">
          Course not found
        </p>
        <p className="text-sm text-text-secondary">
          This course is not in your current enrollments.
        </p>
        <button
          type="button"
          onClick={() => router.back()}
          className="btn-secondary inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm"
        >
          <ArrowLeft size={14} />
          Back to Courses
        </button>
      </div>
    );
  }

  // ── Main layout ─────────────────────────────────────────────────────────

  return (
    <>
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Back link */}
        <button
          type="button"
          onClick={() => router.back()}
          className="inline-flex items-center gap-1.5 text-sm text-text-secondary transition-colors hover:text-text-primary"
        >
          <ArrowLeft size={14} />
          Back to Courses
        </button>

        {/* Course header */}
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-lg font-bold text-accent-green">
              {enrollment.course_code}
            </span>
            <span className="text-text-secondary">·</span>
            <span className="text-lg font-semibold text-text-primary">
              {enrollment.course_title}
            </span>
          </div>
          <div className="mt-1 flex flex-wrap gap-2 text-sm text-text-secondary">
            <span>
              {enrollment.term} {enrollment.year}
            </span>
            {enrollment.meeting_time && (
              <>
                <span>·</span>
                <span>{enrollment.meeting_time}</span>
              </>
            )}
            {enrollment.room && (
              <>
                <span>·</span>
                <span>{enrollment.room}</span>
              </>
            )}
            <span>·</span>
            <span>{enrollment.ects} ECTS</span>
          </div>
          </div>
        </div>

        <div className="flex gap-2 border-b border-border-primary">
          {(["deadlines", "materials", "mindmaps"] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setPageTab(tab)}
              className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
                pageTab === tab
                  ? "border-accent-green text-accent-green"
                  : "border-transparent text-text-secondary hover:text-text-primary"
              }`}
            >
              {tab === "deadlines" ? "Deadlines" : tab === "materials" ? "Materials" : "Mindmaps"}
            </button>
          ))}
        </div>

        {pageTab === "deadlines" ? (
          <>
            <div className="grid grid-cols-3 gap-3">
              <GlassCard padding={false} className="p-4 text-center">
                <p className="text-2xl font-bold text-text-primary">{totalCount}</p>
                <p className="mt-0.5 text-xs text-text-secondary">Total</p>
              </GlassCard>
              <GlassCard padding={false} className="p-4 text-center">
                <p className="text-2xl font-bold text-orange-400">{upcomingCount}</p>
                <p className="mt-0.5 text-xs text-text-secondary">⏰ Upcoming</p>
              </GlassCard>
              <GlassCard padding={false} className="p-4 text-center">
                <p className="text-2xl font-bold text-red-400">{overdueCount}</p>
                <p className="mt-0.5 text-xs text-text-secondary">⚠ Overdue</p>
              </GlassCard>
            </div>

            <GlassCard padding={false} className="overflow-hidden">
              <div className="flex items-center justify-between border-b border-[#2a2a2a] px-5 py-4">
                <h2 className="text-sm font-semibold text-text-primary">
                  Deadlines &amp; Assessments
                </h2>
                <button
                  type="button"
                  onClick={() => {
                    setEditingAssessment(null);
                    setModalOpen(true);
                  }}
                  className="btn-secondary inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs"
                >
                  <Plus size={12} />
                  Add deadline
                </button>
              </div>

              <div className="flex border-b border-[#2a2a2a]">
                {(["all", "upcoming", "completed", "overdue"] as FilterTab[]).map(
                  (t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setFilter(t)}
                      className={`px-4 py-2.5 text-xs capitalize transition-colors ${
                        filter === t
                          ? "border-b-2 border-accent-green text-text-primary"
                          : "text-text-secondary hover:text-text-primary"
                      }`}
                    >
                      {t}
                    </button>
                  )
                )}
              </div>

              {assessmentsLoading ? (
                <div className="flex justify-center py-10">
                  <Spinner />
                </div>
              ) : filtered.length === 0 ? (
                <div className="flex flex-col items-center gap-3 py-12 text-center">
                  <p className="text-sm text-text-secondary">
                    No assessments here yet
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setEditingAssessment(null);
                      setModalOpen(true);
                    }}
                    className="text-xs text-accent-green transition-opacity hover:opacity-75"
                  >
                    + Add your first deadline →
                  </button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-[#2a2a2a] text-xs text-text-secondary">
                        <th className="px-5 py-2.5 text-left font-medium">
                          Status
                        </th>
                        <th className="px-3 py-2.5 text-left font-medium">
                          Assessment
                        </th>
                        <th className="px-3 py-2.5 text-left font-medium">Type</th>
                        <th className="px-3 py-2.5 text-left font-medium">
                          Deadline
                        </th>
                        <th className="px-3 py-2.5 text-left font-medium">
                          Weight
                        </th>
                        <th className="px-3 py-2.5 text-left font-medium">
                          Score
                        </th>
                        <th className="px-3 py-2.5 text-right font-medium">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map((assessment) => {
                        const isConfirmingDelete = confirmDeleteId === assessment.id;
                        const badge = BADGE_STYLES[assessment.assessment_type];
                        const isPast = new Date(assessment.deadline) < now;
                        const prediction = findAssessmentPrediction(
                          studyGroup,
                          assessment.assessment_type,
                        );
                        const predicted = predictedGradeBadge(
                          prediction?.predicted_grade_letter ?? null,
                          prediction?.predicted_score_pct ?? null,
                        );
                        const hasMockExam =
                          ["quiz", "midterm", "final"].includes(
                            assessment.assessment_type
                          ) &&
                          !assessment.is_completed &&
                          !isPast;

                        return (
                          <Fragment key={assessment.id}>
                            <tr className="border-b border-[#1e1e1e] transition-colors hover:bg-white/[0.02]">
                              <td className="px-5 py-3">
                                <button
                                  type="button"
                                  onClick={() =>
                                    void toggleComplete(assessment.id, courseId)
                                  }
                                  className="text-text-secondary transition-colors hover:text-accent-green"
                                >
                                  {assessment.is_completed ? (
                                    <CheckSquare
                                      size={16}
                                      className="text-accent-green"
                                    />
                                  ) : (
                                    <Square size={16} />
                                  )}
                                </button>
                              </td>
                              <td className="max-w-[180px] px-3 py-3">
                                <span
                                  className={`font-medium ${
                                    assessment.is_completed
                                      ? "text-text-secondary line-through"
                                      : "text-text-primary"
                                  }`}
                                >
                                  {assessment.title}
                                </span>
                              </td>
                              <td className="px-3 py-3">
                                <span
                                  className="inline-block rounded-md px-2 py-0.5 text-xs font-medium"
                                  style={{
                                    background: badge.bg,
                                    color: badge.text,
                                  }}
                                >
                                  {ASSESSMENT_LABELS[assessment.assessment_type]}
                                </span>
                              </td>
                              <td className="px-3 py-3 text-xs">
                                <span className="text-text-primary">
                                  {formatDeadline(assessment.deadline)}
                                </span>
                                <br />
                                <span
                                  className={
                                    !assessment.is_completed && isPast
                                      ? "text-accent-red"
                                      : "text-text-secondary"
                                  }
                                >
                                  {relativeTime(assessment.deadline)}
                                </span>
                              </td>
                              <td className="px-3 py-3 text-xs text-text-secondary">
                                {assessment.weight != null
                                  ? `${assessment.weight}%`
                                  : "—"}
                              </td>
                              <td className="px-3 py-3 text-xs text-text-secondary">
                                {isPast ? (
                                  <ScoreInput
                                    initialScore={assessment.score}
                                    assessment={assessment}
                                    onSaved={() => {}}
                                  />
                                ) : assessment.score != null ? (
                                  assessment.max_score != null
                                    ? `${assessment.score} / ${assessment.max_score}`
                                    : `${assessment.score}`
                                ) : "—"}
                              </td>
                              <td className="px-3 py-3">
                                <div className="flex items-center justify-end gap-1">
                                  {hasMockExam ? (
                                    <>
                                      <span
                                        className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ${predicted.badgeClass}`}
                                      >
                                        Predicted {predicted.letter}
                                      </span>
                                      <button
                                        type="button"
                                        onClick={() => router.push(`/study/${courseId}`)}
                                        className="inline-flex items-center gap-1 rounded-md
                                          border border-border-primary px-2 py-1 text-[11px]
                                          text-text-secondary transition-colors
                                          hover:border-accent-green hover:bg-[#243111]
                                          hover:text-accent-green"
                                        title="Open AI mock exams"
                                      >
                                        <Brain size={12} />
                                        AI Mock Exam
                                      </button>
                                    </>
                                  ) : null}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setEditingAssessment(assessment);
                                      setModalOpen(true);
                                    }}
                                    className="rounded p-1.5 text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
                                    title="Edit"
                                  >
                                    <Edit2 size={13} />
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() =>
                                      setConfirmDeleteId(
                                        isConfirmingDelete ? null : assessment.id
                                      )
                                    }
                                    className="rounded p-1.5 text-text-secondary transition-colors hover:bg-red-950/50 hover:text-red-400"
                                    title="Delete"
                                  >
                                    <Trash2 size={13} />
                                  </button>
                                </div>
                              </td>
                            </tr>

                            {isConfirmingDelete ? (
                              <tr className="bg-red-950/20">
                                <td colSpan={7} className="px-5 py-2">
                                  <div className="flex items-center gap-3 text-xs">
                                    <span className="text-red-400">
                                      Delete &quot;{assessment.title}&quot;?
                                    </span>
                                    <button
                                      type="button"
                                      disabled={deletingId === assessment.id}
                                      onClick={() => void handleDelete(assessment.id)}
                                      className="rounded bg-red-600/80 px-3 py-1 text-white transition-opacity hover:opacity-80 disabled:opacity-50"
                                    >
                                      {deletingId === assessment.id
                                        ? "Deleting..."
                                        : "Confirm"}
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => setConfirmDeleteId(null)}
                                      className="text-text-secondary hover:text-text-primary"
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ) : null}
                          </Fragment>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </GlassCard>
          </>
        ) : pageTab === "materials" ? (
          <CourseMaterialsPanel enrollment={enrollment} />
        ) : (
          <CourseMindmapsPanel enrollment={enrollment} />
        )}
      </div>

      {/* Add / Edit modal */}
      <AddAssessmentModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingAssessment(null);
        }}
        enrollment={enrollment}
        initialData={editingAssessment ?? undefined}
        onSuccess={() => {
          void fetchForCourse(courseId);
        }}
      />

    </>
  );
}
