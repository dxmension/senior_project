"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { useAssessmentsStore } from "@/stores/assessments";
import type {
  Assessment,
  AssessmentType,
  EnrollmentItem,
} from "@/types";

const ASSESSMENT_LABELS: Record<AssessmentType, string> = {
  homework: "Homework",
  quiz: "Quiz",
  midterm: "Midterm",
  final: "Final Exam",
  project: "Project",
  lab: "Lab",
  presentation: "Presentation",
  other: "Other",
};

const PRESETS: {
  icon: string;
  label: string;
  type: AssessmentType;
  weight: number;
}[] = [
  { icon: "📝", label: "Midterm", type: "midterm", weight: 50 },
  { icon: "📝", label: "Final", type: "final", weight: 100 },
  { icon: "📋", label: "Project", type: "project", weight: 30 },
  { icon: "📄", label: "Homework", type: "homework", weight: 10 },
  { icon: "❓", label: "Quiz", type: "quiz", weight: 5 },
  { icon: "🔬", label: "Lab", type: "lab", weight: 15 },
];

function toDatetimeLocal(isoString: string): string {
  const date = new Date(isoString);
  const offsetMs = 6 * 60 * 60 * 1000;
  const localDate = new Date(date.getTime() + offsetMs);
  return localDate.toISOString().slice(0, 16);
}

interface FormState {
  title: string;
  assessment_type: AssessmentType;
  deadline: string;
  weight: string;
  max_score: string;
  description: string;
}

const EMPTY_FORM: FormState = {
  title: "",
  assessment_type: "other",
  deadline: "",
  weight: "",
  max_score: "",
  description: "",
};

interface AddAssessmentModalProps {
  open: boolean;
  onClose: () => void;
  enrollment: EnrollmentItem;
  onSuccess: (assessment: Assessment) => void;
  initialData?: Assessment;
}

export function AddAssessmentModal({
  open,
  onClose,
  enrollment,
  onSuccess,
  initialData,
}: AddAssessmentModalProps) {
  const [tab, setTab] = useState<"manual" | "presets">("manual");
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { addAssessment, updateAssessment } = useAssessmentsStore();

  const isEdit = !!initialData;

  // Populate form when modal opens or initialData changes
  useEffect(() => {
    if (!open) return;
    if (initialData) {
      setForm({
        title: initialData.title,
        assessment_type: initialData.assessment_type,
        deadline: toDatetimeLocal(initialData.deadline),
        weight: initialData.weight != null ? String(initialData.weight) : "",
        max_score:
          initialData.max_score != null ? String(initialData.max_score) : "",
        description: initialData.description ?? "",
      });
    } else {
      setForm(EMPTY_FORM);
    }
    setTab("manual");
    setError(null);
  }, [open, initialData]);

  function applyPreset(preset: (typeof PRESETS)[number]) {
    setForm((f) => ({
      ...f,
      assessment_type: preset.type,
      title: preset.label,
      weight: String(preset.weight),
    }));
    setTab("manual");
  }

  function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!form.title.trim()) {
      setError("Title is required.");
      return;
    }
    if (!form.deadline) {
      setError("Deadline is required.");
      return;
    }

    const deadlineIso = form.deadline + ":00+06:00";
    const weight =
      form.weight !== "" ? parseFloat(form.weight) : undefined;
    const maxScore =
      form.max_score !== "" ? parseFloat(form.max_score) : undefined;

    setSubmitting(true);
    try {
      let result: Assessment;
      if (isEdit && initialData) {
        result = await updateAssessment(initialData.id, {
          title: form.title.trim(),
          assessment_type: form.assessment_type,
          deadline: deadlineIso,
          weight,
          max_score: maxScore,
          description: form.description.trim() || undefined,
        });
      } else {
        result = await addAssessment({
          course_id: enrollment.course_id,
          assessment_type: form.assessment_type,
          title: form.title.trim(),
          deadline: deadlineIso,
          weight,
          max_score: maxScore,
          description: form.description.trim() || undefined,
        });
      }
      onSuccess(result);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center">
      <div className="glass-card w-full rounded-t-2xl p-0 transition-all duration-200 sm:max-w-lg sm:rounded-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#2a2a2a] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-text-primary">
              {isEdit ? "Edit Deadline" : "Add Deadline"}
            </h2>
            <p className="text-xs text-text-secondary">
              {enrollment.course_code} · {enrollment.course_title}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
          >
            <X size={16} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[#2a2a2a]">
          {(["manual", "presets"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`flex-1 py-2.5 text-sm transition-colors ${
                tab === t
                  ? "border-b-2 border-accent-green text-text-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {t === "manual" ? "Fill manually" : "Quick presets"}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="px-5 py-4">
          {tab === "presets" ? (
            <div className="grid grid-cols-3 gap-2">
              {PRESETS.map((preset) => (
                <button
                  key={preset.type}
                  type="button"
                  onClick={() => applyPreset(preset)}
                  className="flex flex-col items-center gap-1 rounded-xl border border-[#2a2a2a] bg-white/[0.03] px-3 py-3 text-center transition-colors hover:border-accent-green/40 hover:bg-white/5"
                >
                  <span className="text-xl">{preset.icon}</span>
                  <span className="text-xs font-medium text-text-primary">
                    {preset.label}
                  </span>
                  <span className="text-[10px] text-text-secondary">
                    {preset.weight}% weight
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              {/* Title */}
              <div>
                <label className="mb-1 block text-xs text-text-secondary">
                  Title <span className="text-accent-red">*</span>
                </label>
                <input
                  type="text"
                  maxLength={255}
                  placeholder="e.g. Midterm Exam"
                  value={form.title}
                  onChange={(e) => setField("title", e.target.value)}
                  className="glass-input w-full text-sm"
                  required
                />
              </div>

              {/* Type */}
              <div>
                <label className="mb-1 block text-xs text-text-secondary">
                  Type <span className="text-accent-red">*</span>
                </label>
                <select
                  value={form.assessment_type}
                  onChange={(e) =>
                    setField("assessment_type", e.target.value as AssessmentType)
                  }
                  className="glass-input w-full text-sm"
                  required
                >
                  {(Object.keys(ASSESSMENT_LABELS) as AssessmentType[]).map(
                    (t) => (
                      <option key={t} value={t}>
                        {ASSESSMENT_LABELS[t]}
                      </option>
                    )
                  )}
                </select>
              </div>

              {/* Date & Time */}
              <div>
                <label className="mb-1 block text-xs text-text-secondary">
                  Date & Time <span className="text-accent-red">*</span>
                </label>
                <input
                  type="datetime-local"
                  value={form.deadline}
                  onChange={(e) => setField("deadline", e.target.value)}
                  className="glass-input w-full text-sm"
                  required
                />
              </div>

              {/* Weight & Max score */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs text-text-secondary">
                    Weight (%)
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    placeholder="e.g. 30"
                    value={form.weight}
                    onChange={(e) => setField("weight", e.target.value)}
                    className="glass-input w-full text-sm"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-text-secondary">
                    Max score
                  </label>
                  <input
                    type="number"
                    min={0}
                    placeholder="e.g. 100"
                    value={form.max_score}
                    onChange={(e) => setField("max_score", e.target.value)}
                    className="glass-input w-full text-sm"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="mb-1 block text-xs text-text-secondary">
                  Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Optional notes..."
                  value={form.description}
                  onChange={(e) => setField("description", e.target.value)}
                  className="glass-input w-full resize-none text-sm"
                />
              </div>

              {error && (
                <p className="text-xs text-accent-red">{error}</p>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary rounded-lg px-4 py-2 text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary rounded-lg px-4 py-2 text-sm disabled:opacity-60"
                >
                  {submitting
                    ? "Saving..."
                    : isEdit
                    ? "Save changes"
                    : "Add deadline"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
