import type { MockExamFamily, MockExamListItem } from "@/types";

export function sortMockExams(exams: MockExamListItem[]) {
  return [...exams].sort(
    (left, right) =>
      new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
  );
}

export function sortMockExamFamilies(families: MockExamFamily[]) {
  return [...families].sort((left, right) => {
    const rightTime = right.latest_created_at
      ? new Date(right.latest_created_at).getTime()
      : Number.NEGATIVE_INFINITY;
    const leftTime = left.latest_created_at
      ? new Date(left.latest_created_at).getTime()
      : Number.NEGATIVE_INFINITY;
    if (rightTime !== leftTime) return rightTime - leftTime;
    if (left.assessment_type !== right.assessment_type) {
      return left.assessment_type.localeCompare(right.assessment_type);
    }
    return left.assessment_number - right.assessment_number;
  });
}

export function findMockExamFamily(
  families: MockExamFamily[],
  assessmentType: string,
  assessmentNumber: number,
) {
  return families.find((family) => (
    family.assessment_type === assessmentType
    && family.assessment_number === assessmentNumber
  )) ?? null;
}
