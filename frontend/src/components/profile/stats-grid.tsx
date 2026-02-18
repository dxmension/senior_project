"use client";

import { TrendingUp, BookOpen, GraduationCap, Calendar } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import type { UserStats } from "@/types";

interface StatsGridProps {
  stats: UserStats;
}

const cards = [
  {
    key: "gpa" as const,
    label: "Current GPA",
    icon: TrendingUp,
    color: "text-accent-green",
    bg: "bg-accent-green-dim",
    getValue: (s: UserStats) => s.current_gpa?.toFixed(2) ?? "N/A",
  },
  {
    key: "courses" as const,
    label: "Courses Passed",
    icon: BookOpen,
    color: "text-accent-orange",
    bg: "bg-accent-orange-dim",
    getValue: (s: UserStats) => String(s.completed_courses),
  },
  {
    key: "credits" as const,
    label: "Total Credits",
    icon: GraduationCap,
    color: "text-accent-blue",
    bg: "bg-accent-blue-dim",
    getValue: (s: UserStats) => String(s.total_credits),
  },
  {
    key: "semesters" as const,
    label: "Semesters",
    icon: Calendar,
    color: "text-accent-orange",
    bg: "bg-accent-orange-dim",
    getValue: (s: UserStats) => String(s.semesters_completed),
  },
];

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <GlassCard key={card.key}>
          <div className="flex items-start gap-3">
            <div
              className={`w-10 h-10 rounded-xl ${card.bg} flex items-center justify-center shrink-0`}
            >
              <card.icon size={20} className={card.color} />
            </div>
            <div>
              <p className="text-2xl font-bold text-text-primary">
                {card.getValue(stats)}
              </p>
              <p className="text-xs text-text-muted mt-0.5">{card.label}</p>
            </div>
          </div>
        </GlassCard>
      ))}
    </div>
  );
}
