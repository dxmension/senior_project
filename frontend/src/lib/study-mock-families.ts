import type { MockExamListItem } from "@/types";

export type MockExamFamily = {
  key: string;
  assessmentType: string;
  assessmentNumber: number;
  label: string;
  exams: MockExamListItem[];
  mocksCount: number;
  completedAttempts: number;
  latestCreatedAt: string;
  bestScore: number | null;
  latestScore: number | null;
  predictedScore: number | null;
  predictedLetter: string | null;
  hasActiveAttempt: boolean;
  activeAttempt: MockExamListItem["active_attempt"];
};

export function assessmentFamilyLabel(
  assessmentType: string,
  assessmentNumber: number,
) {
  const labels: Record<string, string> = {
    quiz: "Quiz",
    midterm: "Midterm",
    final: "Final",
    homework: "Homework",
    project: "Project",
    lab: "Lab",
    presentation: "Presentation",
    other: "Assessment",
  };
  return `${labels[assessmentType] ?? assessmentType} ${assessmentNumber}`;
}

export function sortMockExams(exams: MockExamListItem[]) {
  return [...exams].sort(
    (left, right) =>
      new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
  );
}

export function groupMockExamFamilies(exams: MockExamListItem[]) {
  const families = new Map<string, MockExamFamily>();
  for (const exam of sortMockExams(exams)) {
    const key = `${exam.assessment_type}:${exam.assessment_number}`;
    const existing = families.get(key);
    if (existing) {
      existing.exams.push(exam);
      existing.mocksCount += 1;
      existing.completedAttempts += exam.completed_attempts;
      existing.bestScore = maxScore(existing.bestScore, exam.best_score_pct);
      existing.latestScore = firstScore(existing.latestScore, exam.latest_score_pct);
      existing.predictedScore = firstScore(
        existing.predictedScore,
        exam.predicted_score_pct,
      );
      existing.predictedLetter = existing.predictedLetter ?? exam.predicted_grade_letter;
      existing.hasActiveAttempt = existing.hasActiveAttempt || exam.has_active_attempt;
      existing.activeAttempt = existing.activeAttempt ?? exam.active_attempt;
      continue;
    }
    families.set(key, {
      key,
      assessmentType: exam.assessment_type,
      assessmentNumber: exam.assessment_number,
      label: assessmentFamilyLabel(
        exam.assessment_type,
        exam.assessment_number,
      ),
      exams: [exam],
      mocksCount: 1,
      completedAttempts: exam.completed_attempts,
      latestCreatedAt: exam.created_at,
      bestScore: exam.best_score_pct,
      latestScore: exam.latest_score_pct,
      predictedScore: exam.predicted_score_pct,
      predictedLetter: exam.predicted_grade_letter,
      hasActiveAttempt: exam.has_active_attempt,
      activeAttempt: exam.active_attempt,
    });
  }
  return [...families.values()].sort(
    (left, right) =>
      new Date(right.latestCreatedAt).getTime() -
      new Date(left.latestCreatedAt).getTime(),
  );
}

export function findMockExamFamily(
  exams: MockExamListItem[],
  assessmentType: string,
  assessmentNumber: number,
) {
  return groupMockExamFamilies(exams).find(
    (family) =>
      family.assessmentType === assessmentType &&
      family.assessmentNumber === assessmentNumber,
  ) ?? null;
}

function maxScore(current: number | null, next: number | null) {
  if (current == null) return next;
  if (next == null) return current;
  return Math.max(current, next);
}

function firstScore(current: number | null, next: number | null) {
  return current ?? next;
}
