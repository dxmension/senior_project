"use client";

import { BookOpen, Search, TrendingUp, Users } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type { ApiResponse, CatalogCourse } from "@/types";

const PAGE_SIZE = 30;

function gpaVariant(gpa: number): "green" | "orange" | "red" {
  if (gpa >= 3.0) return "green";
  if (gpa >= 2.0) return "orange";
  return "red";
}

function CourseCard({ course }: { course: CatalogCourse }) {
  return (
    <div className="glass-card p-4 flex flex-col gap-3 hover:border-border-light transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono font-semibold text-accent-green">
              {course.code} {course.level}
            </span>
            {course.academic_level && (
              <Badge variant="muted">{course.academic_level}</Badge>
            )}
          </div>
          <p className="mt-1 text-sm font-semibold text-text-primary leading-snug line-clamp-2">
            {course.title}
          </p>
        </div>
        <span className="text-xs text-text-muted whitespace-nowrap shrink-0">
          {course.ects} ECTS
        </span>
      </div>

      {course.department && (
        <p className="text-xs text-text-secondary truncate">{course.department}</p>
      )}

      <div className="flex items-center gap-3 mt-auto pt-2 border-t border-border-primary">
        {course.avg_gpa != null ? (
          <div className="flex items-center gap-1.5">
            <TrendingUp size={12} className="text-text-muted" />
            <Badge variant={gpaVariant(course.avg_gpa)}>
              {course.avg_gpa.toFixed(2)} GPA
            </Badge>
          </div>
        ) : (
          <span className="text-xs text-text-muted italic">No GPA data</span>
        )}

        {course.total_enrolled != null && (
          <div className="flex items-center gap-1.5 ml-auto">
            <Users size={12} className="text-text-muted" />
            <span className="text-xs text-text-secondary">{course.total_enrolled}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function CatalogPage() {
  const [courses, setCourses] = useState<CatalogCourse[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchCourses = useCallback(async (q: string, offset: number, replace: boolean) => {
    const params = new URLSearchParams({ skip: String(offset), limit: String(PAGE_SIZE) });
    if (q.trim()) params.set("q", q.trim());

    try {
      const res = await api.get<ApiResponse<CatalogCourse[]>>(
        `/courses/catalog?${params.toString()}`
      );
      const newTotal = Number((res.meta as Record<string, unknown>)?.total ?? 0);
      setCourses((prev) => (replace ? res.data : [...prev, ...res.data]));
      setTotal(newTotal);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load courses.");
    }
  }, []);

  useEffect(() => {
    setIsLoading(true);
    setSkip(0);
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      await fetchCourses(query, 0, true);
      setIsLoading(false);
    }, query ? 300 : 0);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, fetchCourses]);

  async function loadMore() {
    const nextSkip = skip + PAGE_SIZE;
    setIsLoadingMore(true);
    await fetchCourses(query, nextSkip, false);
    setSkip(nextSkip);
    setIsLoadingMore(false);
  }

  const hasMore = courses.length < total;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Course Catalog</h1>
          <p className="mt-1 text-sm text-text-secondary">
            {total > 0 ? `${total} courses available` : "Browse NU courses"}
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none"
          />
          <input
            type="text"
            placeholder="Search by code or title…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-full bg-bg-card border border-border-primary
              pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted
              focus:outline-none focus:border-border-light"
          />
        </div>
      </div>

      {error && <p className="text-sm text-accent-red">{error}</p>}

      {isLoading ? (
        <GlassCard className="flex items-center justify-center py-16">
          <Spinner />
        </GlassCard>
      ) : courses.length === 0 ? (
        <GlassCard className="flex flex-col items-center py-16">
          <BookOpen size={40} className="text-text-muted mb-4" />
          <p className="text-sm text-text-secondary">
            {query
              ? "No courses match your search."
              : "No courses found. Upload a schedule PDF first."}
          </p>
        </GlassCard>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>

          {hasMore && (
            <div className="flex justify-center pt-2">
              <button
                type="button"
                onClick={loadMore}
                disabled={isLoadingMore}
                className="inline-flex items-center gap-2 rounded-full border border-border-primary
                  px-5 py-2 text-sm text-text-secondary hover:text-text-primary hover:border-border-light
                  transition-colors disabled:opacity-50"
              >
                {isLoadingMore ? <Spinner /> : null}
                {isLoadingMore
                  ? "Loading…"
                  : `Load more (${total - courses.length} remaining)`}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
