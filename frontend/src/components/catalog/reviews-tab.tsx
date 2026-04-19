"use client";

import { useEffect, useState } from "react";
import { Star, Pencil, Trash2, AlertCircle } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { ApiResponse, ReviewsPage, CourseReview } from "@/types";

// ─── Star rating ─────────────────────────────────────────────────────────────

interface StarProps {
  value: number;          // 1–5
  onChange?: (v: number) => void;
  size?: number;
}

function StarRating({ value, onChange, size = 16 }: StarProps) {
  const [hovered, setHovered] = useState(0);
  const interactive = !!onChange;
  const display = hovered || value;

  return (
    <div className={`flex gap-0.5 ${interactive ? "cursor-pointer" : ""}`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          size={size}
          className={`transition-colors ${
            n <= display ? "text-yellow-400 fill-yellow-400" : "text-text-muted/30"
          }`}
          onMouseEnter={() => interactive && setHovered(n)}
          onMouseLeave={() => interactive && setHovered(0)}
          onClick={() => onChange?.(n)}
        />
      ))}
    </div>
  );
}

function AvgStars({ value }: { value: number | null }) {
  if (value == null) return <span className="text-xs text-text-muted">—</span>;
  const rounded = Math.round(value * 2) / 2; // round to 0.5
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((n) => (
          <Star
            key={n}
            size={13}
            className={`${
              n <= rounded
                ? "text-yellow-400 fill-yellow-400"
                : n - 0.5 <= rounded
                ? "text-yellow-400 fill-yellow-400/40"
                : "text-text-muted/30"
            }`}
          />
        ))}
      </div>
      <span className="text-xs text-text-muted font-mono">{value.toFixed(1)}</span>
    </div>
  );
}

// ─── Sub-rating row ───────────────────────────────────────────────────────────

const SUB_LABELS: Record<string, string> = {
  difficulty: "Difficulty",
  informativeness: "Informativeness",
  gpa_boost: "GPA Boost",
  workload: "Workload",
};

interface SubRatingInputProps {
  field: string;
  value: number | null;
  onChange: (v: number | null) => void;
}

function SubRatingInput({ field, value, onChange }: SubRatingInputProps) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-text-muted">{SUB_LABELS[field]}</span>
      <div className="flex items-center gap-2">
        <StarRating value={value ?? 0} onChange={(v) => onChange(v === value ? null : v)} size={14} />
        {value != null && (
          <button
            type="button"
            onClick={() => onChange(null)}
            className="text-[10px] text-text-muted/50 hover:text-text-muted"
          >
            clear
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Review card ──────────────────────────────────────────────────────────────

interface ReviewCardProps {
  review: CourseReview;
  isOwn: boolean;
  onEdit: () => void;
  onDelete: () => void;
}

function ReviewCard({ review, isOwn, onEdit, onDelete }: ReviewCardProps) {
  const subRatings = (
    ["difficulty", "informativeness", "gpa_boost", "workload"] as const
  ).filter((k) => review[k] != null);

  return (
    <div className="rounded-lg border border-border-primary bg-bg-elevated p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-7 h-7 rounded-full bg-accent-green/20 flex items-center justify-center shrink-0">
            <span className="text-xs font-semibold text-accent-green">
              {review.author.first_name[0]}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-text-primary truncate">
              {review.author.first_name} {review.author.last_name}
              {isOwn && (
                <span className="ml-1.5 text-[10px] text-accent-green font-normal">(you)</span>
              )}
            </p>
            <p className="text-[10px] text-text-muted">
              {new Date(review.created_at).toLocaleDateString("en-US", {
                year: "numeric", month: "short", day: "numeric",
              })}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <StarRating value={review.overall_rating} size={14} />
          {isOwn && (
            <div className="flex gap-1">
              <button
                type="button"
                onClick={onEdit}
                className="p-1 rounded text-text-muted hover:text-text-primary transition-colors"
                title="Edit review"
              >
                <Pencil size={13} />
              </button>
              <button
                type="button"
                onClick={onDelete}
                className="p-1 rounded text-text-muted hover:text-accent-red transition-colors"
                title="Delete review"
              >
                <Trash2 size={13} />
              </button>
            </div>
          )}
        </div>
      </div>

      {review.comment && (
        <p className="text-sm text-text-secondary leading-relaxed">{review.comment}</p>
      )}

      {subRatings.length > 0 && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 pt-1">
          {subRatings.map((k) => (
            <div key={k} className="flex items-center gap-1.5">
              <span className="text-[10px] text-text-muted">{SUB_LABELS[k]}:</span>
              <div className="flex gap-0.5">
                {[1, 2, 3, 4, 5].map((n) => (
                  <Star
                    key={n}
                    size={10}
                    className={n <= (review[k] ?? 0) ? "text-yellow-400 fill-yellow-400" : "text-text-muted/20"}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Review form ──────────────────────────────────────────────────────────────

interface FormState {
  overall_rating: number;
  difficulty: number | null;
  informativeness: number | null;
  gpa_boost: number | null;
  workload: number | null;
  comment: string;
}

const EMPTY_FORM: FormState = {
  overall_rating: 0,
  difficulty: null,
  informativeness: null,
  gpa_boost: null,
  workload: null,
  comment: "",
};

interface ReviewFormProps {
  courseId: number;
  existing: CourseReview | null;
  onSaved: (r: CourseReview) => void;
  onCancel?: () => void;
}

function ReviewForm({ courseId, existing, onSaved, onCancel }: ReviewFormProps) {
  const [form, setForm] = useState<FormState>(
    existing
      ? {
          overall_rating: existing.overall_rating,
          difficulty: existing.difficulty,
          informativeness: existing.informativeness,
          gpa_boost: existing.gpa_boost,
          workload: existing.workload,
          comment: existing.comment ?? "",
        }
      : { ...EMPTY_FORM }
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isValid = form.overall_rating >= 1;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid) return;
    setSubmitting(true);
    setError(null);
    const payload = {
      overall_rating: form.overall_rating,
      difficulty: form.difficulty,
      informativeness: form.informativeness,
      gpa_boost: form.gpa_boost,
      workload: form.workload,
      comment: form.comment.trim() || null,
    };
    try {
      let res: ApiResponse<CourseReview>;
      if (existing) {
        res = await api.put<ApiResponse<CourseReview>>(
          `/courses/catalog/${courseId}/reviews/${existing.id}`,
          payload
        );
      } else {
        res = await api.post<ApiResponse<CourseReview>>(
          `/courses/catalog/${courseId}/reviews`,
          payload
        );
      }
      onSaved(res.data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to submit review.";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-xs font-medium text-text-secondary mb-1.5">
          Overall rating <span className="text-accent-red">*</span>
        </label>
        <StarRating
          value={form.overall_rating}
          onChange={(v) => setForm((f) => ({ ...f, overall_rating: v }))}
          size={22}
        />
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium text-text-secondary">Optional ratings</p>
        {(["difficulty", "informativeness", "gpa_boost", "workload"] as const).map((field) => (
          <SubRatingInput
            key={field}
            field={field}
            value={form[field]}
            onChange={(v) => setForm((f) => ({ ...f, [field]: v }))}
          />
        ))}
      </div>

      <div>
        <label className="block text-xs font-medium text-text-secondary mb-1.5">
          Comment <span className="text-text-muted">(optional)</span>
        </label>
        <textarea
          value={form.comment}
          onChange={(e) => setForm((f) => ({ ...f, comment: e.target.value }))}
          maxLength={2000}
          rows={3}
          placeholder="Share your experience with this course..."
          className="w-full rounded-lg border border-border-primary bg-bg-elevated px-3 py-2 text-sm text-text-primary placeholder:text-text-muted resize-none focus:outline-none focus:border-accent-green/50 transition-colors"
        />
        <p className="text-[10px] text-text-muted mt-0.5 text-right">
          {form.comment.length}/2000
        </p>
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-accent-red/30 bg-accent-red/10 px-3 py-2">
          <AlertCircle size={14} className="text-accent-red shrink-0 mt-0.5" />
          <p className="text-xs text-accent-red">{error}</p>
        </div>
      )}

      <div className="flex gap-2 justify-end">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 text-sm text-text-muted hover:text-text-primary transition-colors"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={!isValid || submitting}
          className="px-4 py-1.5 rounded-lg bg-accent-green/20 text-accent-green text-sm font-medium hover:bg-accent-green/30 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {submitting ? "Submitting..." : existing ? "Update review" : "Submit review"}
        </button>
      </div>
    </form>
  );
}

// ─── Main tab component ───────────────────────────────────────────────────────

export function ReviewsTab({ courseId }: { courseId: number }) {
  const { user } = useAuthStore();
  const [page, setPage] = useState<ReviewsPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(false);

  async function fetchReviews() {
    try {
      const res = await api.get<ApiResponse<ReviewsPage>>(
        `/courses/catalog/${courseId}/reviews?limit=100`
      );
      setPage(res.data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchReviews(); }, [courseId]);

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    );
  }

  const reviews = page?.reviews ?? [];
  const stats = page?.stats;
  const myReview = user ? reviews.find((r) => r.user_id === user.id) ?? null : null;
  const others = reviews.filter((r) => r.user_id !== user?.id);

  function handleSaved(saved: CourseReview) {
    setPage((prev) => {
      if (!prev) return prev;
      const exists = prev.reviews.find((r) => r.id === saved.id);
      const next = exists
        ? prev.reviews.map((r) => (r.id === saved.id ? saved : r))
        : [saved, ...prev.reviews];
      return { ...prev, reviews: next };
    });
    setShowForm(false);
    setEditing(false);
    fetchReviews(); // re-fetch to get updated stats
  }

  async function handleDelete() {
    if (!myReview) return;
    if (!confirm("Delete your review?")) return;
    await api.delete(`/courses/catalog/${courseId}/reviews/${myReview.id}`);
    fetchReviews();
    setEditing(false);
  }

  const subFields = ["difficulty", "informativeness", "gpa_boost", "workload"] as const;

  return (
    <div className="space-y-6">
      {/* Stats summary */}
      {stats && stats.total > 0 && (
        <GlassCard>
          <div className="flex flex-wrap gap-6 items-center">
            <div className="text-center">
              <p className="text-3xl font-bold text-text-primary font-mono">
                {stats.avg_overall_rating?.toFixed(1) ?? "—"}
              </p>
              <AvgStars value={stats.avg_overall_rating ?? null} />
              <p className="text-xs text-text-muted mt-1">
                {stats.total} review{stats.total !== 1 ? "s" : ""}
              </p>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-x-8 gap-y-2 min-w-[200px]">
              {subFields.map((k) => {
                const v = stats[`avg_${k}`];
                return (
                  <div key={k} className="flex items-center justify-between gap-2">
                    <span className="text-xs text-text-muted">{SUB_LABELS[k]}</span>
                    <AvgStars value={v ?? null} />
                  </div>
                );
              })}
            </div>
          </div>
        </GlassCard>
      )}

      {/* My review or form trigger */}
      {myReview && !editing ? (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            Your review
          </p>
          <ReviewCard
            review={myReview}
            isOwn
            onEdit={() => setEditing(true)}
            onDelete={handleDelete}
          />
        </div>
      ) : myReview && editing ? (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            Edit your review
          </p>
          <GlassCard>
            <ReviewForm
              courseId={courseId}
              existing={myReview}
              onSaved={handleSaved}
              onCancel={() => setEditing(false)}
            />
          </GlassCard>
        </div>
      ) : showForm ? (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            Write a review
          </p>
          <GlassCard>
            <ReviewForm
              courseId={courseId}
              existing={null}
              onSaved={handleSaved}
              onCancel={() => setShowForm(false)}
            />
          </GlassCard>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setShowForm(true)}
          className="w-full py-2.5 rounded-lg border border-dashed border-border-primary text-sm text-text-muted hover:border-accent-green/40 hover:text-accent-green transition-colors"
        >
          + Write a review
        </button>
      )}

      {/* Other reviews */}
      {others.length > 0 && (
        <div className="space-y-3">
          {myReview && (
            <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              Other reviews
            </p>
          )}
          {others.map((r) => (
            <ReviewCard
              key={r.id}
              review={r}
              isOwn={false}
              onEdit={() => {}}
              onDelete={() => {}}
            />
          ))}
        </div>
      )}

      {reviews.length === 0 && !showForm && (
        <GlassCard className="flex flex-col items-center py-12">
          <Star size={28} className="text-text-muted mb-3" />
          <p className="text-sm text-text-secondary">No reviews yet — be the first!</p>
        </GlassCard>
      )}
    </div>
  );
}
