"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Brain, Layers, LoaderCircle } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type { ApiResponse, EnrollmentItem } from "@/types";

export default function FlashcardsPage() {
  const [enrollments, setEnrollments] = useState<EnrollmentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void api
      .get<ApiResponse<EnrollmentItem[]>>("/enrollments?status=in_progress")
      .then((res) => setEnrollments(res.data ?? []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner text="Loading courses..." />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="mb-8">
        <h1 className="flex items-center gap-2 text-2xl font-bold text-text-primary">
          <Layers size={22} className="text-accent-green" />
          Flashcards
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          Generate AI flashcards from your course materials and study them.
        </p>
      </div>

      {enrollments.length === 0 ? (
        <GlassCard className="py-16 text-center">
          <Brain size={32} className="mx-auto mb-3 text-text-muted" />
          <p className="font-semibold text-text-primary">No active courses</p>
          <p className="mt-1 text-sm text-text-secondary">
            Enroll in courses to start generating flashcards.
          </p>
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {enrollments.map((e) => (
            <Link
              key={e.course_id}
              href={`/flashcards/${e.course_id}`}
              className="block"
            >
              <GlassCard
                padding={false}
                className="flex items-center justify-between px-5 py-4 transition-all hover:border-accent-green/40 hover:bg-white/[0.04]"
              >
                <div>
                  <p className="font-medium text-text-primary">
                    {e.course_code} — {e.course_title}
                  </p>
                  <p className="mt-0.5 text-xs text-text-muted capitalize">
                    {e.term} {e.year}
                  </p>
                </div>
                <Layers size={16} className="shrink-0 text-text-muted" />
              </GlassCard>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
