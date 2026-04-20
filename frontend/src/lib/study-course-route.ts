import type { EnrollmentItem, MockExamCourseGroup } from "@/types";

function enrollmentForStudyCourse(
  enrollments: EnrollmentItem[],
  studyCourseId: number,
) {
  return (
    enrollments.find((item) => item.course_id === studyCourseId) ??
    enrollments.find((item) => item.catalog_course_id === studyCourseId) ??
    null
  );
}

export function resolveStudyRouteCourseId(
  enrollments: EnrollmentItem[],
  catalogCourseId: number,
) {
  return (
    enrollments.find((item) => item.catalog_course_id === catalogCourseId)?.course_id ??
    catalogCourseId
  );
}

export function findStudyGroupByRouteCourseId(
  groups: MockExamCourseGroup[],
  enrollments: EnrollmentItem[],
  studyCourseId: number,
) {
  const enrollment = enrollmentForStudyCourse(enrollments, studyCourseId);
  if (!enrollment) {
    return groups.find((item) => item.course_id === studyCourseId) ?? null;
  }
  return groups.find((item) => item.course_id === enrollment.catalog_course_id) ?? null;
}
