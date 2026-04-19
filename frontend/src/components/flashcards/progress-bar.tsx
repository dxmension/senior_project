interface ProgressBarProps {
  current: number;
  total: number;
}

export function ProgressBar({ current, total }: ProgressBarProps) {
  const pct = ((current + 1) / total) * 100;

  return (
    <div className="space-y-1.5">
      <p className="text-xs text-text-secondary">
        Card {current + 1} of {total}
      </p>
      <div className="h-1.5 w-full rounded-full bg-[#2a2a2a]">
        <div
          className="h-1.5 rounded-full bg-accent-green transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
