"use client";

import type { DatabaseStats, DatabaseHealth } from "@/types";
import { Database, HardDrive, CheckCircle, XCircle, Users, BookOpen, FileText } from "lucide-react";

interface DatabaseManagementProps {
  stats: DatabaseStats | null;
  health: DatabaseHealth | null;
}

export function DatabaseManagement({
  stats,
  health,
}: DatabaseManagementProps) {
  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold text-text-primary mb-6 flex items-center gap-2">
          <Database size={24} />
          Database Health
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <HealthCard
            label="Database Connection"
            status={health?.database_connected}
          />
          <HealthCard
            label="Redis Connection"
            status={health?.redis_connected}
          />
          <StatCard
            label="Database Size"
            value={
              health?.database_size_mb
                ? `${health.database_size_mb.toFixed(2)} MB`
                : "N/A"
            }
            icon={<HardDrive size={20} />}
          />
        </div>
      </div>

      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold text-text-primary mb-6 flex items-center gap-2">
          <FileText size={24} />
          Database Statistics
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            label="Total Users"
            value={stats?.total_users}
            icon={<Users size={20} />}
            color="blue"
          />
          <StatCard
            label="Total Courses"
            value={stats?.total_courses}
            icon={<BookOpen size={20} />}
            color="yellow"
          />
          <StatCard
            label="Total Enrollments"
            value={stats?.total_enrollments}
            icon={<FileText size={20} />}
            color="pink"
          />
        </div>
      </div>
    </div>
  );
}

function HealthCard({
  label,
  status,
}: {
  label: string;
  status: boolean | undefined;
}) {
  return (
    <div className="bg-bg-card border border-border-primary rounded-lg p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-text-secondary">{label}</span>
        {status ? (
          <CheckCircle className="text-green-500" size={20} />
        ) : (
          <XCircle className="text-red-500" size={20} />
        )}
      </div>
      <p
        className={`mt-2 text-lg font-semibold ${
          status ? "text-green-400" : "text-red-400"
        }`}
      >
        {status ? "Connected" : "Disconnected"}
      </p>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  color = "default",
}: {
  label: string;
  value: number | string | undefined;
  icon: React.ReactNode;
  color?: "default" | "blue" | "green" | "purple" | "yellow" | "pink" | "cyan";
}) {
  const colorClasses = {
    default: "text-text-primary",
    blue: "text-blue-400",
    green: "text-green-400",
    purple: "text-purple-400",
    yellow: "text-yellow-400",
    pink: "text-pink-400",
    cyan: "text-cyan-400",
  };

  return (
    <div className="bg-bg-card border border-border-primary rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className={colorClasses[color]}>{icon}</span>
        <span className="text-sm text-text-secondary">{label}</span>
      </div>
      <p className="text-2xl font-bold text-text-primary">
        {value !== undefined ? value : "—"}
      </p>
    </div>
  );
}
