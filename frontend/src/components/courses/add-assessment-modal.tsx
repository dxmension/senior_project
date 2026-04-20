"use client";

import {
  AlertCircle,
  BookOpen,
  Calendar,
  Clock,
  FileText,
  FlaskConical,
  FolderOpen,
  GraduationCap,
  HelpCircle,
  Loader2,
  MoreHorizontal,
  Presentation,
  X,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useAssessmentsStore } from "@/stores/assessments";
import type { Assessment, AssessmentType, EnrollmentItem } from "@/types";

const ASSESSMENT_LABELS: Record<AssessmentType, string> = {
  midterm: "Midterm",
  final: "Final",
  project: "Project",
  homework: "Homework",
  quiz: "Quiz",
  lab: "Lab",
  presentation: "Presentation",
  other: "Other",
};

const TYPE_ICONS: Record<AssessmentType, React.ReactNode> = {
  midterm: <BookOpen size={14} />,
  final: <GraduationCap size={14} />,
  project: <FolderOpen size={14} />,
  homework: <FileText size={14} />,
  quiz: <HelpCircle size={14} />,
  lab: <FlaskConical size={14} />,
  presentation: <Presentation size={14} />,
  other: <MoreHorizontal size={14} />,
};

const PRESETS: {
  icon: React.ReactNode;
  label: string;
  type: AssessmentType;
  weight: number;
  description: string;
}[] = [
  { icon: <BookOpen size={20} />, label: "Midterm", type: "midterm", weight: 30, description: "Mid-semester exam" },
  { icon: <GraduationCap size={20} />, label: "Final", type: "final", weight: 40, description: "End-of-term exam" },
  { icon: <FolderOpen size={20} />, label: "Project", type: "project", weight: 25, description: "Course project" },
  { icon: <FileText size={20} />, label: "Homework", type: "homework", weight: 10, description: "Assignment" },
  { icon: <HelpCircle size={20} />, label: "Quiz", type: "quiz", weight: 5, description: "Short quiz" },
  { icon: <FlaskConical size={20} />, label: "Lab", type: "lab", weight: 15, description: "Lab work" },
];

// Auto-formats digit input → DD.MM.YYYY (inserts dots after day/month)
function formatDateMask(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}.${digits.slice(2)}`;
  return `${digits.slice(0, 2)}.${digits.slice(2, 4)}.${digits.slice(4)}`;
}

// Auto-formats digit input → HH:MM (inserts colon after hours)
function formatTimeMask(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 4);
  if (digits.length <= 2) return digits;
  return `${digits.slice(0, 2)}:${digits.slice(2)}`;
}

// Parse DD.MM.YYYY → YYYY-MM-DD, returns null if incomplete/invalid
function parseDateText(text: string): string | null {
  const parts = text.split(".");
  if (parts.length !== 3) return null;
  const [dd, mm, yyyy] = parts;
  if (!dd || !mm || !yyyy || yyyy.length < 4) return null;
  const d = parseInt(dd, 10), m = parseInt(mm, 10), y = parseInt(yyyy, 10);
  if (d < 1 || d > 31 || m < 1 || m > 12 || y < 2000) return null;
  return `${yyyy}-${mm.padStart(2, "0")}-${dd.padStart(2, "0")}`;
}

// Parse HH:MM, returns null if invalid
function parseTimeText(text: string): string | null {
  const match = text.match(/^(\d{1,2}):(\d{2})$/);
  if (!match) return null;
  const h = parseInt(match[1], 10), m = parseInt(match[2], 10);
  if (h > 23 || m > 59) return null;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

function toDatetimeLocal(isoString: string): string {
  const date = new Date(isoString);
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Almaty",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(date);
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
  return `${get("year")}-${get("month")}-${get("day")}T${get("hour")}:${get("minute")}`;
}

// Convert YYYY-MM-DDTHH:mm → { dateText: DD.MM.YYYY, timeText: HH:MM }
function splitToDisplay(iso: string): { dateText: string; timeText: string } {
  if (!iso) return { dateText: "", timeText: "" };
  const [datePart, timePart] = iso.split("T");
  if (!datePart) return { dateText: "", timeText: "" };
  const [yyyy, mm, dd] = datePart.split("-");
  return {
    dateText: `${dd ?? ""}.${mm ?? ""}.${yyyy ?? ""}`,
    timeText: timePart?.slice(0, 5) ?? "",
  };
}

interface FormState {
  assessment_type: AssessmentType;
  assessment_number: string;
  dateText: string;
  timeText: string;
  weight: string;
  max_score: string;
  description: string;
}

const EMPTY_FORM: FormState = {
  assessment_type: "other",
  assessment_number: "",
  dateText: "",
  timeText: "",
  weight: "",
  max_score: "",
  description: "",
};

function nextAssessmentNumber(
  assessments: Assessment[],
  assessmentType: AssessmentType,
) {
  const numbers = assessments
    .filter((item) => item.assessment_type === assessmentType)
    .map((item) => item.assessment_number);
  return String(Math.max(0, ...numbers) + 1);
}

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

  const { addAssessment, updateAssessment, byCourse } = useAssessmentsStore();
  const courseAssessments = byCourse[enrollment.course_id] ?? [];

  const isEdit = !!initialData;

  useEffect(() => {
    if (!open) return;
    if (initialData) {
      const { dateText, timeText } = splitToDisplay(toDatetimeLocal(initialData.deadline));
      setForm({
        assessment_type: initialData.assessment_type,
        assessment_number: String(initialData.assessment_number),
        dateText,
        timeText,
        weight: initialData.weight != null ? String(initialData.weight) : "",
        max_score: initialData.max_score != null ? String(initialData.max_score) : "",
        description: initialData.description ?? "",
      });
    } else {
      setForm({
        ...EMPTY_FORM,
        assessment_number: nextAssessmentNumber(courseAssessments, "other"),
      });
    }
    setTab("manual");
    setError(null);
  }, [courseAssessments, initialData, open]);

  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  function applyPreset(preset: (typeof PRESETS)[number]) {
    setForm((f) => ({
      ...f,
      assessment_type: preset.type,
      assessment_number: nextAssessmentNumber(courseAssessments, preset.type),
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

    const assessmentNumber = Number(form.assessment_number);
    if (!Number.isInteger(assessmentNumber) || assessmentNumber < 1) {
      setError("Assessment number must be 1 or higher.");
      return;
    }
    const parsedDate = parseDateText(form.dateText);
    if (!parsedDate) { setError("Enter a valid date — DD.MM.YYYY"); return; }
    const parsedTime = parseTimeText(form.timeText);
    if (!parsedTime) { setError("Enter a valid time — HH:MM"); return; }

    const deadlineIso = `${parsedDate}T${parsedTime}:00+05:00`;
    const weight = form.weight !== "" ? parseFloat(form.weight) : undefined;
    const maxScore = form.max_score !== "" ? parseFloat(form.max_score) : undefined;

    setSubmitting(true);
    try {
      let result: Assessment;
      if (isEdit && initialData) {
        result = await updateAssessment(initialData.id, {
          assessment_type: form.assessment_type,
          assessment_number: assessmentNumber,
          deadline: deadlineIso,
          weight,
          max_score: maxScore,
          description: form.description.trim() || undefined,
        });
      } else {
        result = await addAssessment({
          course_id: enrollment.course_id,
          assessment_type: form.assessment_type,
          assessment_number: assessmentNumber,
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
    <>
      <div
        className="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
        style={{ background: "rgba(0,0,0,0.75)", backdropFilter: "blur(6px)" }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <div
          className="w-full sm:max-w-md rounded-t-2xl sm:rounded-2xl flex flex-col"
          style={{
            background: "rgba(18,18,18,0.97)",
            border: "1px solid rgba(255,255,255,0.07)",
            maxHeight: "92dvh",
            boxShadow: "0 32px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(163,230,53,0.04)",
          }}
        >
          {/* ── Header ── */}
          <div className="flex items-start justify-between px-5 pt-5 pb-4 flex-shrink-0">
            <div className="flex flex-col gap-0.5">
              <h2 className="text-[15px] font-semibold tracking-tight text-text-primary">
                {isEdit ? "Edit Deadline" : "Add Deadline"}
              </h2>
              <p className="text-xs text-text-muted font-medium">
                {enrollment.course_code} · {enrollment.course_title}
              </p>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close"
              className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-white/5 hover:text-text-primary"
            >
              <X size={15} />
            </button>
          </div>

          {/* ── Tabs ── */}
          <div
            className="flex mx-5 mb-4 flex-shrink-0 rounded-lg p-0.5"
            style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.05)" }}
          >
            {(["manual", "presets"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-xs font-medium transition-all"
                style={
                  tab === t
                    ? { background: "rgba(163,230,53,0.12)", color: "#a3e635", boxShadow: "0 1px 4px rgba(0,0,0,0.3)" }
                    : { color: "#666" }
                }
              >
                {t === "presets" && <Zap size={11} />}
                {t === "manual" ? "Fill manually" : "Quick presets"}
              </button>
            ))}
          </div>

          {/* ── Scrollable body ── */}
          <div className="overflow-y-auto flex-1 px-5 pb-5">
            {tab === "presets" ? (
              <div className="grid grid-cols-3 gap-2">
                {PRESETS.map((preset) => (
                  <button
                    key={preset.type}
                    type="button"
                    onClick={() => applyPreset(preset)}
                    className="group flex flex-col items-center gap-2.5 rounded-xl px-2 py-4 text-center transition-all active:scale-95"
                    style={{
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.06)",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = "rgba(163,230,53,0.07)";
                      (e.currentTarget as HTMLElement).style.borderColor = "rgba(163,230,53,0.25)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.03)";
                      (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.06)";
                    }}
                  >
                    <span className="text-text-secondary group-hover:text-accent-green transition-colors">
                      {preset.icon}
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-text-primary">{preset.label}</p>
                      <p className="text-[10px] text-text-muted mt-0.5">{preset.description}</p>
                    </div>
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                      style={{ background: "rgba(163,230,53,0.1)", color: "#a3e635" }}
                    >
                      {preset.weight}%
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                {/* Number */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">
                    Number <span className="text-accent-red normal-case tracking-normal">*</span>
                  </label>
                  <input
                    type="number"
                    min={1}
                    inputMode="numeric"
                    placeholder="e.g. 2"
                    value={form.assessment_number}
                    onChange={(e) => setField("assessment_number", e.target.value)}
                    className="glass-input w-full text-sm px-3 py-2.5"
                  />
                  <p className="text-[10px] text-text-muted">
                    The title is generated automatically, like Midterm 2.
                  </p>
                </div>

                {/* Type chips */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">
                    Type <span className="text-accent-red normal-case tracking-normal">*</span>
                  </label>
                  <div className="grid grid-cols-4 gap-1.5">
                    {(Object.keys(ASSESSMENT_LABELS) as AssessmentType[]).map((t) => (
                      <button
                        key={t}
                        type="button"
                        onClick={() => {
                          setField("assessment_type", t);
                          if (!isEdit) {
                            setField("assessment_number", nextAssessmentNumber(courseAssessments, t));
                          }
                        }}
                        className="flex flex-col items-center gap-1 rounded-lg py-2.5 px-1 text-center transition-all text-[10px] font-medium"
                        style={
                          form.assessment_type === t
                            ? {
                                background: "rgba(163,230,53,0.12)",
                                border: "1px solid rgba(163,230,53,0.35)",
                                color: "#a3e635",
                              }
                            : {
                                background: "rgba(255,255,255,0.02)",
                                border: "1px solid rgba(255,255,255,0.05)",
                                color: "#666",
                              }
                        }
                      >
                        <span>{TYPE_ICONS[t]}</span>
                        <span>{ASSESSMENT_LABELS[t]}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Date + Time — masked text inputs, type fast */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">
                    Deadline <span className="text-accent-red normal-case tracking-normal">*</span>
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {/* Date */}
                    <div className="relative flex items-center">
                      <Calendar size={14} className="absolute left-3 text-text-muted pointer-events-none z-10" />
                      <input
                        type="text"
                        inputMode="numeric"
                        placeholder="DD.MM.YYYY"
                        value={form.dateText}
                        onChange={(e) => setField("dateText", formatDateMask(e.target.value))}
                        maxLength={10}
                        className="glass-input w-full text-sm pl-9 pr-3 py-2.5 font-mono tracking-wide"
                      />
                    </div>
                    {/* Time */}
                    <div className="relative flex items-center">
                      <Clock size={14} className="absolute left-3 text-text-muted pointer-events-none z-10" />
                      <input
                        type="text"
                        inputMode="numeric"
                        placeholder="HH:MM"
                        value={form.timeText}
                        onChange={(e) => setField("timeText", formatTimeMask(e.target.value))}
                        maxLength={5}
                        className="glass-input w-full text-sm pl-9 pr-3 py-2.5 font-mono tracking-wide"
                      />
                    </div>
                  </div>
                  <p className="text-[10px] text-text-muted">
                    Type digits — formats automatically
                  </p>
                </div>

                {/* Optional section */}
                <div className="flex items-center gap-3 py-1">
                  <div className="h-px flex-1" style={{ background: "rgba(255,255,255,0.05)" }} />
                  <span className="text-[9px] font-bold uppercase tracking-widest text-text-muted/50">
                    Optional
                  </span>
                  <div className="h-px flex-1" style={{ background: "rgba(255,255,255,0.05)" }} />
                </div>

                {/* Weight + Max Score */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">
                      Weight %
                    </label>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      placeholder="30"
                      value={form.weight}
                      onChange={(e) => setField("weight", e.target.value)}
                      className="glass-input w-full text-sm px-3 py-2.5"
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">
                      Max Score
                    </label>
                    <input
                      type="number"
                      min={0}
                      placeholder="100"
                      value={form.max_score}
                      onChange={(e) => setField("max_score", e.target.value)}
                      className="glass-input w-full text-sm px-3 py-2.5"
                    />
                  </div>
                </div>

                {/* Notes */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">
                    Notes
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Add any notes..."
                    value={form.description}
                    onChange={(e) => setField("description", e.target.value)}
                    className="glass-input w-full resize-none text-sm px-3 py-2.5"
                  />
                </div>

                {/* Error */}
                {error && (
                  <div
                    className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-xs"
                    style={{ background: "rgba(248,113,113,0.1)", color: "#f87171" }}
                  >
                    <AlertCircle size={12} className="flex-shrink-0" />
                    {error}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-1">
                  <button
                    type="button"
                    onClick={onClose}
                    className="btn-secondary flex-1 text-sm py-2.5"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm py-2.5"
                  >
                    {submitting && <Loader2 size={13} className="animate-spin" />}
                    {submitting ? "Saving..." : isEdit ? "Save changes" : "Add deadline"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
