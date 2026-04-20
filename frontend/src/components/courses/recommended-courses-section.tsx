"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  CalendarDays,
  GraduationCap,
  MapPin,
  Star,
  X,
} from "lucide-react";

import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api, getApiErrorMessage } from "@/lib/api";
import type {
  ApiResponse,
  EnrollmentItem,
  RecommendedCourseItem,
  RecommendationsResponse,
} from "@/types";

interface RecommendedCoursesSectionProps {
  enrollments: EnrollmentItem[];
  onEnrollmentCreated: (item: EnrollmentItem) => void;
}

interface TimeRange {
  start: number;
  end: number;
}

type RecommendedOffering = RecommendedCourseItem["offerings"][number];

type SelectableOffering = RecommendedOffering & {
  id: number;
  hasConflict: boolean;
  conflictLabel: string | null;
};

export function RecommendedCoursesSection({
  enrollments,
  onEnrollmentCreated,
}: RecommendedCoursesSectionProps) {
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const enrollmentKey = enrollments
    .map((item) => `${item.catalog_course_id}:${item.course_id}`)
    .sort()
    .join("|");

  useEffect(() => {
    async function loadRecommendations() {
      setIsLoading(true);
      try {
        const response = await api.getRecommendedCourses();
        setData(response.data);
        setErrorMessage(null);
      } catch (error) {
        setData(null);
        setErrorMessage(
          getApiErrorMessage(error, "Could not load recommended courses."),
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadRecommendations();
  }, [enrollmentKey]);

  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent-green">
          Recommended Courses
        </p>
        <h2 className="text-xl font-semibold text-text-primary">
          Smart picks for your next registration
        </h2>
        <p className="text-sm text-text-secondary">
          Suggestions combine your audit progress, course priorities,
          prerequisites, and historical GPA trends.
        </p>
      </div>

      {isLoading ? (
        <GlassCard className="py-12">
          <Spinner text="Loading recommendations..." />
        </GlassCard>
      ) : errorMessage ? (
        <GlassCard>
          <p className="text-sm text-accent-red">{errorMessage}</p>
        </GlassCard>
      ) : !data || data.recommendations.length === 0 ? (
        <GlassCard className="space-y-2">
          <p className="text-sm font-semibold text-text-primary">
            No recommendations available yet
          </p>
          <p className="text-sm text-text-secondary">
            We will show suggestions here once your audit and upcoming offerings
            give us enough signal for the next term.
          </p>
        </GlassCard>
      ) : (
        <div className="space-y-4">
          <GlassCard className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-text-primary">
                Recommended for {data.term} {data.year}
              </p>
              <p className="text-sm text-text-secondary">
                {data.recommendations.length} course
                {data.recommendations.length === 1 ? "" : "s"} matched to your
                progress and eligibility.
              </p>
            </div>
          </GlassCard>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {data.recommendations.map((course) => (
              <RecommendedCourseCard
                key={course.course_id}
                course={course}
                enrollments={enrollments}
                enrollment={
                  enrollments.find(
                    (item) => item.catalog_course_id === course.course_id,
                  ) ?? null
                }
                onEnrollmentCreated={onEnrollmentCreated}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function RecommendedCourseCard({
  course,
  enrollments,
  enrollment,
  onEnrollmentCreated,
}: {
  course: RecommendedCourseItem;
  enrollments: EnrollmentItem[];
  enrollment: EnrollmentItem | null;
  onEnrollmentCreated: (item: EnrollmentItem) => void;
}) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [overloadPendingId, setOverloadPendingId] = useState<number | null>(null);
  const [isSectionDialogOpen, setIsSectionDialogOpen] = useState(false);
  const isRegistered = enrollment !== null;
  const selectableOfferings = useMemo(
    () => buildSelectableOfferings(course, enrollments),
    [course, enrollments],
  );

  async function createEnrollment(
    offeringId: number,
    overloadAcknowledged = false,
  ) {
    if (isSubmitting) return;
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const response = await api.post<ApiResponse<EnrollmentItem>>(
        "/enrollments",
        {
          course_id: offeringId,
          course_overload_acknowledged: overloadAcknowledged,
        },
      );
      onEnrollmentCreated(response.data);
    } catch (error) {
      const code = (
        error as Error & {
          response?: { data?: { error?: { code?: string } } };
        }
      )?.response?.data?.error?.code;
      if (code === "ENROLLMENT_CREDITS_EXCEEDED") {
        setOverloadPendingId(offeringId);
        return;
      }
      setErrorMessage(getApiErrorMessage(error, "Failed to register course."));
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleClick() {
    if (isRegistered && enrollment) {
      router.push(`/courses/${enrollment.course_id}`);
      return;
    }
    if (!selectableOfferings.length) {
      setErrorMessage("No offering is available to register right now.");
      return;
    }
    if (selectableOfferings.length === 1) {
      void createEnrollment(selectableOfferings[0].id);
      return;
    }
    setIsSectionDialogOpen(true);
  }

  return (
    <>
      <button
        type="button"
        onClick={handleClick}
        className="block w-full text-left"
      >
        <GlassCard
          padding={false}
          className="h-full overflow-hidden border-border-primary !bg-white/[0.03]
            transition-all duration-200 hover:border-accent-green/40 hover:!bg-white/[0.05]"
        >
          <div className="flex h-full flex-col gap-5 p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-accent-green">
                    {course.code}
                  </span>
                  <span className="rounded-full border border-border-primary px-2 py-0.5 text-[11px] text-text-secondary">
                    {course.level}
                  </span>
                  {course.priority_match ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-accent-green/15 px-2 py-0.5 text-[11px] font-medium text-accent-green">
                      <Star size={10} />
                      Priority match
                    </span>
                  ) : null}
                  <span className="rounded-full border border-border-primary px-2 py-0.5 text-[11px] text-text-secondary">
                    {cardActionLabel(isRegistered, selectableOfferings.length)}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-text-primary">
                  {course.title}
                </h3>
                <p className="text-sm leading-6 text-text-secondary">
                  {course.reason}
                </p>
              </div>
              <ArrowRight
                size={16}
                className="mt-1 shrink-0 text-text-secondary"
              />
            </div>

            <div className="flex flex-wrap gap-2">
              <InfoChip
                icon={<GraduationCap size={12} />}
                label={formatGpa(course.avg_gpa)}
              />
              <InfoChip
                icon={<CalendarDays size={12} />}
                label={`${course.ects} ECTS`}
              />
              {course.department ? <InfoChip label={course.department} /> : null}
            </div>

            {course.description ? (
              <p className="line-clamp-3 text-sm text-text-secondary">
                {course.description}
              </p>
            ) : null}

            {errorMessage ? (
              <p className="text-sm text-accent-red">{errorMessage}</p>
            ) : null}

            <div className="space-y-2">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-secondary">
                Offered sections
              </p>
              <div className="space-y-2">
                {selectableOfferings.slice(0, 3).map((offering, index) => (
                  <div
                    key={offering.section ?? `${course.course_id}-${index}`}
                    className="rounded-2xl border border-border-primary bg-black/10 px-4 py-3"
                  >
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                      <span className="font-medium text-text-primary">
                        {offeringLabel(offering.section)}
                      </span>
                      {offering.faculty ? (
                        <span className="text-text-secondary">{offering.faculty}</span>
                      ) : null}
                    </div>
                    <p className="mt-1 text-sm text-text-secondary">
                      {formatOfferingDetails(offering)}
                    </p>
                    {offering.conflictLabel ? (
                      <p className="mt-2 text-xs text-accent-red">
                        Conflicts with {offering.conflictLabel}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </GlassCard>
      </button>

      <SectionPickerDialog
        isOpen={isSectionDialogOpen}
        course={course}
        offerings={selectableOfferings}
        isSubmitting={isSubmitting}
        onClose={() => setIsSectionDialogOpen(false)}
        onSelect={(offeringId) => {
          setIsSectionDialogOpen(false);
          void createEnrollment(offeringId);
        }}
      />

      <ConfirmDialog
        isOpen={overloadPendingId !== null}
        title="Course overload?"
        message="Adding this course would exceed the 36 ECTS limit. If you've been approved for a course overload up to 42 ECTS, you can proceed."
        confirmLabel="Yes, register it"
        cancelLabel="Cancel"
        variant="default"
        onConfirm={() => {
          const id = overloadPendingId!;
          setOverloadPendingId(null);
          void createEnrollment(id, true);
        }}
        onCancel={() => setOverloadPendingId(null)}
      />
    </>
  );
}

function SectionPickerDialog({
  isOpen,
  course,
  offerings,
  isSubmitting,
  onClose,
  onSelect,
}: {
  isOpen: boolean;
  course: RecommendedCourseItem;
  offerings: SelectableOffering[];
  isSubmitting: boolean;
  onClose: () => void;
  onSelect: (offeringId: number) => void;
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-40 overflow-y-auto bg-black/70 p-4 backdrop-blur-sm"
    >
      <button
        type="button"
        onClick={onClose}
        className="absolute inset-0"
        aria-label="Close section picker"
      />
      <div className="flex min-h-full items-center justify-center">
        <div
          className="glass-card relative z-10 my-6 flex w-full max-w-2xl
            flex-col p-5"
          style={{ maxHeight: "min(90vh, 960px)" }}
        >
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 rounded-full border border-border-primary p-2 text-text-secondary transition-colors hover:text-text-primary"
          aria-label="Close section picker"
        >
          <X size={16} />
        </button>

        <div className="mb-4 space-y-1 pr-10">
          <p className="font-mono text-xs font-semibold text-accent-green">
            {course.code} {course.level}
          </p>
          <h3 className="text-lg font-semibold text-text-primary">
            Choose a section to register
          </h3>
          <p className="text-sm text-text-secondary">{course.title}</p>
        </div>

        <div className="space-y-3 overflow-y-auto pr-1">
          {offerings.map((offering) => (
            <SectionOptionCard
              key={offering.id}
              offering={offering}
              isSubmitting={isSubmitting}
              onSelect={onSelect}
            />
          ))}
        </div>
      </div>
      </div>
    </div>
  );
}

function SectionOptionCard({
  offering,
  isSubmitting,
  onSelect,
}: {
  offering: SelectableOffering;
  isSubmitting: boolean;
  onSelect: (offeringId: number) => void;
}) {
  return (
    <button
      type="button"
      disabled={isSubmitting || offering.hasConflict}
      onClick={() => onSelect(offering.id)}
      className="w-full rounded-2xl border border-border-primary bg-black/10 p-4 text-left transition-colors hover:border-accent-green/40 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-semibold text-text-primary">
          {offeringLabel(offering.section)}
        </span>
        {offering.hasConflict ? (
          <span className="rounded-full bg-accent-red/15 px-2 py-0.5 text-[11px] font-medium text-accent-red">
            Time clash
          </span>
        ) : (
          <span className="rounded-full bg-accent-green/15 px-2 py-0.5 text-[11px] font-medium text-accent-green">
            Available
          </span>
        )}
      </div>
      <p className="mt-2 text-sm text-text-secondary">
        {formatOfferingDetails(offering)}
      </p>
      {offering.faculty ? (
        <p className="mt-1 text-sm text-text-secondary">{offering.faculty}</p>
      ) : null}
      {offering.room ? (
        <p className="mt-1 inline-flex items-center gap-1 text-xs text-text-secondary">
          <MapPin size={12} />
          {offering.room}
        </p>
      ) : null}
      {offering.conflictLabel ? (
        <p className="mt-2 text-sm text-accent-red">
          Conflicts with {offering.conflictLabel}.
        </p>
      ) : null}
    </button>
  );
}

function InfoChip({
  label,
  icon,
}: {
  label: string;
  icon?: ReactNode;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border-primary px-3 py-1 text-xs text-text-secondary">
      {icon}
      {label}
    </span>
  );
}

function formatGpa(avgGpa: number | null): string {
  if (avgGpa == null) {
    return "Avg GPA unavailable";
  }
  return `Avg GPA ${avgGpa.toFixed(2)}`;
}

function formatOfferingDetails(offering: RecommendedOffering): string {
  const enrollment = formatEnrollment(offering.enrolled, offering.capacity);
  return [offering.days, offering.meeting_time, offering.room, enrollment]
    .filter(Boolean)
    .join(" | ");
}

function formatEnrollment(
  enrolled: number | null,
  capacity: number | null,
): string | null {
  if (enrolled == null && capacity == null) {
    return null;
  }
  if (enrolled != null && capacity != null) {
    return `${enrolled}/${capacity} enrolled`;
  }
  if (enrolled != null) {
    return `${enrolled} enrolled`;
  }
  return `Capacity ${capacity}`;
}

function buildSelectableOfferings(
  course: RecommendedCourseItem,
  enrollments: EnrollmentItem[],
): SelectableOffering[] {
  return course.offering_ids
    .map((id, index) => buildSelectableOffering(id, course.offerings[index], enrollments))
    .filter((item): item is SelectableOffering => item !== null);
}

function buildSelectableOffering(
  id: number | undefined,
  offering: RecommendedOffering | undefined,
  enrollments: EnrollmentItem[],
): SelectableOffering | null {
  if (!id || !offering) {
    return null;
  }
  const conflict = findClashingEnrollment(offering, enrollments);
  return {
    ...offering,
    id,
    hasConflict: conflict !== null,
    conflictLabel: conflict ? conflictTitle(conflict) : null,
  };
}

function findClashingEnrollment(
  offering: RecommendedOffering,
  enrollments: EnrollmentItem[],
): EnrollmentItem | null {
  return enrollments.find((item) => offeringsClash(offering, item)) ?? null;
}

function offeringsClash(
  recommended: RecommendedOffering,
  current: EnrollmentItem,
): boolean {
  const left = parseTimeRange(recommended.meeting_time);
  const right = parseTimeRange(current.meeting_time);
  const leftDays = parseDays(recommended.days);
  const rightDays = parseDays(current.days);

  if (!left || !right || !leftDays.length || !rightDays.length) {
    return false;
  }
  return hasDayOverlap(leftDays, rightDays)
    && left.start < right.end
    && right.start < left.end;
}

function parseTimeRange(value: string | null): TimeRange | null {
  if (!value?.includes("-")) {
    return null;
  }
  const [startText, endText] = value.split("-").map((part) => part.trim());
  const start = parseTimeValue(startText);
  const end = parseTimeValue(endText);
  if (start == null || end == null) {
    return null;
  }
  return { start, end };
}

function parseTimeValue(value: string): number | null {
  const match = value.match(/^(\d{1,2}):(\d{2})(?:\s*([AP]M))?$/i);
  if (!match) {
    return null;
  }
  let hour = Number(match[1]);
  const minute = Number(match[2]);
  const suffix = match[3]?.toUpperCase();
  if (suffix) {
    if (hour === 12) {
      hour = 0;
    }
    if (suffix === "PM") {
      hour += 12;
    }
  }
  return hour * 60 + minute;
}

function parseDays(value: string | null): string[] {
  if (!value) {
    return [];
  }
  const normalized = value.trim().toUpperCase();
  if (!normalized || normalized.includes("ONLINE")) {
    return [];
  }
  const compact = normalized.replace(/\s+/g, "");
  return compact.match(/TH|SU|SA|[MTWRFSU]/g) ?? [];
}

function hasDayOverlap(left: string[], right: string[]): boolean {
  return left.some((day) => right.includes(day));
}

function conflictTitle(enrollment: EnrollmentItem): string {
  return [enrollment.course_code, sectionText(enrollment.section)]
    .filter(Boolean)
    .join(" ");
}

function cardActionLabel(
  isRegistered: boolean,
  offeringCount: number,
): string {
  if (isRegistered) {
    return "Open course";
  }
  return offeringCount > 1 ? "Choose section" : "Register";
}

function offeringLabel(section: string | null): string {
  return sectionText(section) ?? "Section TBA";
}

function sectionText(section: string | null): string | null {
  if (!section) {
    return null;
  }
  return `Section ${section}`;
}
