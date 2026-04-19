"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import { ProfileHeader } from "@/components/profile/profile-header";
import { StatsGrid } from "@/components/profile/stats-grid";
import { EnrollmentHistory } from "@/components/profile/enrollment-history";
import { AuditSection } from "@/components/profile/audit-section";
import { GpaCalculator } from "@/components/profile/gpa-calculator";
import type { ApiResponse, UserStats, EnrollmentItem, AuditResult } from "@/types";

type Tab = "audit" | "history" | "gpa";

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [enrollments, setEnrollments] = useState<EnrollmentItem[]>([]);
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>("audit");

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, enrollRes, auditRes] = await Promise.allSettled([
          api.get<ApiResponse<UserStats>>("/profile/stats"),
          api.get<ApiResponse<EnrollmentItem[]>>("/profile/enrollments"),
          api.get<ApiResponse<AuditResult>>("/profile/audit"),
        ]);

        if (statsRes.status === "fulfilled") {
          setStats(statsRes.value.data);
        }
        if (enrollRes.status === "fulfilled") {
          setEnrollments(enrollRes.value.data);
        }
        if (auditRes.status === "fulfilled") {
          setAudit(auditRes.value.data);
        }
      } catch {
        // silently fail, components handle empty state
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size={28} text="Loading profile..." />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl">
      {user && <ProfileHeader user={user} />}

      {stats && <StatsGrid stats={stats} />}

      {/* Tabs */}
      <div>
        <div className="flex gap-1 border-b border-border-primary mb-6">
          {(["audit", "history", "gpa"] as Tab[]).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                activeTab === tab
                  ? "border-accent-green text-text-primary"
                  : "border-transparent text-text-muted hover:text-text-secondary"
              }`}
            >
              {tab === "audit" ? "Degree Audit" : tab === "history" ? "Course History" : "GPA Calculator"}
            </button>
          ))}
        </div>

        {activeTab === "audit" && (
          audit
            ? <AuditSection audit={audit} studyYear={user?.study_year} />
            : (
              <p className="text-sm text-text-muted text-center py-10">
                No audit data available. Upload your transcript to get started.
              </p>
            )
        )}

        {activeTab === "history" && (
          <EnrollmentHistory enrollments={enrollments} />
        )}

        {activeTab === "gpa" && (
          <GpaCalculator enrollments={enrollments} />
        )}
      </div>
    </div>
  );
}
