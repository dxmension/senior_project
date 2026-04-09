"use client";

import {
  AlertTriangle,
  BookOpen,
  Brain,
  CheckCircle2,
  Clock,
  GraduationCap,
  RefreshCw,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type {
  AISummaryData,
  ApiResponse,
  DashboardData,
  UpcomingDeadlineItem,
  WeeklyWorkloadItem,
} from "@/types";

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatDeadline(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" }) +
    ", " +
    d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
}

function daysLabel(days: number): string {
  if (days === 0) return "today";
  if (days === 1) return "tomorrow";
  return `in ${days}d`;
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <GlassCard padding={false} className="p-5">
      <p className="text-xs text-text-secondary">{label}</p>
      <p
        className="mt-1 text-2xl font-bold"
        style={{ color: accent ?? "var(--text-primary)" }}
      >
        {value}
      </p>
      {sub && <p className="mt-0.5 text-xs text-text-secondary">{sub}</p>}
    </GlassCard>
  );
}

function ProgressBar({ pct }: { pct: number }) {
  return (
    <div className="h-1.5 w-full rounded-full" style={{ background: "#2a2a2a" }}>
      <div
        className="h-1.5 rounded-full transition-all"
        style={{ width: `${Math.min(100, pct)}%`, background: "#a3e635" }}
      />
    </div>
  );
}

function DeadlinesList({ items }: { items: UpcomingDeadlineItem[] }) {
  if (items.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-text-secondary">
        No upcoming deadlines 🎉
      </p>
    );
  }
  return (
    <ul className="divide-y divide-[#1e1e1e]">
      {items.map((item) => (
        <li key={item.assessment_id} className="flex items-start justify-between gap-3 py-3">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-text-primary">
              {item.title}
            </p>
            <p className="mt-0.5 text-xs text-text-secondary">
              {item.course_code} · {formatDeadline(item.deadline)}
            </p>
          </div>
          <span
            className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
              item.days_until === 0
                ? "bg-red-950/60 text-red-400"
                : item.days_until <= 2
                ? "bg-orange-950/60 text-orange-400"
                : "bg-[#1e2a1e] text-accent-green"
            }`}
          >
            {daysLabel(item.days_until)}
          </span>
        </li>
      ))}
    </ul>
  );
}

function WorkloadWeek({ week }: { week: WeeklyWorkloadItem }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-xl border border-[#2a2a2a] bg-white/[0.02]">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <div>
          <p className="text-sm font-medium text-text-primary">
            {week.week_label}
          </p>
          <p className="text-xs text-text-secondary">
            {week.assessment_count} assessment{week.assessment_count !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {week.assessment_count > 0 && (
            <span className="rounded-full bg-accent-green/10 px-2 py-0.5 text-xs font-semibold text-accent-green">
              {week.assessment_count}
            </span>
          )}
          <span className="text-xs text-text-secondary">{open ? "▲" : "▼"}</span>
        </div>
      </button>
      {open && week.assessments.length > 0 && (
        <ul className="border-t border-[#2a2a2a] px-4 pb-3">
          {week.assessments.map((a) => (
            <li
              key={a.assessment_id}
              className="flex items-center justify-between gap-2 pt-2 text-xs"
            >
              <span
                className={`flex-1 truncate ${
                  a.is_completed ? "text-text-secondary line-through" : "text-text-primary"
                }`}
              >
                {a.title}
              </span>
              <span className="text-text-secondary">{a.course_code}</span>
              <span className="text-text-secondary">{formatDeadline(a.deadline)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AISummaryCard() {
  const [data, setData] = useState<AISummaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<ApiResponse<AISummaryData>>("/dashboard/ai-summary");
      setData(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate summary.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <GlassCard padding={false} className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#2a2a2a] px-5 py-4">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-accent-green" />
          <h2 className="text-sm font-semibold text-text-primary">AI Academic Summary</h2>
        </div>
        <button
          type="button"
          onClick={generate}
          disabled={loading}
          className="inline-flex items-center gap-1.5 rounded-lg bg-accent-green/10 px-3 py-1.5 text-xs font-medium text-accent-green transition-colors hover:bg-accent-green/20 disabled:opacity-50"
        >
          {loading ? (
            <RefreshCw size={12} className="animate-spin" />
          ) : (
            <Brain size={12} />
          )}
          {data ? "Regenerate" : "Generate"}
        </button>
      </div>

      <div className="px-5 py-4">
        {loading && (
          <div className="flex justify-center py-6">
            <Spinner text="Generating your academic summary..." />
          </div>
        )}
        {error && (
          <p className="text-sm text-accent-red">{error}</p>
        )}
        {!loading && !error && !data && (
          <p className="text-sm text-text-secondary">
            Click &ldquo;Generate&rdquo; to get a personalized AI summary of your academic progress and recommendations.
          </p>
        )}
        {!loading && data && (
          <div className="space-y-4">
            <p className="text-sm leading-relaxed text-text-primary">{data.summary}</p>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-secondary">
                Recommendations
              </p>
              <ul className="space-y-1.5">
                {data.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-primary">
                    <CheckCircle2 size={14} className="mt-0.5 shrink-0 text-accent-green" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
            <p className="rounded-lg bg-accent-green/5 px-3 py-2 text-sm italic text-accent-green">
              {data.motivation}
            </p>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

// ─── Main page ───────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get<ApiResponse<DashboardData>>("/dashboard");
        setData(res.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard.");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Welcome back, {user?.first_name}
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          Here&apos;s your academic overview
        </p>
      </div>

      {loading && (
        <div className="flex justify-center py-16">
          <Spinner text="Loading dashboard..." />
        </div>
      )}

      {error && (
        <p className="text-sm text-accent-red">{error}</p>
      )}

      {data && (
        <>
          {/* Stats row */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard
              label="Current GPA"
              value={data.current_gpa != null ? data.current_gpa.toFixed(2) : "—"}
              sub="All time"
              accent="#a3e635"
            />
            <StatCard
              label="Semester GPA"
              value={data.semester_gpa != null ? data.semester_gpa.toFixed(2) : "—"}
              sub="This term"
            />
            <StatCard
              label="Credits Earned"
              value={data.total_credits_earned}
              sub={`${data.total_credits_enrolled} enrolled`}
            />
            <StatCard
              label="Active Courses"
              value={data.active_courses_count}
              sub={`${data.completed_courses_count} completed`}
            />
          </div>

          {/* Alert row */}
          {(data.overdue_count > 0 || data.upcoming_deadlines_count > 0) && (
            <div className="flex flex-wrap gap-3">
              {data.overdue_count > 0 && (
                <div className="flex items-center gap-2 rounded-lg bg-red-950/40 px-4 py-2.5 text-sm text-red-400">
                  <AlertTriangle size={14} />
                  <span>
                    {data.overdue_count} overdue{" "}
                    {data.overdue_count === 1 ? "assessment" : "assessments"}
                  </span>
                </div>
              )}
              {data.upcoming_deadlines_count > 0 && (
                <div className="flex items-center gap-2 rounded-lg bg-orange-950/40 px-4 py-2.5 text-sm text-orange-400">
                  <Clock size={14} />
                  <span>
                    {data.upcoming_deadlines_count} due in the next 7 days
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Main grid */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            {/* Left col — course progress + upcoming */}
            <div className="space-y-4 lg:col-span-2">
              {/* Course progress */}
              <GlassCard padding={false} className="overflow-hidden">
                <div className="flex items-center gap-2 border-b border-[#2a2a2a] px-5 py-4">
                  <BookOpen size={15} className="text-accent-green" />
                  <h2 className="text-sm font-semibold text-text-primary">
                    Course Progress
                  </h2>
                </div>
                {data.course_progress.length === 0 ? (
                  <p className="px-5 py-6 text-sm text-text-secondary">
                    No active courses this semester.
                  </p>
                ) : (
                  <ul className="divide-y divide-[#1e1e1e]">
                    {data.course_progress.map((c) => (
                      <li key={c.course_id} className="px-5 py-3">
                        <div className="mb-1.5 flex items-center justify-between gap-2">
                          <div className="min-w-0">
                            <span className="font-mono text-xs font-semibold text-accent-green">
                              {c.course_code}
                            </span>
                            <span className="ml-2 truncate text-xs text-text-secondary">
                              {c.course_title}
                            </span>
                          </div>
                          <span className="shrink-0 text-xs text-text-secondary">
                            {c.completed_assessments}/{c.total_assessments}
                          </span>
                        </div>
                        <ProgressBar pct={c.progress_pct} />
                        {c.upcoming_deadline && (
                          <p className="mt-1 text-xs text-text-secondary">
                            Next: {formatDeadline(c.upcoming_deadline)}
                          </p>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </GlassCard>

              {/* Weekly workload */}
              <GlassCard padding={false} className="overflow-hidden">
                <div className="flex items-center gap-2 border-b border-[#2a2a2a] px-5 py-4">
                  <TrendingUp size={15} className="text-accent-green" />
                  <h2 className="text-sm font-semibold text-text-primary">
                    Weekly Workload
                  </h2>
                </div>
                <div className="space-y-2 p-4">
                  {data.weekly_workload.map((week) => (
                    <WorkloadWeek key={week.week_start} week={week} />
                  ))}
                </div>
              </GlassCard>
            </div>

            {/* Right col — upcoming deadlines + AI */}
            <div className="space-y-4">
              {/* Upcoming deadlines */}
              <GlassCard padding={false} className="overflow-hidden">
                <div className="flex items-center gap-2 border-b border-[#2a2a2a] px-5 py-4">
                  <GraduationCap size={15} className="text-accent-green" />
                  <h2 className="text-sm font-semibold text-text-primary">
                    Upcoming Deadlines
                  </h2>
                </div>
                <div className="px-5 py-2">
                  <DeadlinesList items={data.upcoming_deadlines} />
                </div>
              </GlassCard>

              {/* AI Summary */}
              <AISummaryCard />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
