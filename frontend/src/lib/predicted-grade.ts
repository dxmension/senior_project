type GradeBadge = {
  letter: string;
  scoreLabel: string;
  badgeClass: string;
  textClass: string;
};

const GRADE_STYLES: Record<string, Omit<GradeBadge, "letter" | "scoreLabel">> = {
  A: {
    badgeClass: "bg-emerald-500/18 text-emerald-300 ring-emerald-400/35",
    textClass: "text-emerald-300",
  },
  "A-": {
    badgeClass: "bg-lime-500/18 text-lime-300 ring-lime-400/35",
    textClass: "text-lime-300",
  },
  "B+": {
    badgeClass: "bg-green-500/18 text-green-300 ring-green-400/35",
    textClass: "text-green-300",
  },
  B: {
    badgeClass: "bg-teal-500/18 text-teal-300 ring-teal-400/35",
    textClass: "text-teal-300",
  },
  "B-": {
    badgeClass: "bg-cyan-500/18 text-cyan-300 ring-cyan-400/35",
    textClass: "text-cyan-300",
  },
  "C+": {
    badgeClass: "bg-yellow-500/18 text-yellow-300 ring-yellow-400/35",
    textClass: "text-yellow-300",
  },
  C: {
    badgeClass: "bg-amber-500/18 text-amber-300 ring-amber-400/35",
    textClass: "text-amber-300",
  },
  "C-": {
    badgeClass: "bg-orange-500/18 text-orange-300 ring-orange-400/35",
    textClass: "text-orange-300",
  },
  "D+": {
    badgeClass: "bg-orange-600/18 text-orange-200 ring-orange-500/35",
    textClass: "text-orange-200",
  },
  D: {
    badgeClass: "bg-red-500/18 text-red-300 ring-red-400/35",
    textClass: "text-red-300",
  },
  F: {
    badgeClass: "bg-red-700/20 text-red-200 ring-red-500/35",
    textClass: "text-red-200",
  },
};

function formatScore(score: number | null) {
  if (score == null) return "No data";
  return `${score.toFixed(1).replace(".0", "")}%`;
}

export function predictedGradeBadge(
  letter: string | null,
  score: number | null,
): GradeBadge {
  if (!letter) {
    return {
      letter: "—",
      scoreLabel: formatScore(score),
      badgeClass: "bg-white/[0.05] text-text-secondary ring-white/10",
      textClass: "text-text-secondary",
    };
  }
  const tone = GRADE_STYLES[letter] ?? GRADE_STYLES.F;
  return {
    letter,
    scoreLabel: formatScore(score),
    badgeClass: tone.badgeClass,
    textClass: tone.textClass,
  };
}
