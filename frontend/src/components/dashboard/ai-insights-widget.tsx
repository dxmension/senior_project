"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import type { InsightsData } from "@/types";

type Props = {
  data: InsightsData | null;
  loading: boolean;
};

export function AiInsightsWidget({ data, loading }: Props) {
  if (!loading && !data) return null;

  return (
    <GlassCard padding={false} className="overflow-hidden">
      <div className="flex items-center gap-2 border-b border-[#2a2a2a] px-5 py-4">
        <Sparkles size={15} className="text-accent-green" />
        <h2 className="text-sm font-semibold text-text-primary">
          AI Insights
        </h2>
      </div>
      <div className="px-5 py-4">
        {loading ? <WidgetSkeleton /> : <WidgetBody data={data} />}
      </div>
    </GlassCard>
  );
}

function WidgetBody({ data }: { data: InsightsData | null }) {
  if (!data) return null;

  return (
    <div className="space-y-3">
      <p className="text-sm leading-6 text-text-secondary">
        {data.short_summary}
      </p>
      <Link
        href="/study"
        className="inline-flex text-sm font-medium text-accent-green hover:opacity-80"
      >
        View full recommendations →
      </Link>
    </div>
  );
}

function WidgetSkeleton() {
  return (
    <div className="animate-pulse space-y-2">
      <div className="h-4 rounded bg-white/10" />
      <div className="h-4 w-5/6 rounded bg-white/10" />
    </div>
  );
}
