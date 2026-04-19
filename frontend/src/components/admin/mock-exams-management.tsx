"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, BookOpen, LoaderCircle, RefreshCw } from "lucide-react";

import { api } from "@/lib/api";
import type { ApiResponse, CourseListItem, DatabaseStats } from "@/types";

const COURSE_PICKER_LIMIT = 20;

export function MockExamsManagement() {
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [searchResults, setSearchResults] = useState<CourseListItem[]>([]);
  const [courseQuery, setCourseQuery] = useState("");
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [searchingCourses, setSearchingCourses] = useState(false);
  const [totalCourses, setTotalCourses] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadCourses();
  }, []);

  useEffect(() => {
    const query = courseQuery.trim();
    if (!query) {
      setSearchResults([]);
      return;
    }
    const timeoutId = window.setTimeout(() => {
      void searchCourses(query);
    }, 250);
    return () => window.clearTimeout(timeoutId);
  }, [courseQuery]);

  async function loadCourses() {
    setLoadingCourses(true);
    setError(null);
    try {
      const [coursesRes, statsRes] = await Promise.all([
        api.get<ApiResponse<CourseListItem[]>>(
          `/admin/courses?limit=${COURSE_PICKER_LIMIT}`
        ),
        api.get<ApiResponse<DatabaseStats>>("/admin/stats"),
      ]);
      setCourses(coursesRes.data ?? []);
      setSearchResults([]);
      setTotalCourses(statsRes.data?.total_courses ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load courses");
    } finally {
      setLoadingCourses(false);
    }
  }

  async function searchCourses(query: string) {
    setSearchingCourses(true);
    setError(null);
    try {
      const response = await api.get<ApiResponse<CourseListItem[]>>(
        `/admin/courses/search?q=${encodeURIComponent(query)}&limit=100`,
      );
      setSearchResults(response.data ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to search courses");
    } finally {
      setSearchingCourses(false);
    }
  }

  function updateCourseQuery(value: string) {
    setCourseQuery(value);
    if (!value.trim()) {
      setSearchResults([]);
      setError(null);
    }
  }

  async function refreshCourses() {
    const query = courseQuery.trim();
    if (query) {
      await searchCourses(query);
      return;
    }
    await loadCourses();
  }

  const displayedCourses = courseQuery.trim() ? searchResults : courses;
  const isLoadingList = loadingCourses || searchingCourses;

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <div className="mb-4 flex items-center gap-2">
          <BookOpen size={22} className="text-accent-green" />
          <div>
            <h2 className="text-xl font-semibold text-text-primary">Mock Exams</h2>
            <p className="text-sm text-text-secondary">
              Choose a course to open its dedicated mock exam page.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 lg:flex-row">
          <input
            type="text"
            value={courseQuery}
            onChange={(event) => updateCourseQuery(event.target.value)}
            placeholder="Search courses by code or title..."
            className="glass-input w-full px-4 py-2 text-sm"
          />
          <button
            type="button"
            onClick={() => void refreshCourses()}
            className="btn-secondary inline-flex items-center justify-center gap-2 px-4 py-2 text-sm"
          >
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>

        <div className="mt-4 space-y-1 text-sm text-text-secondary">
          <p>
            {courseQuery.trim()
              ? `Searching across ${totalCourses ?? "all"} courses.`
              : `Showing up to ${COURSE_PICKER_LIMIT} courses from ${
                  totalCourses ?? "the full"
                } course table.`}
          </p>
        </div>

        {isLoadingList ? (
          <div className="flex justify-center py-10">
            <LoaderCircle size={20} className="animate-spin text-text-secondary" />
          </div>
        ) : displayedCourses.length === 0 ? (
          <div className="rounded-2xl border border-border-primary bg-white/[0.03] px-4 py-8 text-center text-sm text-text-secondary">
            No courses match the current search.
          </div>
        ) : (
          <div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            {displayedCourses.map((course) => (
              <Link
                key={course.id}
                href={`/admin/mock-exams/${course.id}`}
                className="rounded-2xl border border-border-primary bg-white/[0.03] px-4 py-3 text-left transition-all duration-200 hover:border-accent-green/70 hover:bg-[#243111] hover:shadow-[0_0_0_1px_rgba(163,230,53,0.2)]"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-mono text-sm font-semibold text-accent-green">
                      {course.code} {course.level}
                    </p>
                    <p className="mt-1 text-sm text-text-primary">{course.title}</p>
                  </div>
                  <ArrowRight size={16} className="mt-0.5 text-text-secondary" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {error ? (
        <div className="rounded-2xl bg-accent-red-dim px-4 py-3 text-sm text-accent-red">
          {error}
        </div>
      ) : null}
    </div>
  );
}
