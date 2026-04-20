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

// Mirrors backend _is_lecture_type / _RECITATION_TYPES
const RECITATION_TYPES = new Set(["R", "LAB", "LB", "CLB", "PLB", "TUT", "T"]);

function isLectureSection(section: string | null): boolean {
  if (!section) return true;
  const match = section.trim().match(/^\d+([A-Za-z]*)$/);
  if (!match) return true;
  return !RECITATION_TYPES.has(match[1].toUpperCase());
}

interface OfferingGroup {
  componentType: "lecture" | "lab";
  label: string;
  offerings: SelectableOffering[];
}

function groupOfferings(offerings: SelectableOffering[]): OfferingGroup[] {
  const lectures = offerings.filter((o) => isLectureSection(o.section));
  const labs = offerings.filter((o) => !isLectureSection(o.section));
  const groups: OfferingGroup[] = [];
  if (lectures.length > 0) groups.push({ componentType: "lecture", label: "Lecture", offerings: lectures });
  if (labs.length > 0) groups.push({ componentType: "lab", label: "Lab / Recitation", offerings: labs });
  return groups;
}

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
  const [overloadPendingIds, setOverloadPendingIds] = useState<number[] | null>(null);
  const [isSectionDialogOpen, setIsSectionDialogOpen] = useState(false);
  const isRegistered = enrollment !== null;
  const selectableOfferings = useMemo(
    () => buildSelectableOfferings(course, enrollments),
    [course, enrollments],
  );
  const offeringGroups = useMemo(
    () => groupOfferings(selectableOfferings),
    [selectableOfferings],
  );

  async function enrollBatch(ids: number[], overloadAcknowledged = false) {
    if (isSubmitting) return;
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      for (const offeringId of ids) {
        const response = await api.post<ApiResponse<EnrollmentItem>>(
          "/enrollments",
          { course_id: offeringId, course_overload_acknowledged: overloadAcknowledged },
        );
        onEnrollmentCreated(response.data);
      }
    } catch (error) {
      const code = (
        error as Error & {
          response?: { data?: { error?: { code?: string } } };
        }
      )?.response?.data?.error?.code;
      if (code === "ENROLLMENT_CREDITS_EXCEEDED") {
        setOverloadPendingIds(ids);
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
    // Auto-register only if there is exactly one offering and no component split
    if (selectableOfferings.length === 1 && offeringGroups.length === 1) {
      void enrollBatch([selectableOfferings[0].id]);
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

            <div className="space-y-3">
              {offeringGroups.slice(0, 2).map((group) => (
                <div key={group.componentType}>
                  {offeringGroups.length > 1 && (
                    <p className="mb-1 text-xs font-semibold uppercase tracking-[0.18em] text-text-secondary">
                      {group.label}
                    </p>
                  )}
                  <div className="space-y-2">
                    {group.offerings.slice(0, 2).map((offering, index) => (
                      <div
                        key={offering.section ?? `${course.course_id}-${group.componentType}-${index}`}
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
              ))}
            </div>
          </div>
        </GlassCard>
      </button>

      <SectionPickerDialog
        isOpen={isSectionDialogOpen}
        course={course}
        offeringGroups={offeringGroups}
        isSubmitting={isSubmitting}
        onClose={() => setIsSectionDialogOpen(false)}
        onSelect={(ids) => {
          setIsSectionDialogOpen(false);
          void enrollBatch(ids);
        }}
      />

      <ConfirmDialog
        isOpen={overloadPendingIds !== null}
        title="Course overload?"
        message="Adding this course would exceed the 36 ECTS limit. If you've been approved for a course overload up to 42 ECTS, you can proceed."
        confirmLabel="Yes, register it"
        cancelLabel="Cancel"
        variant="default"
        onConfirm={() => {
          const ids = overloadPendingIds!;
          setOverloadPendingIds(null);
          void enrollBatch(ids, true);
        }}
        onCancel={() => setOverloadPendingIds(null)}
      />
    </>
  );
}

function SectionPickerDialog({
  isOpen,
  course,
  offeringGroups,
  isSubmitting,
  onClose,
  onSelect,
}: {
  isOpen: boolean;
  course: RecommendedCourseItem;
  offeringGroups: OfferingGroup[];
  isSubmitting: boolean;
  onClose: () => void;
  onSelect: (offeringIds: number[]) => void;
}) {
  const [selectedIds, setSelectedIds] = useState<Record<string, number>>({});

  useEffect(() => {
    if (!isOpen) setSelectedIds({});
  }, [isOpen]);

  if (!isOpen) return null;

  const allSelected = offeringGroups.every((g) => selectedIds[g.componentType] != null);

  function handleRegister() {
    if (!allSelected) return;
    onSelect(offeringGroups.map((g) => selectedIds[g.componentType]));
  }

  return (
    <div className="fixed inset-0 z-40 overflow-y-auto bg-black/70 p-4 backdrop-blur-sm">
      <button
        type="button"
        onClick={onClose}
        className="absolute inset-0"
        aria-label="Close section picker"
      />
      <div className="flex min-h-full items-center justify-center">
        <div
          className="glass-card relative z-10 my-6 flex w-full max-w-2xl flex-col p-5"
          style={{ maxHeight: "min(90vh, 960px)" }}
        >
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 rounded-full border border-border-primary p-2
              text-text-secondary transition-colors hover:text-text-primary"
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

          <div className="space-y-5 overflow-y-auto pr-1">
            {offeringGroups.map((group) => (
              <div key={group.componentType}>
                {offeringGroups.length > 1 && (
                  <div className="mb-2 flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-text-primary">{group.label}</h4>
                    <span className="rounded-full bg-accent-green/10 px-2 py-0.5 text-xs text-accent-green">
                      Required
                    </span>
                  </div>
                )}
                <div className="space-y-2">
                  {group.offerings.map((offering) => (
                    <SectionOptionCard
                      key={offering.id}
                      offering={offering}
                      isSelected={selectedIds[group.componentType] === offering.id}
                      isSubmitting={isSubmitting}
                      showRadio={true}
                      onSelect={() =>
                        setSelectedIds((prev) => ({
                          ...prev,
                          [group.componentType]: offering.id,
                        }))
                      }
                    />
                  ))}
                </div>
              </div>
            ))}

            <div className="flex justify-end pt-1">
              <button
                type="button"
                onClick={handleRegister}
                disabled={!allSelected || isSubmitting}
                className="rounded-[var(--radius-md)] bg-accent-green px-5 py-2 text-sm
                  font-medium text-bg-base transition-opacity disabled:opacity-40"
              >
                {isSubmitting ? "Registering…" : "Register"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SectionOptionCard({
  offering,
  isSelected = false,
  showRadio = false,
  isSubmitting,
  onSelect,
}: {
  offering: SelectableOffering;
  isSelected?: boolean;
  showRadio?: boolean;
  isSubmitting: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      disabled={isSubmitting || offering.hasConflict}
      onClick={onSelect}
      className={`w-full rounded-2xl border bg-black/10 p-4 text-left transition-colors
        disabled:cursor-not-allowed disabled:opacity-60 ${
          isSelected
            ? "border-accent-green bg-accent-green/5"
            : "border-border-primary hover:border-accent-green/40"
        }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        {showRadio && (
          <div
            className={`h-3.5 w-3.5 shrink-0 rounded-full border-2 transition-colors ${
              isSelected
                ? "border-accent-green bg-accent-green"
                : "border-border-primary bg-transparent"
            }`}
          />
        )}
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
