"use client";

const LEGEND_ITEMS = [
  { label: "Deadline", color: "#60a5fa" },
  { label: "Personal", color: "#a3e635" },
  { label: "Course", color: "#818cf8" },
  { label: "Midterm/Final", color: "#f87171" },
  { label: "Project", color: "#c084fc" },
  { label: "Quiz", color: "#fb923c" },
  { label: "Lab", color: "#34d399" },
];

export function CalendarLegend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-2">
      {LEGEND_ITEMS.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span
            className="block h-2.5 w-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-xs text-text-secondary">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
