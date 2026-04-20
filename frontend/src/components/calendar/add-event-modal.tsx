"use client";

import { useEffect, useState } from "react";
import { X, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { ApiResponse, CalendarEntry } from "@/types";

interface Category {
  id: number;
  name: string;
  color: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
  existingPersonalEvents: CalendarEntry[];
  initialDate?: string;
}

function hasClash(
  start: Date,
  end: Date,
  existing: CalendarEntry[]
): boolean {
  const s = start.getTime();
  const e = end.getTime();
  return existing.some((x) => {
    if (!x.end_at) return false;
    const xs = new Date(x.start_at).getTime();
    const xe = new Date(x.end_at).getTime();
    return s < xe && e > xs;
  });
}

function toAlmatyISO(dateStr: string, timeStr: string): string {
  return `${dateStr}T${timeStr}:00+05:00`;
}

export function AddEventModal({
  isOpen,
  onClose,
  onCreated,
  existingPersonalEvents,
  initialDate,
}: Props) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [title, setTitle] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [date, setDate] = useState(initialDate ?? new Date().toISOString().slice(0, 10));
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:00");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    api
      .get<ApiResponse<Category[]>>("/events/categories")
      .then((res) => setCategories(res.data ?? []))
      .catch(() => {});
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      setTitle("");
      setCategoryId(null);
      setDate(initialDate ?? new Date().toISOString().slice(0, 10));
      setStartTime("09:00");
      setEndTime("10:00");
      setDescription("");
      setLocation("");
      setError(null);
    }
  }, [isOpen, initialDate]);

  if (!isOpen) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const start = new Date(`${date}T${startTime}:00+05:00`);
    const end = new Date(`${date}T${endTime}:00+05:00`);

    if (end <= start) {
      setError("End time must be after start time.");
      return;
    }

    if (hasClash(start, end, existingPersonalEvents)) {
      setError("This time conflicts with an existing event.");
      return;
    }

    setSubmitting(true);
    try {
      await api.post<ApiResponse>("/events", {
        title,
        description: description || null,
        location: location || null,
        start_at: toAlmatyISO(date, startTime),
        end_at: toAlmatyISO(date, endTime),
        is_all_day: false,
        category_id: categoryId,
      });
      onCreated();
      onClose();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to create event";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="relative glass-card w-full max-w-md p-6 shadow-2xl">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-text-secondary hover:bg-white/5 hover:text-text-primary transition-colors"
        >
          <X size={16} />
        </button>

        <h2 className="text-base font-semibold text-text-primary mb-5">Add event</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-text-muted mb-1">Title</label>
            <input
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Study session"
              className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green/50"
            />
          </div>

          {categories.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-text-muted mb-1">Category</label>
              <select
                value={categoryId ?? ""}
                onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : null)}
                className="w-full rounded-lg border border-border-primary bg-bg-card px-3 py-2 text-sm text-text-primary"
              >
                <option value="">— no category —</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-text-muted mb-1">Date</label>
            <input
              required
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green/50"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-text-muted mb-1">Start time</label>
              <input
                required
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green/50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-muted mb-1">End time</label>
              <input
                required
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green/50"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-text-muted mb-1">
              Location <span className="font-normal">(optional)</span>
            </label>
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Library room 201"
              className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green/50"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-text-muted mb-1">
              Description <span className="font-normal">(optional)</span>
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary resize-none focus:outline-none focus:border-accent-green/50"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-accent-red/30 bg-accent-red/10 px-3 py-2">
              <AlertCircle size={14} className="text-accent-red shrink-0" />
              <p className="text-xs text-accent-red">{error}</p>
            </div>
          )}

          <div className="flex gap-3 justify-end pt-1">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary px-4 py-2 text-sm rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !title.trim()}
              className="px-4 py-2 text-sm font-semibold rounded-lg bg-accent-green text-bg-primary hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              {submitting ? "Saving…" : "Create event"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
