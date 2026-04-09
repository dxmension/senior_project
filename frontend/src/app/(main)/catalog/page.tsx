"use client";

import { BookOpen, ChevronDown, Search, TrendingUp, Users } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type { ApiResponse, CatalogCourse } from "@/types";

const PAGE_SIZE = 30;

const TERMS = ["Fall", "Spring", "Summer"];

function gpaVariant(gpa: number): "green" | "orange" | "red" {
  if (gpa >= 3.0) return "green";
  if (gpa >= 2.0) return "orange";
  return "red";
}

function TermBadge({ term }: { term: string }) {
  const colors: Record<string, string> = {
    Fall: "bg-orange-500/15 text-orange-400 border border-orange-500/30",
    Spring: "bg-green-500/15 text-green-400 border border-green-500/30",
    Summer: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${colors[term] ?? "bg-bg-elevated text-text-muted border border-border-primary"}`}
    >
      {term}
    </span>
  );
}

function CourseCard({ course }: { course: CatalogCourse }) {
  return (
    <Link href={`/catalog/${course.id}`} className="glass-card p-4 flex flex-col gap-3 hover:border-border-light transition-colors block">
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

      {course.terms_available.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {course.terms_available.map((t) => (
            <TermBadge key={t} term={t} />
          ))}
        </div>
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
    </Link>
  );
}

interface Filters {
  query: string;
  term: string;
  academic_level: string;
  level_prefix: string;
}

export default function CatalogPage() {
  const [courses, setCourses] = useState<CatalogCourse[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<Filters>({ query: "", term: "", academic_level: "", level_prefix: "" });
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchCourses = useCallback(
    async (f: Filters, offset: number, replace: boolean) => {
      const params = new URLSearchParams({ skip: String(offset), limit: String(PAGE_SIZE) });
      if (f.query.trim()) params.set("q", f.query.trim());
      if (f.term) params.set("term", f.term);
      if (f.academic_level) params.set("academic_level", f.academic_level);
      if (f.level_prefix) params.set("level_prefix", f.level_prefix);

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
    },
    []
  );

  useEffect(() => {
    setIsLoading(true);
    setSkip(0);
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const delay = filters.query ? 300 : 0;
    debounceRef.current = setTimeout(async () => {
      await fetchCourses(filters, 0, true);
      setIsLoading(false);
    }, delay);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [filters, fetchCourses]);

  async function loadMore() {
    const nextSkip = skip + PAGE_SIZE;
    setIsLoadingMore(true);
    await fetchCourses(filters, nextSkip, false);
    setSkip(nextSkip);
    setIsLoadingMore(false);
  }

  function setFilter<K extends keyof Filters>(key: K, value: Filters[K]) {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  const hasMore = courses.length < total;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Header */}
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
            value={filters.query}
            onChange={(e) => setFilter("query", e.target.value)}
            className="w-full rounded-full bg-bg-card border border-border-primary
              pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted
              focus:outline-none focus:border-border-light"
          />
        </div>
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-xs text-text-muted">Filter:</span>

        {/* Term filter */}
        <div className="relative">
          <select
            value={filters.term}
            onChange={(e) => setFilter("term", e.target.value)}
            className="appearance-none rounded-full bg-bg-card border border-border-primary
              pl-3 pr-8 py-1.5 text-xs text-text-secondary
              focus:outline-none focus:border-border-light cursor-pointer"
          >
            <option value="">All terms</option>
            {TERMS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <ChevronDown
            size={12}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none"
          />
        </div>

        {/* Academic level filter */}
        <div className="relative">
          <select
            value={filters.academic_level}
            onChange={(e) => setFilter("academic_level", e.target.value)}
            className="appearance-none rounded-full bg-bg-card border border-border-primary
              pl-3 pr-8 py-1.5 text-xs text-text-secondary
              focus:outline-none focus:border-border-light cursor-pointer"
          >
            <option value="">All levels</option>
            <option value="Undergraduate">Undergraduate</option>
            <option value="Graduate">Graduate</option>
          </select>
          <ChevronDown
            size={12}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none"
          />
        </div>

        {/* Course level filter (100 / 200 / 300 / 400) */}
        <div className="relative">
          <select
            value={filters.level_prefix}
            onChange={(e) => setFilter("level_prefix", e.target.value)}
            className="appearance-none rounded-full bg-bg-card border border-border-primary
              pl-3 pr-8 py-1.5 text-xs text-text-secondary
              focus:outline-none focus:border-border-light cursor-pointer"
          >
            <option value="">All codes</option>
            <option value="1">100-level</option>
            <option value="2">200-level</option>
            <option value="3">300-level</option>
            <option value="4">400-level</option>
            <option value="5">500-level</option>
          </select>
          <ChevronDown
            size={12}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none"
          />
        </div>

        {(filters.term || filters.academic_level || filters.level_prefix) && (
          <button
            type="button"
            onClick={() => setFilters((prev) => ({ ...prev, term: "", academic_level: "", level_prefix: "" }))}
            className="text-xs text-text-muted hover:text-text-secondary transition-colors underline-offset-2 underline"
          >
            Clear filters
          </button>
        )}
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
            {filters.query || filters.term || filters.academic_level || filters.level_prefix
              ? "No courses match your filters."
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
