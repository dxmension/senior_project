"use client";

import { useState } from "react";
import { Plus, Trash2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { GlassCard } from "@/components/ui/glass-card";
import type { ApiResponse, CourseRecord, ParsedTranscriptData } from "@/types";

interface ConfirmStepProps {
  parsedData: ParsedTranscriptData | null;
  isManual: boolean;
  onDone: () => void;
}

const emptyCourse: CourseRecord = {
  code: "",
  title: "",
  semester: "Fall",
  grade: "A",
  grade_points: 4.0,
  ects: 6,
};

export function ConfirmStep({ parsedData, isManual, onDone }: ConfirmStepProps) {
  const { fetchUser } = useAuthStore();
  const [major, setMajor] = useState(parsedData?.major || "");
  const [courses, setCourses] = useState<CourseRecord[]>(
    parsedData?.courses?.length ? parsedData.courses : []
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateCourse = (idx: number, field: keyof CourseRecord, value: string | number) => {
    setCourses((prev) =>
      prev.map((c, i) => (i === idx ? { ...c, [field]: value } : c))
    );
  };

  const removeCourse = (idx: number) => {
    setCourses((prev) => prev.filter((_, i) => i !== idx));
  };

  const addCourse = () => {
    setCourses((prev) => [...prev, { ...emptyCourse }]);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);

    const endpoint = isManual ? "/transcripts/manual" : "/transcripts/confirm";
    const payload = { major: major || null, courses };

    try {
      await api.post<ApiResponse>(endpoint, payload);
      await fetchUser();
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-1">
          {isManual ? "Enter Your Courses" : "Confirm Parsed Data"}
        </h2>
        <p className="text-sm text-text-secondary">
          {isManual
            ? "Add your courses and grades manually."
            : "Review and edit the parsed data before confirming."}
        </p>
      </div>

      <div>
        <label className="block text-sm text-text-secondary mb-1.5">Major</label>
        <input
          type="text"
          value={major}
          onChange={(e) => setMajor(e.target.value)}
          placeholder="e.g. Computer Science"
          className="glass-input w-full px-3 py-2 text-sm"
        />
      </div>

      <CourseTable
        courses={courses}
        onUpdate={updateCourse}
        onRemove={removeCourse}
      />

      <button
        onClick={addCourse}
        className="btn-secondary flex items-center gap-2 text-sm"
      >
        <Plus size={16} />
        Add Course
      </button>

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-[var(--radius-sm)] bg-accent-red-dim text-accent-red text-sm">
          <AlertCircle size={16} className="shrink-0" />
          {error}
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={submitting || courses.length === 0}
        className="btn-primary w-full"
      >
        {submitting ? "Saving..." : "Confirm & Continue"}
      </button>
    </div>
  );
}

interface CourseTableProps {
  courses: CourseRecord[];
  onUpdate: (idx: number, field: keyof CourseRecord, value: string | number) => void;
  onRemove: (idx: number) => void;
}

function CourseTable({ courses, onUpdate, onRemove }: CourseTableProps) {
  if (courses.length === 0) {
    return (
      <GlassCard className="text-center py-8">
        <p className="text-sm text-text-muted">
          No courses yet. Click &quot;Add Course&quot; to get started.
        </p>
      </GlassCard>
    );
  }

  return (
    <div className="overflow-x-auto">
      <GlassCard padding={false}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-primary text-text-muted">
              <th className="text-left px-4 py-3 font-medium">Code</th>
              <th className="text-left px-4 py-3 font-medium">Title</th>
              <th className="text-left px-4 py-3 font-medium">Semester</th>
              <th className="text-left px-4 py-3 font-medium">Year</th>
              <th className="text-left px-4 py-3 font-medium">Grade</th>
              <th className="text-center px-4 py-3 font-medium">ECTS</th>
              <th className="w-10" />
            </tr>
          </thead>
          <tbody>
            {courses.map((c, idx) => (
              <tr
                key={idx}
                className="border-b border-border-primary last:border-0 hover:bg-bg-card-hover transition-colors"
              >
                <td className="px-4 py-2">
                  <input
                    value={c.code}
                    onChange={(e) => onUpdate(idx, "code", e.target.value)}
                    className="glass-input px-2 py-1 w-24 text-xs font-mono"
                  />
                </td>
                <td className="px-4 py-2">
                  <input
                    value={c.title}
                    onChange={(e) => onUpdate(idx, "title", e.target.value)}
                    className="glass-input px-2 py-1 w-full text-xs"
                  />
                </td>
                <td className="px-4 py-2">
                  <select
                    value={c.semester}
                    onChange={(e) => onUpdate(idx, "semester", e.target.value)}
                    className="glass-input px-2 py-1 text-xs"
                  >
                    <option value="Fall">Fall</option>
                    <option value="Spring">Spring</option>
                    <option value="Summer">Summer</option>
                  </select>
                </td>
                <td className="px-4 py-2">
                  <input
                    value={c.grade}
                    onChange={(e) => onUpdate(idx, "grade", e.target.value)}
                    className="glass-input px-2 py-1 w-14 text-xs"
                  />
                </td>
                <td className="px-4 py-2 text-center">
                  <input
                    type="number"
                    value={c.ects}
                    onChange={(e) => onUpdate(idx, "ects", Number(e.target.value))}
                    className="glass-input px-2 py-1 w-14 text-xs text-center"
                  />
                </td>
                <td className="px-2 py-2">
                  <button
                    onClick={() => onRemove(idx)}
                    className="text-text-muted hover:text-accent-red transition-colors p-1"
                  >
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
}
