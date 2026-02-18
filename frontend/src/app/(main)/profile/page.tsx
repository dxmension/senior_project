"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/lib/api";
import { Spinner } from "@/components/ui/spinner";
import { ProfileHeader } from "@/components/profile/profile-header";
import { StatsGrid } from "@/components/profile/stats-grid";
import { EnrollmentHistory } from "@/components/profile/enrollment-history";
import type { ApiResponse, UserStats, EnrollmentItem } from "@/types";

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [enrollments, setEnrollments] = useState<EnrollmentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, enrollRes] = await Promise.all([
          api.get<ApiResponse<UserStats>>("/users/stats"),
          api.get<ApiResponse<EnrollmentItem[]>>("/users/enrollments"),
        ]);
        setStats(statsRes.data);
        setEnrollments(enrollRes.data);
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

      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-4">
          Course History
        </h2>
        <EnrollmentHistory enrollments={enrollments} />
      </div>
    </div>
  );
}
