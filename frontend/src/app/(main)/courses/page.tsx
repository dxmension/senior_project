"use client";

import { Plus } from "lucide-react";
import { useEffect, useState } from "react";

import { CourseSearchDialog } from "@/components/courses/course-search-dialog";
import { CurrentEnrollments } from "@/components/courses/current-enrollments";
import { api } from "@/lib/api";
import type { ApiResponse, EnrollmentItem } from "@/types";

function enrollmentKey(item: EnrollmentItem): string {
  return `${item.course_id}:${item.term}:${item.year}`;
}

export default function CoursesPage() {
  const [enrollments, setEnrollments] = useState<EnrollmentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deletingKey, setDeletingKey] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await api.get<ApiResponse<EnrollmentItem[]>>(
          "/enrollments?status=in_progress"
        );
        setEnrollments(response.data);
        setErrorMessage(null);
      } catch {
        setEnrollments([]);
        setErrorMessage("Could not load current courses.");
      } finally {
        setIsLoading(false);
      }
    }

    void load();
  }, []);

  function handleCreated(item: EnrollmentItem) {
    setEnrollments((current) => [...current, item]);
    setErrorMessage(null);
  }

  async function handleRemove(item: EnrollmentItem) {
    const key = enrollmentKey(item);
    setDeletingKey(key);
    try {
      await api.delete<ApiResponse<{ deleted: boolean }>>(
        `/enrollments/${item.course_id}?term=${item.term}&year=${item.year}`
      );
      setEnrollments((current) =>
        current.filter((entry) => enrollmentKey(entry) !== key)
      );
      setErrorMessage(null);
    } catch (error) {
      const message = error instanceof Error
        ? error.message
        : "Failed to remove current course.";
      setErrorMessage(message);
    } finally {
      setDeletingKey(null);
    }
  }

  return (
    <>
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              My Courses
            </h1>
            <p className="mt-1 text-sm text-text-secondary">
              Search and manage your current semester enrollments here.
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

        {errorMessage ? (
          <p className="text-sm text-accent-red">{errorMessage}</p>
        ) : null}

        <CurrentEnrollments
          enrollments={enrollments}
          isLoading={isLoading}
          deletingKey={deletingKey}
          onRemove={handleRemove}
        />
      </div>

      <CourseSearchDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={handleCreated}
      />
    </>
  );
}
