export const LETTER_TO_POINTS: Record<string, number> = {
  "A": 4.0, "A-": 3.67,
  "B+": 3.33, "B": 3.0, "B-": 2.67,
  "C+": 2.33, "C": 2.0, "C-": 1.67,
  "D+": 1.33, "D": 1.0,
  "F": 0.0,
};

// P/F grades — "P" is excluded from GPA, "NP" counts as 0
export const PASS_FAIL_POINTS: Record<string, number | null> = {
  "P": null,  // Pass: does not affect GPA
  "NP": 0.0, // No Pass / Fail: counts as 0
};

export const LETTER_OPTIONS = [
  ...Object.keys(LETTER_TO_POINTS),
  "P",
  "NP",
] as string[];

export function computeGpa(
  items: { ects: number; letter: string | null }[]
): { gpa: number | null; totalEcts: number } {
  const graded = items.filter((i) => {
    if (!i.letter) return false;
    if (LETTER_TO_POINTS[i.letter] !== undefined) return true;
    // NP (No Pass) counts as 0 and affects GPA; P (Pass) is excluded
    return i.letter === "NP";
  });
  const totalEcts = graded.reduce((s, i) => s + i.ects, 0);
  if (totalEcts === 0) return { gpa: null, totalEcts: 0 };
  const weighted = graded.reduce((s, i) => {
    const pts = i.letter === "NP" ? 0.0 : LETTER_TO_POINTS[i.letter!];
    return s + pts * i.ects;
  }, 0);
  return { gpa: weighted / totalEcts, totalEcts };
}

export interface AssessmentSlice {
  score: number | null;
  max_score: number | null;
  weight: number | null;
}

export function computeCurrentGrade(assessments: AssessmentSlice[]) {
  let earned = 0;
  let possible = 0;
  let total = 0;
  for (const a of assessments) {
    if (a.weight == null) continue;
    total += a.weight;
    if (a.score != null && a.max_score != null && a.max_score > 0) {
      possible += a.weight;
      earned += (a.score / a.max_score) * a.weight;
    }
  }
  const pct = possible > 0 ? (earned / possible) * 100 : null;
  return {
    earned: Math.round(earned * 100) / 100,
    possible: Math.round(possible * 100) / 100,
    total,
    pct,
  };
}
