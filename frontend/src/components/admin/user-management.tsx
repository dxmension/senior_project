"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ApiResponse, UserListItem, UserDetail } from "@/types";
import { Search, UserCog, Shield, CheckCircle, XCircle, Trash2 } from "lucide-react";

interface UserManagementProps {
  users: UserListItem[];
  onUpdate: () => void;
}

export function UserManagement({ users, onUpdate }: UserManagementProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<UserListItem[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserDetail | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const res = await api.get<ApiResponse<UserListItem[]>>(
        `/admin/users/search?q=${encodeURIComponent(searchQuery)}`
      );
      setSearchResults(res.data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const loadUserDetail = async (userId: number) => {
    try {
      const res = await api.get<ApiResponse<UserDetail>>(
        `/admin/users/${userId}`
      );
      setSelectedUser(res.data);
    } catch (err) {
      console.error("Failed to load user details:", err);
    }
  };

  const updateUser = async (
    userId: number,
    updates: {
      is_admin?: boolean;
      is_onboarded?: boolean;
    }
  ) => {
    setIsUpdating(true);
    try {
      await api.patch<ApiResponse<UserDetail>>(
        `/admin/users/${userId}`,
        updates
      );
      await loadUserDetail(userId);
      onUpdate();
    } catch (err) {
      console.error("Update failed:", err);
      alert(err instanceof Error ? err.message : "Failed to update user");
    } finally {
      setIsUpdating(false);
    }
  };

  const deleteUser = async (userId: number) => {
    if (!confirm("Are you sure you want to delete this user? This action cannot be undone.")) {
      return;
    }

    setIsUpdating(true);
    try {
      await api.delete(`/admin/users/${userId}`);
      setSelectedUser(null);
      onUpdate();
    } catch (err) {
      console.error("Delete failed:", err);
      alert(err instanceof Error ? err.message : "Failed to delete user");
    } finally {
      setIsUpdating(false);
    }
  };

  const displayedUsers = searchResults.length > 0 ? searchResults : users;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold text-text-primary mb-4">
            User Management
          </h2>

          <div className="flex gap-2 mb-4">
            <div className="relative flex-1">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary"
                size={18}
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Search by name or email..."
                className="w-full pl-10 pr-4 py-2 bg-bg-card border border-border-primary rounded-lg text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-green"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="px-4 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green/90 disabled:opacity-50"
            >
              {isSearching ? "..." : "Search"}
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border-primary">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Name
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Email
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Major
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {displayedUsers.map((user) => (
                  <tr
                    key={user.id}
                    onClick={() => loadUserDetail(user.id)}
                    className="border-b border-border-primary hover:bg-bg-card cursor-pointer"
                  >
                    <td className="py-3 px-4 text-sm text-text-primary">
                      {user.first_name} {user.last_name}
                    </td>
                    <td className="py-3 px-4 text-sm text-text-secondary">
                      {user.email}
                    </td>
                    <td className="py-3 px-4 text-sm text-text-secondary">
                      {user.major || "—"}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        {user.is_admin && (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                            <Shield size={12} />
                            Admin
                          </span>
                        )}
                        {user.is_onboarded ? (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                            <CheckCircle size={12} />
                            Onboarded
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded">
                            <XCircle size={12} />
                            Pending
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="lg:col-span-1">
        <div className="glass-card p-6 sticky top-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <UserCog size={20} />
            User Details
          </h3>

          {selectedUser ? (
            <div className="space-y-4">
              <div>
                <label className="text-xs text-text-secondary">Name</label>
                <p className="text-sm text-text-primary font-medium">
                  {selectedUser.first_name} {selectedUser.last_name}
                </p>
              </div>

              <div>
                <label className="text-xs text-text-secondary">Email</label>
                <p className="text-sm text-text-primary">{selectedUser.email}</p>
              </div>

              <div>
                <label className="text-xs text-text-secondary">Major</label>
                <p className="text-sm text-text-primary">
                  {selectedUser.major || "Not set"}
                </p>
              </div>

              <div>
                <label className="text-xs text-text-secondary">Study Year</label>
                <p className="text-sm text-text-primary">
                  {selectedUser.study_year || "Not set"}
                </p>
              </div>

              <div>
                <label className="text-xs text-text-secondary">CGPA</label>
                <p className="text-sm text-text-primary">
                  {selectedUser.cgpa?.toFixed(2) || "Not set"}
                </p>
              </div>

              <div>
                <label className="text-xs text-text-secondary">
                  Enrollments
                </label>
                <p className="text-sm text-text-primary">
                  {selectedUser.enrollment_count} courses
                </p>
              </div>

              <div className="pt-4 border-t border-border-primary space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-primary">Admin Status</span>
                  <button
                    onClick={() =>
                      updateUser(selectedUser.id, {
                        is_admin: !selectedUser.is_admin,
                      })
                    }
                    disabled={isUpdating}
                    className={`px-3 py-1 text-xs rounded flex items-center gap-1 ${
                      selectedUser.is_admin
                        ? "bg-purple-500/20 text-purple-400 hover:bg-purple-500/30"
                        : "bg-accent-green/20 text-accent-green hover:bg-accent-green/30"
                    } disabled:opacity-50`}
                  >
                    <Shield size={12} />
                    {selectedUser.is_admin ? "Revoke Admin" : "Promote to Admin"}
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-primary">
                    Onboarded Status
                  </span>
                  <button
                    onClick={() =>
                      updateUser(selectedUser.id, {
                        is_onboarded: !selectedUser.is_onboarded,
                      })
                    }
                    disabled={isUpdating}
                    className={`px-3 py-1 text-xs rounded ${
                      selectedUser.is_onboarded
                        ? "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                        : "bg-bg-card text-text-secondary hover:bg-bg-hover"
                    } disabled:opacity-50`}
                  >
                    {selectedUser.is_onboarded ? "Onboarded" : "Not Onboarded"}
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-border-primary">
                <button
                  onClick={() => deleteUser(selectedUser.id)}
                  disabled={isUpdating}
                  className="w-full px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 disabled:opacity-50 flex items-center justify-center gap-2 text-sm font-medium"
                >
                  <Trash2 size={16} />
                  Remove User
                </button>
              </div>

              <div className="pt-4 border-t border-border-primary text-xs text-text-secondary">
                <p>Created: {new Date(selectedUser.created_at).toLocaleDateString()}</p>
                <p>Updated: {new Date(selectedUser.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-text-secondary text-center py-8">
              Select a user to view details
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
