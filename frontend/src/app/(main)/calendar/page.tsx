"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import type { EventInput, DatesSetArg, EventClickArg } from "@fullcalendar/core";
import { AlertCircle } from "lucide-react";

import { useCalendarStore } from "@/stores/calendar";
import { resolveEventColor } from "@/lib/calendar-colors";
import type { CalendarEntry } from "@/types";
import { CalendarToolbar } from "@/components/calendar/calendar-toolbar";
import { CalendarLegend } from "@/components/calendar/calendar-legend";
import { EventPopup } from "@/components/calendar/event-popup";
import { Spinner } from "@/components/ui/spinner";

function toFullCalendarEvent(entry: CalendarEntry): EventInput {
  const colors = resolveEventColor(entry);
  const isCompleted = entry.source_meta.is_completed === true;
  return {
    id: String(entry.id) + "_" + entry.event_type,
    title: entry.title,
    start: entry.start_at,
    end: entry.end_at ?? undefined,
    allDay: entry.is_all_day,
    backgroundColor: colors.bg,
    borderColor: colors.border,
    textColor: colors.text,
    extendedProps: { entry },
    classNames: isCompleted ? ["fc-event-completed"] : [],
  };
}

export default function CalendarPage() {
  const { entries, isLoading, error, fetchEntries } = useCalendarStore();
  const calendarRef = useRef<FullCalendar>(null);
  const lastRangeRef = useRef<{ start: Date; end: Date } | null>(null);

  const [selectedEntry, setSelectedEntry] = useState<CalendarEntry | null>(null);
  const [popupPos, setPopupPos] = useState<{ x: number; y: number } | null>(null);
  const [currentView, setCurrentView] = useState<"dayGridMonth" | "timeGridWeek">("dayGridMonth");
  const [calendarTitle, setCalendarTitle] = useState("");

  const handleDatesSet = useCallback(
    (dateInfo: DatesSetArg) => {
      lastRangeRef.current = { start: dateInfo.start, end: dateInfo.end };
      fetchEntries(dateInfo.start, dateInfo.end);
      setCalendarTitle(
        calendarRef.current?.getApi().view.title ?? ""
      );
    },
    [fetchEntries]
  );

  const handleEventClick = (info: EventClickArg) => {
    const entry = info.event.extendedProps.entry as CalendarEntry;
    const rect = info.el.getBoundingClientRect();
    setSelectedEntry(entry);
    setPopupPos({ x: rect.left, y: rect.bottom + window.scrollY + 8 });
    info.jsEvent.stopPropagation();
  };

  const handleRetry = () => {
    if (lastRangeRef.current) {
      fetchEntries(lastRangeRef.current.start, lastRangeRef.current.end);
    }
  };

  useEffect(() => {
    function handleClick() {
      setSelectedEntry(null);
      setPopupPos(null);
    }
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  const clampedX = popupPos
    ? Math.min(popupPos.x, typeof window !== "undefined" ? window.innerWidth - 336 : popupPos.x)
    : 0;

  return (
    <div className="flex flex-col gap-6 relative">
      <h1 className="text-2xl font-bold text-text-primary">Calendar</h1>

      {/* Legend */}
      <div className="glass-card-sm px-4 py-3">
        <CalendarLegend />
      </div>

      {/* Error banner */}
      {error && (
        <button
          onClick={handleRetry}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#3d1515] border border-[#f87171] text-[#f87171] text-sm hover:bg-[#4a1a1a] transition-colors text-left w-full"
        >
          <AlertCircle size={15} className="flex-shrink-0" />
          <span>Failed to load calendar data — click to retry</span>
        </button>
      )}

      {/* Calendar card */}
      <div className="glass-card p-5 flex flex-col gap-4">
        <CalendarToolbar
          calendarRef={calendarRef}
          currentView={currentView}
          onViewChange={setCurrentView}
          title={calendarTitle}
        />

        <div className="relative">
          {isLoading && (
            <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
              <Spinner />
            </div>
          )}
          <div className={isLoading ? "opacity-50 pointer-events-none" : ""}>
            <FullCalendar
              ref={calendarRef}
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView={currentView}
              headerToolbar={false}
              events={entries.map(toFullCalendarEvent)}
              eventClick={handleEventClick}
              datesSet={handleDatesSet}
              height="auto"
              dayMaxEvents={4}
              nowIndicator={true}
              eventDisplay="block"
              firstDay={1}
            />
          </div>
        </div>
      </div>

      {/* Event popup */}
      {selectedEntry && popupPos && (
        <EventPopup
          entry={selectedEntry}
          position={{ x: clampedX, y: popupPos.y }}
          onClose={() => {
            setSelectedEntry(null);
            setPopupPos(null);
          }}
        />
      )}
    </div>
  );
}
