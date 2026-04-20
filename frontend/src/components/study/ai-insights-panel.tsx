"use client";

import { useRouter } from "next/navigation";
import {
  ArrowRight,
  BookOpen,
  Brain,
  HelpCircle,
  Layers,
  Map,
} from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import type { InsightAction, InsightsData } from "@/types";

type Props = {
  data: InsightsData | null;
  loading: boolean;
  error: string | null;
};

const ACTION_ICONS = {
  take_mock: Brain,
  start_flashcards: Layers,
  view_mindmap: Map,
  take_quiz: HelpCircle,
  take_midterm: BookOpen,
} as const;

export function AiInsightsPanel({ data, loading, error }: Props) {
  if (loading) return <InsightsPanelSkeleton />;
  if (error || !data) return <InsightsPanelEmpty />;
  const validActions = data.actions.filter(hasRenderableStudyRoute);

  const paragraphs = data.long_summary
    .split("\n\n")
    .map((item) => item.trim())
    .filter(Boolean);

  return (
    <GlassCard className="min-h-[420px] p-8">
      <div className="space-y-6">
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent-green">
            AI Recommendations
          </p>
          <div className="space-y-3">
            {paragraphs.map((item) => (
              <p key={item} className="text-sm leading-6 text-text-secondary">
                {item}
              </p>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          {validActions.map((action) => (
            <ActionCard key={`${action.action_type}:${action.action_url}`} action={action} />
          ))}
        </div>

        <p className="text-[11px] text-text-muted">
          Generated {relativeTimeLabel(data.generated_at)}
          {data.cached ? " · cached" : ""}
        </p>
      </div>
    </GlassCard>
  );
}

function InsightsPanelEmpty() {
  return (
    <GlassCard className="min-h-[420px] p-8">
      <div className="space-y-4">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent-green">
          AI Recommendations
        </p>
        <p className="max-w-xl text-sm leading-6 text-text-secondary">
          Recommendations will appear here once your latest study signals are ready.
        </p>
      </div>
    </GlassCard>
  );
}

function ActionCard({ action }: { action: InsightAction }) {
  const router = useRouter();
  const Icon = ACTION_ICONS[action.action_type];

  return (
    <button
      type="button"
      onClick={() => router.push(action.action_url)}
      className="group flex w-full items-start gap-3 rounded-2xl border border-border-primary
        bg-white/[0.03] px-4 py-4 text-left transition-all
        hover:border-accent-green/40 hover:bg-accent-green/5"
    >
      <div className="mt-0.5 rounded-xl border border-border-primary bg-white/[0.04] p-2">
        <Icon size={16} className="text-accent-green" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-text-primary">{action.label}</p>
        <p className="mt-1 text-sm leading-6 text-text-secondary">
          {action.description}
        </p>
      </div>
      <ArrowRight
        size={16}
        className="mt-1 shrink-0 text-text-secondary transition-transform group-hover:translate-x-0.5"
      />
    </button>
  );
}

function InsightsPanelSkeleton() {
  return (
    <GlassCard className="min-h-[420px] p-8">
      <div className="animate-pulse space-y-4">
        <div className="h-3 w-40 rounded bg-white/10" />
        <div className="space-y-2">
          <div className="h-4 rounded bg-white/10" />
          <div className="h-4 w-11/12 rounded bg-white/10" />
          <div className="h-4 w-10/12 rounded bg-white/10" />
          <div className="h-4 w-9/12 rounded bg-white/10" />
        </div>
        <div className="space-y-3 pt-2">
          <div className="h-24 rounded-2xl bg-white/10" />
          <div className="h-24 rounded-2xl bg-white/10" />
          <div className="h-24 rounded-2xl bg-white/10" />
        </div>
        <div className="h-3 w-32 rounded bg-white/10" />
      </div>
    </GlassCard>
  );
}

function relativeTimeLabel(value: string) {
  const date = new Date(value);
  const seconds = Math.max(1, Math.floor((Date.now() - date.getTime()) / 1000));
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function hasRenderableStudyRoute(action: InsightAction) {
  try {
    const url = new URL(action.action_url, "http://local.test");
    const parts = url.pathname.split("/").filter(Boolean);
    if (parts[0] !== "study") return false;

    if (
      parts.length === 2 &&
      /^\d+$/.test(parts[1]) &&
      !url.search
    ) {
      return true;
    }

    if (
      parts.length === 2 &&
      /^\d+$/.test(parts[1]) &&
      (url.searchParams.get("tab") === "flashcards" ||
        url.searchParams.get("tab") === "mindmaps")
    ) {
      return true;
    }

    if (parts.length !== 4) return false;
    if (!/^\d+$/.test(parts[1]) || !/^\d+$/.test(parts[3])) return false;

    return parts[2] === "quiz" || parts[2] === "midterm";
  } catch {
    return false;
  }
}
