"use client";

import { GlassCard } from "@/components/ui/glass-card";
import { useAuthStore } from "@/stores/auth";

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Welcome back, {user?.first_name}
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          Here&apos;s your academic overview
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <GlassCard>
          <p className="mb-2 text-sm text-text-muted">Coming soon</p>
          <h3 className="text-lg font-semibold text-text-primary">
            GPA Trends
          </h3>
          <p className="mt-1 text-xs text-text-secondary">
            Track your academic performance over time
          </p>
        </GlassCard>

        <GlassCard>
          <p className="mb-2 text-sm text-text-muted">Coming soon</p>
          <h3 className="text-lg font-semibold text-text-primary">
            Upcoming Deadlines
          </h3>
          <p className="mt-1 text-xs text-text-secondary">
            Never miss an assignment or exam
          </p>
        </GlassCard>

        <GlassCard>
          <p className="mb-2 text-sm text-text-muted">Coming soon</p>
          <h3 className="text-lg font-semibold text-text-primary">
            AI Summary
          </h3>
          <p className="mt-1 text-xs text-text-secondary">
            Personalized study recommendations
          </p>
        </GlassCard>
      </div>
    </div>
  );
}
