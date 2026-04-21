"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  BookOpen,
  FileText,
  LoaderCircle,
  Plus,
  RefreshCw,
  Save,
  Trash2,
} from "lucide-react";

import { api } from "@/lib/api";
import type {
  AdminCourseOffering,
  AdminMockExamItem,
  AdminMockExamQuestion,
  ApiResponse,
  CourseListItem,
  MockExamAdminDetail,
  MockExamQuestionCurationStatus,
  AssessmentType,
} from "@/types";

const EXAM_TYPES: AssessmentType[] = ["quiz", "midterm", "final"];
const QUESTION_PAGE_SIZE = 5;

function assessmentLabel(type: AssessmentType, number: number) {
  const labels: Record<AssessmentType, string> = {
    homework: "Homework",
    quiz: "Quiz",
    midterm: "Midterm",
    final: "Final",
    project: "Project",
    lab: "Lab",
    presentation: "Presentation",
    other: "Assessment",
  };
  return `${labels[type]} ${number}`;
}

function matchesQuestion(question: AdminMockExamQuestion, query: string) {
  if (!query.trim()) return true;
  const needle = query.trim().toLowerCase();
  const haystack = [
    question.question_text,
    question.source_label,
    question.historical_course_offering_label ?? "",
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(needle);
}

function emptyQuestionForm() {
  return {
    id: null as number | null,
    source: "ai" as AdminMockExamQuestion["source"],
    historic_section: "",
    historic_year: "",
    historical_course_offering_id: "",
    question_text: "",
    answer_variant_1: "",
    answer_variant_2: "",
    answer_variant_3: "",
    answer_variant_4: "",
    answer_variant_5: "",
    answer_variant_6: "",
    correct_option_index: "1",
    explanation: "",
  };
}

function emptyExamForm() {
  return {
    id: null as number | null,
    assessment_type: "quiz" as AssessmentType,
    assessment_number: "",
    time_limit_minutes: "",
    instructions: "",
    is_active: true,
    selected_question_ids: [] as number[],
  };
}

type CourseResources = {
  offerings: AdminCourseOffering[];
  exams: AdminMockExamItem[];
  questions: AdminMockExamQuestion[];
};

type MockExamCourseView = "overview" | "questions" | "builder";

export function MockExamCourseManagement({
  courseId,
  view = "overview",
  editExamId = null,
}: {
  courseId: number;
  view?: MockExamCourseView;
  editExamId?: number | null;
}) {
  const router = useRouter();
  const [course, setCourse] = useState<CourseListItem | null>(null);
  const [offerings, setOfferings] = useState<AdminCourseOffering[]>([]);
  const [questions, setQuestions] = useState<AdminMockExamQuestion[]>([]);
  const [exams, setExams] = useState<AdminMockExamItem[]>([]);
  const [questionForm, setQuestionForm] = useState(emptyQuestionForm());
  const [examForm, setExamForm] = useState(emptyExamForm());
  const [loadingPage, setLoadingPage] = useState(true);
  const [refreshingData, setRefreshingData] = useState(false);
  const [savingQuestion, setSavingQuestion] = useState(false);
  const [savingExam, setSavingExam] = useState(false);
  const [loadingExamDetail, setLoadingExamDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [questionPage, setQuestionPage] = useState(1);
  const [selectedQuestionId, setSelectedQuestionId] = useState<number | null>(null);
  const [questionSearch, setQuestionSearch] = useState("");
  const [builderSearch, setBuilderSearch] = useState("");
  const [builderPage, setBuilderPage] = useState(1);
  const [builderPreviewId, setBuilderPreviewId] = useState<number | null>(null);
  const [questionEditorOpen, setQuestionEditorOpen] = useState(false);
  const [pendingQuestions, setPendingQuestions] = useState<AdminMockExamQuestion[]>([]);
  const [curating, setCurating] = useState<number | null>(null);

  useEffect(() => {
    void loadPageData();
  }, [courseId]);

  async function loadPageData() {
    setLoadingPage(true);
    setError(null);
    try {
      const [coursesRes, resources] = await Promise.all([
        api.get<ApiResponse<CourseListItem[]>>("/admin/courses?limit=100"),
        loadCourseResources(courseId),
      ]);
      const selectedCourse = (coursesRes.data ?? []).find((item) => item.id === courseId);
      if (!selectedCourse) {
        throw new Error("Course not found in admin course list");
      }
      setCourse(selectedCourse);
      syncResources(resources);
      resetEditors();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load mock exam page");
    } finally {
      setLoadingPage(false);
    }
  }

  async function refreshCourseData() {
    setRefreshingData(true);
    setError(null);
    try {
      const resources = await loadCourseResources(courseId);
      syncResources(resources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh mock exam data");
    } finally {
      setRefreshingData(false);
    }
  }

  async function loadCourseResources(id: number): Promise<CourseResources> {
    const [offeringsRes, examsRes, questionsRes] = await Promise.all([
      api.get<ApiResponse<AdminCourseOffering[]>>(`/admin/courses/${id}/offerings`),
      api.get<ApiResponse<AdminMockExamItem[]>>(`/admin/mock-exams?course_id=${id}`),
      api.get<ApiResponse<AdminMockExamQuestion[]>>(
        `/admin/mock-exam-questions?course_id=${id}`
      ),
    ]);
    void loadPendingQuestions(id);
    return {
      offerings: offeringsRes.data ?? [],
      exams: examsRes.data ?? [],
      questions: questionsRes.data ?? [],
    };
  }

  async function loadPendingQuestions(id: number) {
    try {
      const res = await api.get<ApiResponse<AdminMockExamQuestion[]>>(
        `/admin/mock-exam-questions?course_id=${id}&curation_status=pending`
      );
      setPendingQuestions(res.data ?? []);
    } catch {
      // non-critical
    }
  }

  async function curateQuestion(
    questionId: number,
    status: MockExamQuestionCurationStatus,
    rejectionReason?: string,
  ) {
    setCurating(questionId);
    try {
      await api.patch<ApiResponse<AdminMockExamQuestion>>(
        `/admin/mock-exam-questions/${questionId}/curate`,
        { status, rejection_reason: rejectionReason ?? null },
      );
      setPendingQuestions((prev) => prev.filter((q) => q.id !== questionId));
      if (status === "approved") {
        await refreshCourseData();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to curate question");
    } finally {
      setCurating(null);
    }
  }

  function syncResources(resources: CourseResources) {
    setOfferings(resources.offerings);
    setExams(resources.exams);
    setQuestions(resources.questions);
  }

  function resetEditors() {
    setQuestionForm(emptyQuestionForm());
    setExamForm(emptyExamForm());
    setQuestionEditorOpen(false);
  }

  async function saveQuestion() {
    setSavingQuestion(true);
    setError(null);
    try {
      const body = {
        course_id: courseId,
        source: questionForm.source,
        historic_section: questionForm.historic_section || undefined,
        historic_year: questionForm.historic_year ? Number(questionForm.historic_year) : undefined,
        historical_course_offering_id: questionForm.historical_course_offering_id
          ? Number(questionForm.historical_course_offering_id)
          : null,
        question_text: questionForm.question_text,
        answer_variant_1: questionForm.answer_variant_1,
        answer_variant_2: questionForm.answer_variant_2,
        answer_variant_3: questionForm.answer_variant_3 || undefined,
        answer_variant_4: questionForm.answer_variant_4 || undefined,
        answer_variant_5: questionForm.answer_variant_5 || undefined,
        answer_variant_6: questionForm.answer_variant_6 || undefined,
        correct_option_index: Number(questionForm.correct_option_index),
        explanation: questionForm.explanation || undefined,
      };
      if (questionForm.id) {
        await api.patch<ApiResponse<AdminMockExamQuestion>>(
          `/admin/mock-exam-questions/${questionForm.id}`,
          body
        );
      } else {
        await api.post<ApiResponse<AdminMockExamQuestion>>(
          "/admin/mock-exam-questions",
          body
        );
      }
      setQuestionForm(emptyQuestionForm());
      setQuestionEditorOpen(false);
      await refreshCourseData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save question");
    } finally {
      setSavingQuestion(false);
    }
  }

  async function saveExam() {
    setSavingExam(true);
    setError(null);
    try {
      const questionsPayload = examForm.selected_question_ids.map((questionId, index) => ({
        question_id: questionId,
        position: index + 1,
        points: 1,
      }));
      const body = {
        course_id: courseId,
        assessment_type: examForm.assessment_type,
        assessment_number: Number(examForm.assessment_number),
        time_limit_minutes: examForm.time_limit_minutes
          ? Number(examForm.time_limit_minutes)
          : undefined,
        instructions: examForm.instructions || undefined,
        is_active: examForm.is_active,
        questions: questionsPayload,
      };
      if (examForm.id) {
        await api.patch<ApiResponse<MockExamAdminDetail>>(
          `/admin/mock-exams/${examForm.id}`,
          body
        );
      } else {
        await api.post<ApiResponse<MockExamAdminDetail>>("/admin/mock-exams", body);
      }
      await refreshCourseData();
      resetEditors();
      router.push(`/admin/mock-exams/${courseId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save mock exam");
    } finally {
      setSavingExam(false);
    }
  }

  async function removeQuestion(questionId: number) {
    if (!window.confirm("Delete this question?")) return;
    try {
      await api.delete<ApiResponse>(`/admin/mock-exam-questions/${questionId}`);
      await refreshCourseData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete question");
    }
  }

  async function deactivateExam(examId: number) {
    try {
      await api.post<ApiResponse>(`/admin/mock-exams/${examId}/deactivate`);
      await refreshCourseData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to deactivate exam");
    }
  }

  async function removeExam(examId: number) {
    if (!window.confirm("Delete this mock exam version?")) return;
    try {
      await api.delete<ApiResponse>(`/admin/mock-exams/${examId}`);
      await refreshCourseData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete mock exam");
    }
  }

  async function editExam(examId: number) {
    setError(null);
    try {
      setLoadingExamDetail(true);
      const response = await api.get<ApiResponse<MockExamAdminDetail>>(
        `/admin/mock-exams/${examId}`
      );
      const detail = response.data;
      const selectedIds = detail.questions.map((item) => {
        return item.question.id;
      });
      setExamForm({
        id: detail.exam.id,
        assessment_type: detail.exam.assessment_type,
        assessment_number: String(detail.exam.assessment_number),
        time_limit_minutes: detail.exam.time_limit_minutes
          ? String(detail.exam.time_limit_minutes)
          : "",
        instructions: detail.exam.instructions ?? "",
        is_active: detail.exam.is_active,
        selected_question_ids: selectedIds,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load exam detail");
    } finally {
      setLoadingExamDetail(false);
    }
  }

  function editQuestion(question: AdminMockExamQuestion) {
    setSelectedQuestionId(question.id);
    setQuestionEditorOpen(true);
    setQuestionForm({
      id: question.id,
      source: question.source,
      historic_section: question.historic_section ?? "",
      historic_year: question.historic_year ? String(question.historic_year) : "",
      historical_course_offering_id: question.historical_course_offering_id
        ? String(question.historical_course_offering_id)
        : "",
      question_text: question.question_text,
      answer_variant_1: question.answer_variant_1,
      answer_variant_2: question.answer_variant_2,
      answer_variant_3: question.answer_variant_3 ?? "",
      answer_variant_4: question.answer_variant_4 ?? "",
      answer_variant_5: question.answer_variant_5 ?? "",
      answer_variant_6: question.answer_variant_6 ?? "",
      correct_option_index: String(question.correct_option_index),
      explanation: question.explanation ?? "",
    });
  }

  useEffect(() => {
    if (view !== "builder") return;
    if (!editExamId) {
      setExamForm(emptyExamForm());
      return;
    }
    void editExam(editExamId);
  }, [editExamId, view]);

  useEffect(() => {
    const totalPages = Math.max(1, Math.ceil(questions.length / QUESTION_PAGE_SIZE));
    setQuestionPage((page) => Math.min(page, totalPages));
    if (!questions.length) {
      setSelectedQuestionId(null);
      return;
    }
    if (selectedQuestionId == null) {
      return;
    }
    const exists = questions.some((item) => item.id === selectedQuestionId);
    if (!exists) {
      setSelectedQuestionId(questions[0].id);
    }
  }, [questions, selectedQuestionId]);

  const filteredQuestions = useMemo(
    () => questions.filter((question) => matchesQuestion(question, questionSearch)),
    [questionSearch, questions],
  );
  const totalQuestionPages = Math.max(
    1,
    Math.ceil(filteredQuestions.length / QUESTION_PAGE_SIZE),
  );
  const paginatedQuestions = useMemo(() => {
    const start = (questionPage - 1) * QUESTION_PAGE_SIZE;
    return filteredQuestions.slice(start, start + QUESTION_PAGE_SIZE);
  }, [filteredQuestions, questionPage]);
  const builderQuestions = useMemo(
    () => questions.filter((question) => matchesQuestion(question, builderSearch)),
    [builderSearch, questions],
  );
  const totalBuilderPages = Math.max(
    1,
    Math.ceil(builderQuestions.length / QUESTION_PAGE_SIZE),
  );
  const paginatedBuilderQuestions = useMemo(() => {
    const start = (builderPage - 1) * QUESTION_PAGE_SIZE;
    return builderQuestions.slice(start, start + QUESTION_PAGE_SIZE);
  }, [builderPage, builderQuestions]);

  const selectedQuestion = questions.find((item) => item.id === selectedQuestionId) ?? null;
  const builderPreviewQuestion =
    questions.find((item) => item.id === builderPreviewId) ?? null;
  const backHref =
    view === "overview" ? "/admin?tab=mock-exams" : `/admin/mock-exams/${courseId}`;
  const backLabel =
    view === "overview" ? "Back to course list" : "Back to course mock exams";

  useEffect(() => {
    setQuestionPage(1);
  }, [questionSearch]);

  useEffect(() => {
    setBuilderPage(1);
  }, [builderSearch]);

  useEffect(() => {
    setQuestionPage((page) => Math.min(page, totalQuestionPages));
  }, [totalQuestionPages]);

  useEffect(() => {
    setBuilderPage((page) => Math.min(page, totalBuilderPages));
  }, [totalBuilderPages]);

  useEffect(() => {
    if (!builderQuestions.length) {
      setBuilderPreviewId(null);
      return;
    }
    const exists = builderQuestions.some((item) => item.id === builderPreviewId);
    if (!exists) {
      setBuilderPreviewId(builderQuestions[0].id);
    }
  }, [builderPreviewId, builderQuestions]);

  if (loadingPage) {
    return (
      <div className="flex justify-center py-16">
        <LoaderCircle size={20} className="animate-spin text-text-secondary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link
              href={backHref}
              className="inline-flex items-center gap-2 text-sm text-text-secondary transition-colors hover:text-text-primary"
            >
              <ArrowLeft size={14} />
              {backLabel}
            </Link>
            <div className="mt-4 flex items-center gap-2">
              <BookOpen size={22} className="text-accent-green" />
              <div>
                <h1 className="text-2xl font-semibold text-text-primary">
                  {course?.code} {course?.level}
                </h1>
                <p className="text-sm text-text-secondary">{course?.title}</p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {view === "overview" ? (
              <>
                <Link
                  href={`/admin/mock-exams/${courseId}/create`}
                  className="inline-flex items-center gap-2 rounded-full bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary"
                >
                  <Plus size={14} />
                  Create Mock Exam
                </Link>
                <Link
                  href={`/admin/mock-exams/${courseId}/questions`}
                  className="btn-secondary inline-flex items-center gap-2 px-4 py-2 text-sm"
                >
                  Manage Question Bank
                  {pendingQuestions.length > 0 && (
                    <span className="rounded-full bg-accent-orange px-1.5 py-0.5 text-xs font-bold text-white">
                      {pendingQuestions.length}
                    </span>
                  )}
                </Link>
              </>
            ) : null}
            <button
              type="button"
              onClick={() => void refreshCourseData()}
              className="btn-secondary inline-flex items-center gap-2 px-4 py-2 text-sm"
            >
              <RefreshCw size={14} className={refreshingData ? "animate-spin" : ""} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {error ? (
        <div className="rounded-2xl bg-accent-red-dim px-4 py-3 text-sm text-accent-red">
          {error}
        </div>
      ) : null}

      {view === "overview" ? (
        <OverviewPanel
          courseId={courseId}
          exams={exams}
          onDeactivate={deactivateExam}
          onDelete={removeExam}
        />
      ) : null}

      {view === "questions" ? (
        <>
          {pendingQuestions.length > 0 && (
            <CurationPanel
              questions={pendingQuestions}
              curating={curating}
              onApprove={(id) => void curateQuestion(id, "approved")}
              onReject={(id, reason) => void curateQuestion(id, "rejected", reason)}
            />
          )}
          <QuestionBankPanel
            offerings={offerings}
            questions={paginatedQuestions}
            selectedQuestion={selectedQuestion}
            form={questionForm}
            editorOpen={questionEditorOpen}
            page={questionPage}
            search={questionSearch}
            totalPages={totalQuestionPages}
            onCloseEditor={() => setQuestionEditorOpen(false)}
            onDelete={removeQuestion}
            onEdit={editQuestion}
            onNewQuestion={() => {
              setSelectedQuestionId(null);
              setQuestionEditorOpen(true);
              setQuestionForm(emptyQuestionForm());
            }}
            onPageChange={setQuestionPage}
            onSearchChange={setQuestionSearch}
            onSelectQuestion={setSelectedQuestionId}
            onFormChange={setQuestionForm}
            onSave={saveQuestion}
            saving={savingQuestion}
          />
        </>
      ) : null}

      {view === "builder" ? (
        <MockExamFormPanel
          builderPage={builderPage}
          previewQuestion={builderPreviewQuestion}
          questions={paginatedBuilderQuestions}
          form={examForm}
          onFormChange={setExamForm}
          onPageChange={setBuilderPage}
          onPreviewQuestion={setBuilderPreviewId}
          onSearchChange={setBuilderSearch}
          onSave={saveExam}
          search={builderSearch}
          saving={savingExam || loadingExamDetail}
          totalPages={totalBuilderPages}
        />
      ) : null}
    </div>
  );
}

function OverviewPanel({
  courseId,
  exams,
  onDeactivate,
  onDelete,
}: {
  courseId: number;
  exams: AdminMockExamItem[];
  onDeactivate: (examId: number) => Promise<void>;
  onDelete: (examId: number) => Promise<void>;
}) {
  return (
    <div className="glass-card p-6">
      <div className="mb-4 flex items-center gap-2">
        <FileText size={20} className="text-accent-green" />
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            Current Mock Exams
          </h2>
          <p className="text-sm text-text-secondary">
            Review the live versions for this course before creating a new one.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {exams.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No mock exams for this course yet. Use "Create Mock Exam" to add the first one.
          </p>
        ) : (
          exams.map((exam) => (
            <div
              key={exam.id}
              className="rounded-2xl border border-border-primary bg-white/[0.03] p-4"
            >
              <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-accent-green/10 px-2.5 py-1 text-[11px] font-semibold tracking-wide text-accent-green">
                      {assessmentLabel(
                        exam.assessment_type,
                        exam.assessment_number,
                      )}
                    </span>
                    <span className="text-sm font-semibold text-text-primary">
                      Mock {exam.version}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-3 text-xs text-text-secondary">
                    <span>{exam.question_count} questions</span>
                    <span>{exam.total_attempts} attempts</span>
                    <span>Best {exam.best_score_pct ?? "—"}%</span>
                    <span>Average {exam.average_score_pct ?? "—"}%</span>
                    <span>{exam.active_attempts} active</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link
                    href={`/admin/mock-exams/${courseId}/create?exam_id=${exam.id}`}
                    className="btn-secondary px-3 py-2 text-xs"
                  >
                    Edit as New Version
                  </Link>
                  <button
                    type="button"
                    onClick={() => void onDeactivate(exam.id)}
                    className="btn-secondary px-3 py-2 text-xs"
                  >
                    Deactivate
                  </button>
                  <button
                    type="button"
                    onClick={() => void onDelete(exam.id)}
                    className="rounded-lg border border-border-primary px-3 py-2 text-xs text-accent-red transition-colors hover:bg-accent-red-dim"
                  >
                    <span className="inline-flex items-center gap-1">
                      <Trash2 size={13} />
                      Delete
                    </span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function QuestionBankPanel({
  offerings,
  questions,
  selectedQuestion,
  form,
  editorOpen,
  page,
  search,
  totalPages,
  onCloseEditor,
  onFormChange,
  onEdit,
  onNewQuestion,
  onPageChange,
  onSearchChange,
  onSelectQuestion,
  onDelete,
  onSave,
  saving,
}: {
  offerings: AdminCourseOffering[];
  questions: AdminMockExamQuestion[];
  selectedQuestion: AdminMockExamQuestion | null;
  form: ReturnType<typeof emptyQuestionForm>;
  editorOpen: boolean;
  page: number;
  search: string;
  totalPages: number;
  onCloseEditor: () => void;
  onFormChange: (value: ReturnType<typeof emptyQuestionForm>) => void;
  onEdit: (question: AdminMockExamQuestion) => void;
  onNewQuestion: () => void;
  onPageChange: (value: number | ((current: number) => number)) => void;
  onSearchChange: (value: string) => void;
  onSelectQuestion: (questionId: number) => void;
  onDelete: (questionId: number) => void;
  onSave: () => void;
  saving: boolean;
}) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-text-primary">Question Bank</h3>
        <button
          type="button"
          onClick={onNewQuestion}
          className="btn-secondary px-3 py-2 text-xs"
        >
          New Question
        </button>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="space-y-4">
          <input
            type="text"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search questions"
            className="glass-input w-full px-3 py-2 text-sm"
          />
          <div className="space-y-3">
            {questions.map((question) => {
              const selected = selectedQuestion?.id === question.id;
              return (
                <button
                  key={question.id}
                  type="button"
                  onClick={() => onSelectQuestion(question.id)}
                  className={`w-full rounded-2xl border p-4 text-left transition-colors ${
                    selected
                      ? "border-accent-green/50 bg-accent-green/5"
                      : "border-border-primary bg-white/[0.03] hover:border-accent-green/40"
                  }`}
                >
                  <p className="line-clamp-3 text-sm text-text-primary">
                    {question.question_text}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-3 text-xs text-text-secondary">
                    <span>
                      {question.source_label}
                      {question.historical_course_offering_label
                        ? ` · ${question.historical_course_offering_label}`
                        : ""}
                    </span>
                  </div>
                </button>
              );
            })}
            {questions.length === 0 ? (
              <p className="text-sm text-text-secondary">
                No questions found on this page yet.
              </p>
            ) : null}
          </div>

          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => onPageChange((current) => Math.max(current - 1, 1))}
              disabled={page === 1}
              className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
            >
              Back
            </button>
            <p className="min-w-6 text-center text-sm text-text-secondary">{page}</p>
            <button
              type="button"
              onClick={() =>
                onPageChange((current) => Math.min(current + 1, totalPages))
              }
              disabled={page >= totalPages}
              className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
            >
              Next
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {selectedQuestion ? (
            <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-wide text-text-secondary">Preview</p>
              <p className="mt-3 text-sm font-medium text-text-primary">
                {selectedQuestion.question_text}
              </p>
              <div className="mt-4 space-y-2 text-sm text-text-secondary">
                {[1, 2, 3, 4, 5, 6].map((index) => {
                  const value =
                    selectedQuestion[
                      `answer_variant_${index}` as keyof AdminMockExamQuestion
                    ];
                  if (typeof value !== "string" || !value) return null;
                  const correct = selectedQuestion.correct_option_index === index;
                  return (
                    <div
                      key={index}
                      className={`rounded-xl border px-3 py-2 ${
                        correct
                          ? "border-accent-green/50 bg-accent-green/5 text-accent-green"
                          : "border-border-primary bg-white/[0.03]"
                      }`}
                    >
                      {index}. {value}
                    </div>
                  );
                })}
              </div>
              {selectedQuestion.explanation ? (
                <p className="mt-4 text-sm text-text-secondary">
                  {selectedQuestion.explanation}
                </p>
              ) : null}
              <div className="mt-4 flex gap-2">
                <button
                  type="button"
                  onClick={() => onEdit(selectedQuestion)}
                  className="btn-secondary px-3 py-2 text-xs"
                >
                  Edit This Question
                </button>
                <button
                  type="button"
                  onClick={() => onDelete(selectedQuestion.id)}
                  className="rounded-lg border border-border-primary px-3 py-2 text-xs text-accent-red transition-colors hover:bg-accent-red-dim"
                >
                  Delete
                </button>
              </div>
            </div>
          ) : null}

          {editorOpen ? (
            <div className="grid gap-3 rounded-2xl border border-border-primary bg-white/[0.03] p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-text-primary">
                  {form.id ? "Edit Question" : "New Question"}
                </p>
                <button
                  type="button"
                  onClick={onCloseEditor}
                  className="text-xs text-text-secondary transition-colors hover:text-text-primary"
                >
                  Close
                </button>
              </div>
              <select
                value={form.source}
                onChange={(event) =>
                  onFormChange({
                    ...form,
                    source: event.target.value as AdminMockExamQuestion["source"],
                    historical_course_offering_id:
                      event.target.value === "historic"
                        ? form.historical_course_offering_id
                        : "",
                  })
                }
                className="glass-input px-3 py-2 text-sm"
              >
                <option value="ai">AI</option>
                <option value="historic">Historic</option>
                <option value="rumored">Rumored</option>
                <option value="tutor_made">Tutor made</option>
              </select>
              {form.source === "historic" ? (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex flex-col gap-1">
                      <label className="text-xs text-text-secondary">Section (optional)</label>
                      <input
                        type="text"
                        value={form.historic_section}
                        onChange={(event) =>
                          onFormChange({ ...form, historic_section: event.target.value })
                        }
                        placeholder="e.g. Section A"
                        className="glass-input px-3 py-2 text-sm"
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <label className="text-xs text-text-secondary">Year (optional)</label>
                      <input
                        type="number"
                        value={form.historic_year}
                        onChange={(event) =>
                          onFormChange({ ...form, historic_year: event.target.value })
                        }
                        placeholder="e.g. 2023"
                        className="glass-input px-3 py-2 text-sm"
                      />
                    </div>
                  </div>
                  <select
                    value={form.historical_course_offering_id}
                    onChange={(event) =>
                      onFormChange({
                        ...form,
                        historical_course_offering_id: event.target.value,
                      })
                    }
                    className="glass-input px-3 py-2 text-sm"
                  >
                    <option value="">General historic question</option>
                    {offerings.map((offering) => (
                      <option key={offering.id} value={offering.id}>
                        {offering.term} {offering.year} · {offering.section ?? "No section"}
                      </option>
                    ))}
                  </select>
                </>
              ) : null}
              <textarea
                value={form.question_text}
                onChange={(event) =>
                  onFormChange({ ...form, question_text: event.target.value })
                }
                placeholder="Question text"
                className="glass-input min-h-24 px-3 py-2 text-sm"
              />
              {[1, 2, 3, 4, 5, 6].map((index) => (
                <input
                  key={index}
                  type="text"
                  value={form[`answer_variant_${index}` as keyof typeof form] as string}
                  onChange={(event) =>
                    onFormChange({
                      ...form,
                      [`answer_variant_${index}`]: event.target.value,
                    })
                  }
                  placeholder={`Answer option ${index}${index > 2 ? " (optional)" : ""}`}
                  className="glass-input px-3 py-2 text-sm"
                />
              ))}
              <div className="grid gap-3 md:grid-cols-2">
                <select
                  value={form.correct_option_index}
                  onChange={(event) =>
                    onFormChange({ ...form, correct_option_index: event.target.value })
                  }
                  className="glass-input px-3 py-2 text-sm"
                >
                  {[1, 2, 3, 4, 5, 6].map((value) => (
                    <option key={value} value={value}>
                      Correct option {value}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  value={form.explanation}
                  onChange={(event) =>
                    onFormChange({ ...form, explanation: event.target.value })
                  }
                  placeholder="Explanation (optional)"
                  className="glass-input px-3 py-2 text-sm"
                />
              </div>
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => void onSave()}
                  disabled={saving}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary"
                >
                  {saving ? (
                    <LoaderCircle size={14} className="animate-spin" />
                  ) : (
                    <Plus size={14} />
                  )}
                  {form.id ? "Save Question" : "Add Question"}
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function MockExamFormPanel({
  builderPage,
  form,
  previewQuestion,
  questions,
  onFormChange,
  onPageChange,
  onPreviewQuestion,
  onSearchChange,
  onSave,
  search,
  saving,
  totalPages,
}: {
  builderPage: number;
  form: ReturnType<typeof emptyExamForm>;
  previewQuestion: AdminMockExamQuestion | null;
  questions: AdminMockExamQuestion[];
  onFormChange: (value: ReturnType<typeof emptyExamForm>) => void;
  onPageChange: (value: number | ((current: number) => number)) => void;
  onPreviewQuestion: (id: number) => void;
  onSearchChange: (value: string) => void;
  onSave: () => void;
  search: string;
  saving: boolean;
  totalPages: number;
}) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-text-primary">Mock Exam Builder</h3>
      </div>

      <div className="mt-4 grid gap-3">
        <div className="grid gap-3 md:grid-cols-2">
          <select
            value={form.assessment_type}
            onChange={(event) =>
              onFormChange({
                ...form,
                assessment_type: event.target.value as AssessmentType,
              })
            }
            className="glass-input px-3 py-2 text-sm"
          >
            {EXAM_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={form.time_limit_minutes}
            onChange={(event) =>
              onFormChange({ ...form, time_limit_minutes: event.target.value })
            }
            placeholder="Time limit (minutes)"
            className="glass-input px-3 py-2 text-sm"
          />
        </div>
        <input
          type="number"
          min={1}
          value={form.assessment_number}
          onChange={(event) =>
            onFormChange({ ...form, assessment_number: event.target.value })
          }
          placeholder="Assessment number"
          className="glass-input px-3 py-2 text-sm"
        />
        <textarea
          value={form.instructions}
          onChange={(event) =>
            onFormChange({ ...form, instructions: event.target.value })
          }
          placeholder="Instructions"
          className="glass-input min-h-24 px-3 py-2 text-sm"
        />
        <label className="flex items-center gap-2 text-sm text-text-secondary">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(event) =>
              onFormChange({ ...form, is_active: event.target.checked })
            }
          />
          Publish as active version
        </label>
      </div>

      <div className="mt-6 space-y-3">
        <p className="text-sm font-semibold text-text-primary">Question selection</p>
        <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4">
            <input
              type="text"
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Search questions"
              className="glass-input w-full px-3 py-2 text-sm"
            />
            {questions.length === 0 ? (
              <p className="text-sm text-text-secondary">
                Add questions first to compose a mock exam.
              </p>
            ) : (
              <div className="space-y-3">
                {questions.map((question) => {
                  const selected = form.selected_question_ids.includes(question.id);
                  const previewed = previewQuestion?.id === question.id;
                  return (
                    <button
                      key={question.id}
                      type="button"
                      onClick={() => onPreviewQuestion(question.id)}
                      className={`w-full rounded-2xl border p-4 text-left ${
                        previewed
                          ? "border-accent-green/50 bg-accent-green/5"
                          : "border-border-primary bg-white/[0.03] hover:border-accent-green/40"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() => {
                            const exists = form.selected_question_ids.includes(question.id);
                            const selected_question_ids = exists
                              ? form.selected_question_ids.filter((id) => id !== question.id)
                              : [...form.selected_question_ids, question.id];
                            onFormChange({
                              ...form,
                              selected_question_ids,
                            });
                          }}
                          onClick={(event) => event.stopPropagation()}
                          className="mt-1"
                        />
                        <div className="min-w-0 flex-1">
                          <p className="text-sm text-text-primary">
                            {question.question_text}
                          </p>
                          <p className="mt-2 text-xs text-text-secondary">
                            {question.source_label}
                            {question.historical_course_offering_label
                              ? ` · ${question.historical_course_offering_label}`
                              : ""}
                          </p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            <div className="flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={() => onPageChange((current) => Math.max(current - 1, 1))}
                disabled={builderPage === 1}
                className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
              >
                Back
              </button>
              <p className="min-w-6 text-center text-sm text-text-secondary">
                {builderPage}
              </p>
              <button
                type="button"
                onClick={() =>
                  onPageChange((current) => Math.min(current + 1, totalPages))
                }
                disabled={builderPage >= totalPages}
                className="btn-secondary px-4 py-2 text-sm disabled:opacity-60"
              >
                Next
              </button>
            </div>
          </div>

          <div>
            {previewQuestion ? (
              <div className="rounded-2xl border border-border-primary bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-wide text-text-secondary">Preview</p>
                <p className="mt-3 text-sm font-medium text-text-primary">
                  {previewQuestion.question_text}
                </p>
                <div className="mt-4 space-y-2 text-sm text-text-secondary">
                  {[1, 2, 3, 4, 5, 6].map((index) => {
                    const value =
                      previewQuestion[
                        `answer_variant_${index}` as keyof AdminMockExamQuestion
                      ];
                    if (typeof value !== "string" || !value) return null;
                    const correct = previewQuestion.correct_option_index === index;
                    return (
                      <div
                        key={index}
                        className={`rounded-xl border px-3 py-2 ${
                          correct
                            ? "border-accent-green/50 bg-accent-green/5 text-accent-green"
                            : "border-border-primary bg-white/[0.03]"
                        }`}
                      >
                        {index}. {value}
                      </div>
                    );
                  })}
                </div>
                {previewQuestion.explanation ? (
                  <p className="mt-4 text-sm text-text-secondary">
                    {previewQuestion.explanation}
                  </p>
                ) : null}
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-border-primary p-6 text-sm text-text-secondary">
                Select a question to preview it here.
              </div>
            )}
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => void onSave()}
        disabled={saving || form.selected_question_ids.length === 0}
        className="mt-6 inline-flex items-center justify-center gap-2 rounded-full bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary disabled:opacity-60"
      >
        {saving ? <LoaderCircle size={14} className="animate-spin" /> : <Save size={14} />}
        {form.id ? "Publish New Version" : "Create Mock Exam"}
      </button>
    </div>
  );
}

function CurationPanel({
  questions,
  curating,
  onApprove,
  onReject,
}: {
  questions: AdminMockExamQuestion[];
  curating: number | null;
  onApprove: (id: number) => void;
  onReject: (id: number, reason: string) => void;
}) {
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("");

  function submitReject(id: number) {
    onReject(id, rejectReason);
    setRejectingId(null);
    setRejectReason("");
  }

  return (
    <div className="glass-card p-6">
      <div className="mb-4 flex items-center gap-2">
        <span className="rounded-full bg-accent-orange/10 px-2.5 py-1 text-xs font-semibold text-accent-orange">
          {questions.length} pending
        </span>
        <h3 className="text-sm font-semibold text-text-primary">Pending Curation</h3>
      </div>
      <div className="space-y-3">
        {questions.map((q) => (
          <div
            key={q.id}
            className="rounded-xl border border-border-primary bg-white/[0.02] p-4"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm text-text-primary">{q.question_text}</p>
                <div className="mt-1 flex flex-wrap gap-2 text-xs text-text-muted">
                  <span className="capitalize">{q.source_label}</span>
                  {q.historic_section && <span>· {q.historic_section}</span>}
                  {q.historic_year && <span>· {q.historic_year}</span>}
                  <span>· {[1, 2, 3, 4, 5, 6].filter((i) => q[`answer_variant_${i}` as keyof AdminMockExamQuestion]).length} options</span>
                </div>
                <p className="mt-1 text-xs text-text-secondary line-clamp-2">
                  Correct: {q[`answer_variant_${q.correct_option_index}` as keyof AdminMockExamQuestion] as string}
                </p>
              </div>
              <div className="flex shrink-0 gap-2">
                <button
                  type="button"
                  disabled={curating === q.id}
                  onClick={() => onApprove(q.id)}
                  className="rounded-lg bg-accent-green/10 px-3 py-1.5 text-xs font-medium text-accent-green hover:bg-accent-green/20 disabled:opacity-60"
                >
                  Approve
                </button>
                <button
                  type="button"
                  disabled={curating === q.id}
                  onClick={() => {
                    setRejectingId(q.id);
                    setRejectReason("");
                  }}
                  className="rounded-lg bg-accent-red/10 px-3 py-1.5 text-xs font-medium text-accent-red hover:bg-accent-red/20 disabled:opacity-60"
                >
                  Reject
                </button>
              </div>
            </div>
            {rejectingId === q.id && (
              <div className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Reason for rejection (optional)"
                  className="glass-input flex-1 px-3 py-1.5 text-xs"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") submitReject(q.id);
                    if (e.key === "Escape") setRejectingId(null);
                  }}
                />
                <button
                  type="button"
                  onClick={() => submitReject(q.id)}
                  className="rounded-lg bg-accent-red px-3 py-1.5 text-xs font-medium text-white"
                >
                  Confirm
                </button>
                <button
                  type="button"
                  onClick={() => setRejectingId(null)}
                  className="text-xs text-text-secondary hover:text-text-primary"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
