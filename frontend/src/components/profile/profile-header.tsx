"use client";

import { useState } from "react";
import { Pencil, X, Check } from "lucide-react";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { ApiResponse, User } from "@/types";

const KLL_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

const MAJORS_BY_SCHOOL: { school: string; majors: string[] }[] = [
  {
    school: "School of Engineering and Digital Sciences",
    majors: [
      "Computer Science",
      "Electrical and Computer Engineering",
      "Civil and Environmental Engineering",
      "Mechanical and Aerospace Engineering",
      "Chemical and Materials Engineering",
      "Robotics Engineering",
    ],
  },
  {
    school: "School of Sciences and Humanities",
    majors: [
      "Anthropology",
      "Biological Sciences",
      "Chemistry",
      "Economics",
      "History",
      "Mathematics",
      "Physics",
      "Political Science and International Relations",
      "Sociology",
      "World Languages",
    ],
  },
  {
    school: "School of Mining and Geosciences",
    majors: ["Geology", "Mining Engineering", "Petroleum Engineering"],
  },
  {
    school: "School of Medicine",
    majors: ["Medicine", "Nursing"],
  },
  {
    school: "Graduate Schools",
    majors: ["Business Administration", "Education", "Public Policy"],
  },
];

interface ProfileHeaderProps {
  user: User;
}

export function ProfileHeader({ user }: ProfileHeaderProps) {
  const { fetchUser } = useAuthStore();
  const fullName = `${user.first_name} ${user.last_name}`;

  const [editing, setEditing] = useState(false);
  const [major, setMajor] = useState(user.major ?? "");
  const [kazakhLevel, setKazakhLevel] = useState(user.kazakh_level ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await api.patch<ApiResponse>("/profile", {
        major: major.trim() || null,
        kazakh_level: kazakhLevel || null,
      });
      await fetchUser();
      setEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setMajor(user.major ?? "");
    setKazakhLevel(user.kazakh_level ?? "");
    setError(null);
    setEditing(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-5">
        <Avatar src={user.avatar_url} name={fullName} size="lg" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-text-primary">{fullName}</h1>
            {!editing && (
              <button
                type="button"
                onClick={() => setEditing(true)}
                className="p-1 text-text-muted hover:text-text-primary transition-colors"
                title="Edit profile"
              >
                <Pencil size={14} />
              </button>
            )}
          </div>
          <p className="text-sm text-text-secondary">{user.email}</p>
          {!editing && (
            <div className="flex flex-wrap gap-2 mt-2">
              {user.major && <Badge variant="green">{user.major}</Badge>}
              {user.kazakh_level && (
                <Badge variant="muted">KLL {user.kazakh_level}</Badge>
              )}
            </div>
          )}
        </div>
      </div>

      {editing && (
        <div className="rounded-lg border border-border-primary bg-bg-elevated p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-text-muted mb-1">Major</label>
              <select
                value={major}
                onChange={(e) => setMajor(e.target.value)}
                className="glass-input w-full px-3 py-1.5 text-sm"
              >
                <option value="">— Select major —</option>
                {MAJORS_BY_SCHOOL.map((group) => (
                  <optgroup key={group.school} label={group.school}>
                    {group.majors.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-text-muted mb-1">
                Kazakh Language Level
              </label>
              <select
                value={kazakhLevel}
                onChange={(e) => setKazakhLevel(e.target.value)}
                className="glass-input w-full px-3 py-1.5 text-sm"
              >
                <option value="">Not set</option>
                {KLL_LEVELS.map((lvl) => (
                  <option key={lvl} value={lvl}>KLL {lvl}</option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <p className="text-xs text-accent-red">{error}</p>
          )}

          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="inline-flex items-center gap-1.5 rounded-full bg-accent-green/15 text-accent-green border border-accent-green/30 px-3 py-1.5 text-xs font-medium hover:bg-accent-green/25 transition-colors disabled:opacity-50"
            >
              <Check size={12} />
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              disabled={saving}
              className="inline-flex items-center gap-1.5 rounded-full bg-bg-card text-text-secondary border border-border-primary px-3 py-1.5 text-xs font-medium hover:border-border-light transition-colors"
            >
              <X size={12} />
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
