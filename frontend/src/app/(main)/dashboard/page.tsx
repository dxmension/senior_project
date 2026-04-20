"use client";

import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  Clock,
  FileText,
  FlaskConical,
  FolderOpen,
  GraduationCap,
  HelpCircle,
  Loader2,
  MoreHorizontal,
  Presentation,
  TrendingUp,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/navigation";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type {
  ApiResponse,
  CourseProgressItem,
  DashboardData,
  DeadlineDotItem,
  UpcomingDeadlineItem,
  WeeklyWorkloadItem,
} from "@/types";

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatDeadline(iso: string): string {
  const d = new Date(iso);
  return (
    d.toLocaleDateString("en-US", { month: "short", day: "numeric" }) +
    ", " +
    d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
  );
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
    <GlassCard padding={false} className="flex flex-col justify-between p-5">
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
        <li
          key={item.assessment_id}
          className="flex items-start justify-between gap-3 py-3"
        >
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
            {week.assessment_count} assessment
            {week.assessment_count !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {week.assessment_count > 0 && (
            <span className="rounded-full bg-accent-green/10 px-2 py-0.5 text-xs font-semibold text-accent-green">
              {week.assessment_count}
            </span>
          )}
          <span className="text-xs text-text-secondary">
            {open ? "▲" : "▼"}
          </span>
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
                  a.is_completed
                    ? "text-text-secondary line-through"
                    : "text-text-primary"
                }`}
              >
                {a.title}
              </span>
              <span className="text-text-secondary">{a.course_code}</span>
              <span className="text-text-secondary">
                {formatDeadline(a.deadline)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Assessment types that open the study session
const STUDY_TYPES = new Set(["quiz", "midterm", "final", "presentation"]);

const TYPE_ICONS: Record<string, React.ReactNode> = {
  midterm: <BookOpen size={13} />,
  final: <GraduationCap size={13} />,
  quiz: <HelpCircle size={13} />,
  presentation: <Presentation size={13} />,
  homework: <FileText size={13} />,
  lab: <FlaskConical size={13} />,
  project: <FolderOpen size={13} />,
  other: <MoreHorizontal size={13} />,
};

// Popover shown for past study-type assessments (midterm/quiz/final/presentation)
function GoodJobPopover({
  dot,
  courseId,
  position,
  onClose,
}: {
  dot: DeadlineDotItem;
  courseId: number;
  position: { x: number; y: number };
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    const t = setTimeout(() => document.addEventListener("mousedown", handler), 50);
    return () => { clearTimeout(t); document.removeEventListener("mousedown", handler); };
  }, [onClose]);

  const POPOVER_WIDTH = 220;
  const style: React.CSSProperties = {
    position: "fixed",
    left: Math.min(Math.max(position.x - POPOVER_WIDTH / 2, 8), window.innerWidth - POPOVER_WIDTH - 8),
    top: position.y - 8,
    transform: "translateY(-100%)",
    width: POPOVER_WIDTH,
    zIndex: 9999,
    background: "rgba(20,20,20,0.98)",
    border: "1px solid rgba(163,230,53,0.15)",
    borderRadius: 12,
    boxShadow: "0 20px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(163,230,53,0.06)",
  };

  return createPortal(
    <div ref={ref} style={style}>
      <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 h-3 w-3 rotate-45"
        style={{ background: "rgba(20,20,20,0.98)", borderRight: "1px solid rgba(163,230,53,0.15)", borderBottom: "1px solid rgba(163,230,53,0.15)" }} />
      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className="text-base">🎉</span>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary transition-colors">
            <X size={13} />
          </button>
        </div>
        <p className="text-sm font-semibold text-text-primary mb-1">Good job!</p>
        <p className="text-[11px] text-text-secondary leading-relaxed mb-3">
          Once grades are released, fill in your score so we can track your GPA.
        </p>
        <button
          onClick={() => { onClose(); router.push(`/courses/${courseId}`); }}
          className="w-full flex items-center justify-center gap-1.5 text-xs font-semibold py-2 px-3 rounded-lg transition-all"
          style={{ background: "#a3e635", color: "#0d0d0d" }}
        >
          Fill score
        </button>
      </div>
    </div>,
    document.body
  );
}

// Portal popover — renders at body level to escape overflow:hidden cards
function CompletionPopover({
  dot,
  position,
  onClose,
  onToggled,
}: {
  dot: DeadlineDotItem;
  position: { x: number; y: number };
  onClose: () => void;
  onToggled: (assessmentId: number, completed: boolean) => void;
}) {
  const [saving, setSaving] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    // Slight delay so the opening click doesn't immediately close it
    const t = setTimeout(() => document.addEventListener("mousedown", handler), 50);
    return () => { clearTimeout(t); document.removeEventListener("mousedown", handler); };
  }, [onClose]);

  async function handleToggle() {
    setSaving(true);
    try {
      const newState = !dot.is_completed;
      await api.patch(`/assessments/${dot.assessment_id}`, { is_completed: newState });
      onToggled(dot.assessment_id, newState);
      onClose();
    } catch {
      // silently ignore
    } finally {
      setSaving(false);
    }
  }

  const typeLabel = dot.assessment_type.charAt(0).toUpperCase() + dot.assessment_type.slice(1);
  const POPOVER_WIDTH = 224;

  const style: React.CSSProperties = {
    position: "fixed",
    // Center horizontally on the dot, clamp so it doesn't go off screen
    left: Math.min(
      Math.max(position.x - POPOVER_WIDTH / 2, 8),
      window.innerWidth - POPOVER_WIDTH - 8
    ),
    // Place above the dot with a small gap
    top: position.y - 8,
    transform: "translateY(-100%)",
    width: POPOVER_WIDTH,
    zIndex: 9999,
    background: "rgba(20,20,20,0.98)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 12,
    boxShadow: "0 20px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(163,230,53,0.06)",
  };

  return createPortal(
    <div ref={ref} style={style}>
      {/* Arrow pointing down */}
      <div
        className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 h-3 w-3 rotate-45"
        style={{
          background: "rgba(20,20,20,0.98)",
          borderRight: "1px solid rgba(255,255,255,0.1)",
          borderBottom: "1px solid rgba(255,255,255,0.1)",
        }}
      />

      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-text-muted flex-shrink-0">
              {TYPE_ICONS[dot.assessment_type] ?? <MoreHorizontal size={13} />}
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">
              {typeLabel}
            </span>
          </div>
          <button onClick={onClose} className="flex-shrink-0 text-text-muted hover:text-text-primary transition-colors">
            <X size={13} />
          </button>
        </div>

        <p className="text-sm font-semibold text-text-primary leading-snug mb-0.5">{dot.title}</p>
        <p className="text-[11px] text-text-muted mb-3">Due {formatDeadline(dot.deadline)}</p>

        {dot.is_completed ? (
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-xs text-accent-green font-medium">
              <CheckCircle2 size={13} /> Marked as done
            </div>
            <button
              onClick={handleToggle}
              disabled={saving}
              className="w-full text-xs py-1.5 px-3 rounded-lg text-text-secondary border transition-colors hover:text-text-primary"
              style={{ borderColor: "rgba(255,255,255,0.08)", background: "transparent" }}
            >
              {saving ? "Updating..." : "Undo — mark as not done"}
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-[11px] text-text-secondary">Have you finished this task?</p>
            <button
              onClick={handleToggle}
              disabled={saving}
              className="w-full flex items-center justify-center gap-1.5 text-xs font-semibold py-2 px-3 rounded-lg transition-all disabled:opacity-60"
              style={{ background: "#a3e635", color: "#0d0d0d" }}
            >
              {saving
                ? <><Loader2 size={12} className="animate-spin" /> Saving…</>
                : <><CheckCircle2 size={12} /> Yes, mark as done</>}
            </button>
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}

function DeadlineDot({
  dot,
  now,
  courseId,
  onToggled,
}: {
  dot: DeadlineDotItem;
  now: Date;
  courseId: number;
  onToggled: (assessmentId: number, completed: boolean) => void;
}) {
  const router = useRouter();
  const [popoverPos, setPopoverPos] = useState<{ x: number; y: number } | null>(null);
  const [goodJobPos, setGoodJobPos] = useState<{ x: number; y: number } | null>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const isStudy = STUDY_TYPES.has(dot.assessment_type);
  const isPastDeadline = new Date(dot.deadline) < now;
  const isOverdue = !dot.is_completed && new Date(dot.deadline) < now;
  const tooltip = `${dot.title} · ${formatDeadline(dot.deadline)}`;

  let dotClass =
    "relative flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-transform hover:scale-125 cursor-pointer";
  if (dot.is_completed) {
    dotClass += " border-accent-green bg-accent-green";
  } else if (isOverdue) {
    dotClass += " border-red-400 bg-transparent";
  } else {
    dotClass += " border-accent-green bg-transparent";
  }

  function getPos() {
    const rect = btnRef.current?.getBoundingClientRect();
    return rect ? { x: rect.left + rect.width / 2, y: rect.top } : null;
  }

  function handleClick() {
    if (isStudy && !isPastDeadline) {
      // Future study assessment → go to study session
      router.push(`/study/${courseId}`);
    } else if (isStudy && isPastDeadline) {
      // Past study assessment → "good job, fill score" popover
      setGoodJobPos((v) => (v ? null : getPos()));
    } else {
      // Assignment type → completion popover
      setPopoverPos((v) => (v ? null : getPos()));
    }
  }

  return (
    <div className="relative">
      <button ref={btnRef} type="button" className={dotClass} title={tooltip} onClick={handleClick}>
        {dot.is_completed && (
          <svg className="h-2.5 w-2.5 text-bg-primary" fill="none" viewBox="0 0 10 8">
            <path d="M1 4l3 3 5-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
        {!dot.is_completed && isOverdue && (
          <span className="text-[8px] font-bold leading-none text-red-400">!</span>
        )}
      </button>

      {popoverPos && !isStudy && (
        <CompletionPopover
          dot={dot}
          position={popoverPos}
          onClose={() => setPopoverPos(null)}
          onToggled={(id, completed) => { onToggled(id, completed); setPopoverPos(null); }}
        />
      )}

      {goodJobPos && isStudy && isPastDeadline && (
        <GoodJobPopover
          dot={dot}
          courseId={courseId}
          position={goodJobPos}
          onClose={() => setGoodJobPos(null)}
        />
      )}
    </div>
  );
}

function CourseRoadmapRow({
  course,
  now,
}: {
  course: CourseProgressItem;
  now: Date;
}) {
  const router = useRouter();
  // Local dot state for optimistic completion toggling
  const [dots, setDots] = useState(course.deadline_dots);

  function handleToggled(assessmentId: number, completed: boolean) {
    setDots((prev) =>
      prev.map((d) =>
        d.assessment_id === assessmentId ? { ...d, is_completed: completed } : d
      )
    );
  }

  return (
    <li className="px-5 py-4">
      <button
        type="button"
        onClick={() => router.push(`/courses/${course.course_id}`)}
        className="mb-3 flex items-baseline gap-2 hover:opacity-80 transition-opacity"
      >
        <span className="font-mono text-xs font-semibold text-accent-green">
          {course.course_code}
        </span>
        <span className="truncate text-xs text-text-secondary">
          {course.course_title}
        </span>
      </button>

      {dots.length === 0 ? (
        <p className="text-xs text-text-secondary">No deadlines</p>
      ) : (
        <div className="overflow-x-auto pb-2">
          <div className="flex min-w-max items-center pb-4 pl-6 pr-4">
            {dots.map((dot, idx) => (
              <div key={dot.assessment_id} className="flex items-center">
                {/* Circle + label pinned absolutely below — label never affects circle height */}
                <div className="relative">
                  <DeadlineDot
                    dot={dot}
                    now={now}
                    courseId={course.course_id}
                    onToggled={handleToggled}
                  />
                  <span className="absolute left-1/2 top-full mt-1 -translate-x-1/2 whitespace-nowrap text-center text-[10px] leading-tight text-text-secondary">
                    {dot.assessment_type.charAt(0).toUpperCase() + dot.assessment_type.slice(1)}
                  </span>
                </div>
                {idx < dots.length - 1 && (
                  <div className="mx-1 h-px w-8 shrink-0 bg-[#3a3a3a]" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </li>
  );
}

// ─── Main page ───────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const now = new Date();

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get<ApiResponse<DashboardData>>("/dashboard");
        setData(res.data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load dashboard."
        );
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

      {error && <p className="text-sm text-accent-red">{error}</p>}

      {data && (
        <>
          {/* Stats row — 3 cards */}
          <div className="grid grid-cols-3 items-stretch gap-3">
            <StatCard
              label="Current GPA"
              value={
                data.current_gpa != null ? data.current_gpa.toFixed(2) : "—"
              }
              sub="All time"
              accent="#a3e635"
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
            {/* Left col — course roadmap + weekly workload */}
            <div className="space-y-4 lg:col-span-2">
              {/* Course roadmap */}
              <GlassCard padding={false} className="overflow-hidden">
                <div className="flex items-center gap-2 border-b border-[#2a2a2a] px-5 py-4">
                  <BookOpen size={15} className="text-accent-green" />
                  <h2 className="text-sm font-semibold text-text-primary">
                    Course Deadlines
                  </h2>
                </div>
                {data.course_progress.length === 0 ? (
                  <p className="px-5 py-6 text-sm text-text-secondary">
                    No active courses this semester.
                  </p>
                ) : (
                  <ul className="divide-y divide-[#1e1e1e]">
                    {data.course_progress.map((c) => (
                      <CourseRoadmapRow key={c.course_id} course={c} now={now} />
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

            {/* Right col — upcoming deadlines */}
            <div className="flex flex-col gap-4">
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
            </div>
          </div>
        </>
      )}
    </div>
  );
}
