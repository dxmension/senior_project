"use client";

import { Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AddAssessmentModal } from "@/components/courses/add-assessment-modal";
import { CourseCard } from "@/components/courses/course-card";
import { CourseSearchDialog } from "@/components/courses/course-search-dialog";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { useAssessmentsStore } from "@/stores/assessments";
import type { ApiResponse, EnrollmentItem } from "@/types";

const CURRENT_TERM = "Spring";
const CURRENT_YEAR = 2026;

export default function CoursesPage() {
  const router = useRouter();
  const [enrollments, setEnrollments] = useState<EnrollmentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEnrollment, setSelectedEnrollment] =
    useState<EnrollmentItem | null>(null);
  const [deletingKey, setDeletingKey] = useState<string | null>(null);

  const { byCourse, loadingCourseIds, fetchForCourse } = useAssessmentsStore();

  useEffect(() => {
    async function load() {
      try {
        const response = await api.get<ApiResponse<EnrollmentItem[]>>(
          "/enrollments?status=in_progress"
        );
        const current = (response.data ?? []).filter(
          (e) =>
            e.term === CURRENT_TERM && e.year === CURRENT_YEAR
        );
        setEnrollments(current);
        setErrorMessage(null);
        // Fetch assessments for all enrolled courses in parallel
        await Promise.all(current.map((e) => fetchForCourse(e.course_id)));
      } catch {
        setEnrollments([]);
        setErrorMessage("Could not load current courses.");
      } finally {
        setIsLoading(false);
      }
    }
    void load();
  }, [fetchForCourse]);

  async function handleRemove(item: EnrollmentItem) {
    const key = `${item.course_id}:${item.term}:${item.year}`;
    setDeletingKey(key);
    try {
      await api.delete(
        `/enrollments/${item.course_id}?term=${encodeURIComponent(item.term)}&year=${item.year}`
      );
      setEnrollments((prev) => prev.filter((e) => e.course_id !== item.course_id || e.term !== item.term || e.year !== item.year));
      setErrorMessage(null);
    } catch {
      setErrorMessage("Failed to remove course. Please try again.");
    } finally {
      setDeletingKey(null);
    }
  }

  function handleCreated(item: EnrollmentItem) {
    if (item.term === CURRENT_TERM && item.year === CURRENT_YEAR) {
      setEnrollments((prev) => [...prev, item]);
      void fetchForCourse(item.course_id);
    }
    setErrorMessage(null);
  }

  return (
    <>
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">My Courses</h1>
            <p className="mt-1 text-sm text-text-secondary">
              {CURRENT_TERM} {CURRENT_YEAR}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setDialogOpen(true)}
            className="inline-flex items-center justify-center gap-2 rounded-full
              bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary
              transition-transform hover:scale-[1.02]"
          >
            <Plus size={16} />
            Add Course
          </button>
        </div>

        {errorMessage && (
          <p className="text-sm text-accent-red">{errorMessage}</p>
        )}

        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner text="Loading courses..." />
          </div>
        ) : enrollments.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
            <p className="text-text-secondary">No courses enrolled this semester.</p>
            <button
              type="button"
              onClick={() => setDialogOpen(true)}
              className="btn-secondary rounded-lg px-4 py-2 text-sm"
            >
              + Add your first course
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {enrollments.map((enrollment) => (
              <CourseCard
                key={`${enrollment.course_id}:${enrollment.term}:${enrollment.year}`}
                enrollment={enrollment}
                assessments={byCourse[enrollment.course_id] ?? []}
                assessmentsLoading={loadingCourseIds.has(enrollment.course_id)}
                onAddAssessment={(e) => {
                  e.stopPropagation();
                  setSelectedEnrollment(enrollment);
                  setModalOpen(true);
                }}
                onClick={() => router.push(`/courses/${enrollment.course_id}`)}
                onRemove={() => void handleRemove(enrollment)}
                isRemoving={
                  deletingKey ===
                  `${enrollment.course_id}:${enrollment.term}:${enrollment.year}`
                }
              />
            ))}
          </div>
        )}
      </div>

      <CourseSearchDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={handleCreated}
      />

      {selectedEnrollment && (
        <AddAssessmentModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          enrollment={selectedEnrollment}
          onSuccess={() => {
            void fetchForCourse(selectedEnrollment.course_id);
          }}
        />
      )}
    </>
  );
}
