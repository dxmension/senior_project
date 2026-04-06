"use client";

import type { AnalyticsOverview, DatabaseStats } from "@/types";
import {
  TrendingUp,
  Users,
  BookOpen,
  Calendar,
  Briefcase,
} from "lucide-react";

interface AnalyticsProps {
  analytics: AnalyticsOverview | null;
  stats: DatabaseStats | null;
}

export function Analytics({ analytics, stats }: AnalyticsProps) {
  const usersByYear = analytics?.users_by_study_year || {};
  const usersByMajor = analytics?.users_by_major || {};

  const sortedYears = Object.entries(usersByYear).sort(([a], [b]) =>
    Number(a) > Number(b) ? 1 : -1
  );

  const sortedMajors = Object.entries(usersByMajor).sort(
    ([, a], [, b]) => b - a
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Users"
          value={analytics?.total_users}
          icon={<Users size={20} />}
          color="blue"
        />
        <MetricCard
          label="Active Users (30d)"
          value={analytics?.active_users_last_30_days}
          icon={<TrendingUp size={20} />}
          color="green"
        />
        <MetricCard
          label="Total Courses"
          value={analytics?.total_courses}
          icon={<BookOpen size={20} />}
          color="purple"
        />
        <MetricCard
          label="Course Offerings"
          value={analytics?.total_course_offerings}
          icon={<Calendar size={20} />}
          color="yellow"
        />
      </div>

      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
          <Users size={20} />
          Total Enrollments
        </h3>
        <div className="text-center py-6">
          <p className="text-5xl font-bold text-blue-400">
            {analytics?.total_enrollments || 0}
          </p>
          <p className="text-sm text-text-secondary mt-2">
            Historical course enrollments
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <Calendar size={20} />
            Users by Study Year
          </h3>
          <div className="space-y-3">
            {sortedYears.length > 0 ? (
              sortedYears.map(([year, count]) => (
                <div key={year} className="flex items-center gap-3">
                  <div className="w-24 text-sm text-text-secondary">
                    Year {year}
                  </div>
                  <div className="flex-1 bg-bg-card rounded-full h-8 overflow-hidden">
                    <div
                      className="bg-accent-green h-full flex items-center justify-end px-3"
                      style={{
                        width: `${
                          (count / Math.max(...Object.values(usersByYear))) *
                          100
                        }%`,
                      }}
                    >
                      <span className="text-xs font-semibold text-white">
                        {count}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-text-secondary text-center py-4">
                No data available
              </p>
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <Briefcase size={20} />
            Users by Major
          </h3>
          <div className="space-y-3 max-h-[300px] overflow-y-auto">
            {sortedMajors.length > 0 ? (
              sortedMajors.map(([major, count]) => (
                <div key={major} className="flex items-center gap-3">
                  <div className="w-32 text-sm text-text-secondary truncate">
                    {major}
                  </div>
                  <div className="flex-1 bg-bg-card rounded-full h-8 overflow-hidden">
                    <div
                      className="bg-blue-500 h-full flex items-center justify-end px-3"
                      style={{
                        width: `${
                          (count / Math.max(...Object.values(usersByMajor))) *
                          100
                        }%`,
                      }}
                    >
                      <span className="text-xs font-semibold text-white">
                        {count}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-text-secondary text-center py-4">
                No data available
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: number | undefined;
  icon: React.ReactNode;
  color: "blue" | "green" | "purple" | "yellow";
}) {
  const colorClasses = {
    blue: "text-blue-400 bg-blue-500/20",
    green: "text-green-400 bg-green-500/20",
    purple: "text-purple-400 bg-purple-500/20",
    yellow: "text-yellow-400 bg-yellow-500/20",
  };

  return (
    <div className="glass-card p-6">
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>{icon}</div>
        <span className="text-sm text-text-secondary">{label}</span>
      </div>
      <p className="text-3xl font-bold text-text-primary">
        {value !== undefined ? value.toLocaleString() : "—"}
      </p>
    </div>
  );
}
