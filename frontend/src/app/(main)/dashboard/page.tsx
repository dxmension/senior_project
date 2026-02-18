"use client";

import { useAuthStore } from "@/stores/auth";
import { GlassCard } from "@/components/ui/glass-card";

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Welcome back, {user?.first_name}
        </h1>
        <p className="text-sm text-text-secondary mt-1">
          Here&apos;s your academic overview
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <GlassCard>
          <p className="text-sm text-text-muted mb-2">Coming soon</p>
          <h3 className="text-lg font-semibold text-text-primary">
            GPA Trends
          </h3>
          <p className="text-xs text-text-secondary mt-1">
            Track your academic performance over time
          </p>
        </GlassCard>

        <GlassCard>
          <p className="text-sm text-text-muted mb-2">Coming soon</p>
          <h3 className="text-lg font-semibold text-text-primary">
            Upcoming Deadlines
          </h3>
          <p className="text-xs text-text-secondary mt-1">
            Never miss an assignment or exam
          </p>
        </GlassCard>

        <GlassCard>
          <p className="text-sm text-text-muted mb-2">Coming soon</p>
          <h3 className="text-lg font-semibold text-text-primary">
            AI Summary
          </h3>
          <p className="text-xs text-text-secondary mt-1">
            Personalized study recommendations
          </p>
        </GlassCard>
      </div>
    </div>
  );
}
