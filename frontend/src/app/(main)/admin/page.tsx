"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  DatabaseStats,
  AnalyticsOverview,
  DatabaseHealth,
  UserListItem,
} from "@/types";
import { UserManagement } from "@/components/admin/user-management";
import { DatabaseManagement } from "@/components/admin/database-management";
import { Analytics } from "@/components/admin/analytics";
import { CourseManagement } from "@/components/admin/course-management";
import { MaterialsManagement } from "@/components/admin/materials-management";
import { Shield, AlertCircle } from "lucide-react";

type TabType =
  | "users"
  | "courses"
  | "materials"
  | "database"
  | "analytics";

export default function AdminPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState<TabType>("users");
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [health, setHealth] = useState<DatabaseHealth | null>(null);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.is_admin) {
      return;
    }
    loadData();
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, analyticsRes, healthRes, usersRes] = await Promise.all([
        api.get<ApiResponse<DatabaseStats>>("/admin/stats"),
        api.get<ApiResponse<AnalyticsOverview>>("/admin/analytics"),
        api.get<ApiResponse<DatabaseHealth>>("/admin/health"),
        api.get<ApiResponse<UserListItem[]>>("/admin/users?limit=50"),
      ]);

      setStats(statsRes.data);
      setAnalytics(analyticsRes.data);
      setHealth(healthRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-text-secondary">Loading...</p>
      </div>
    );
  }

  if (!user.is_admin) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <Shield className="text-red-500" size={48} />
        <h1 className="text-2xl font-bold text-text-primary">Access Denied</h1>
        <p className="text-text-secondary">
          You do not have permission to access this page.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-pulse text-text-secondary">
          Loading admin panel...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <AlertCircle className="text-red-500" size={48} />
        <h1 className="text-xl font-bold text-text-primary">Error</h1>
        <p className="text-text-secondary">{error}</p>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green/90"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1600px] overflow-x-hidden p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary mb-2">
          Admin Panel
        </h1>
        <p className="text-text-secondary">
          Manage users, database, and view analytics
        </p>
      </div>

      <div className="mb-6 flex flex-wrap gap-x-3 gap-y-2 border-b border-border-primary pb-2">
        <TabButton
          active={activeTab === "users"}
          onClick={() => setActiveTab("users")}
        >
          User Management
        </TabButton>
        <TabButton
          active={activeTab === "courses"}
          onClick={() => setActiveTab("courses")}
        >
          Course Management
        </TabButton>
        <TabButton
          active={activeTab === "materials"}
          onClick={() => setActiveTab("materials")}
        >
          Materials
        </TabButton>
        <TabButton
          active={activeTab === "database"}
          onClick={() => setActiveTab("database")}
        >
          Database Management
        </TabButton>
        <TabButton
          active={activeTab === "analytics"}
          onClick={() => setActiveTab("analytics")}
        >
          Analytics & Reporting
        </TabButton>
      </div>

      <div className="mt-6">
        {activeTab === "users" && (
          <UserManagement users={users} onUpdate={loadData} />
        )}
        {activeTab === "courses" && (
          <CourseManagement onUpdate={loadData} />
        )}
        {activeTab === "materials" && (
          <MaterialsManagement refreshKey={0} />
        )}
        {activeTab === "database" && (
          <DatabaseManagement stats={stats} health={health} />
        )}
        {activeTab === "analytics" && (
          <Analytics analytics={analytics} stats={stats} />
        )}
      </div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`border-b-2 px-2 py-2 text-sm font-medium transition-colors ${
        active
          ? "border-accent-green text-accent-green"
          : "border-transparent text-text-secondary hover:text-text-primary"
      }`}
    >
      {children}
    </button>
  );
}
