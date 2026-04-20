import { GlassCard } from "@/components/ui/glass-card";
import { computeCurrentGrade, type AssessmentSlice } from "@/lib/grade-calc";

export function CurrentGradeCard({ assessments }: { assessments: AssessmentSlice[] }) {
  const { earned, possible, total, pct } = computeCurrentGrade(assessments);

  if (possible === 0) return null;

  return (
    <GlassCard padding={false} className="p-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs text-text-muted uppercase tracking-wider">Current grade</p>
          <p className="mt-1 font-mono text-2xl font-bold text-accent-green">
            {earned} / {possible}
          </p>
          {pct != null && (
            <p className="text-xs text-text-muted">{pct.toFixed(1)}% of graded weight</p>
          )}
        </div>
        <div className="text-right text-xs text-text-muted">
          <p>{total}% total weight</p>
          <p>{(total - possible).toFixed(0)}% ungraded</p>
        </div>
      </div>
    </GlassCard>
  );
}
