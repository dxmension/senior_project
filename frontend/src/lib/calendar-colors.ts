import type { CalendarEntry, CalendarEventType } from "@/types";

export const ASSESSMENT_TYPE_COLORS: Record<
  string,
  { bg: string; border: string; text: string }
> = {
  midterm:      { bg: "#3d1515", border: "#f87171", text: "#f87171" },
  final:        { bg: "#3d1515", border: "#f87171", text: "#f87171" },
  project:      { bg: "#1e1535", border: "#c084fc", text: "#c084fc" },
  homework:     { bg: "#0f2035", border: "#60a5fa", text: "#60a5fa" },
  quiz:         { bg: "#2d1a00", border: "#fb923c", text: "#fb923c" },
  lab:          { bg: "#0d2620", border: "#34d399", text: "#34d399" },
  presentation: { bg: "#2a2000", border: "#fbbf24", text: "#fbbf24" },
  other:        { bg: "#1e1e1e", border: "#a0a0a0", text: "#a0a0a0" },
};

export const EVENT_TYPE_COLORS: Record<
  CalendarEventType,
  { bg: string; border: string; text: string }
> = {
  assessment_deadline: { bg: "#0f2035", border: "#60a5fa", text: "#60a5fa" },
  personal_event:      { bg: "#1a2510", border: "#a3e635", text: "#a3e635" },
  course_session:      { bg: "#1a1a2e", border: "#818cf8", text: "#818cf8" },
};

const FALLBACK_COLOR = { bg: "#1e1e1e", border: "#a0a0a0", text: "#a0a0a0" };

export function resolveEventColor(
  entry: CalendarEntry
): { bg: string; border: string; text: string } {
  // Normalise to lowercase in case the API ever changes casing
  const eventType = (entry.event_type as string).toLowerCase();

  if (eventType === "assessment_deadline") {
    const type = (entry.source_meta.assessment_type as string | undefined)?.toLowerCase();
    if (type && ASSESSMENT_TYPE_COLORS[type]) return ASSESSMENT_TYPE_COLORS[type];
  }
  if (eventType === "personal_event" && entry.color) {
    return {
      bg: entry.color + "22",
      border: entry.color,
      text: entry.color,
    };
  }
  return EVENT_TYPE_COLORS[eventType as CalendarEventType] ?? FALLBACK_COLOR;
}
