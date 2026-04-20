"use client";

import { useRef, useState, useCallback } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import type { EventInput, DatesSetArg, EventHoveringArg, EventSourceFuncArg, EventClickArg } from "@fullcalendar/core";
import { AlertCircle, Plus } from "lucide-react";

import { api } from "@/lib/api";
import { resolveEventColor } from "@/lib/calendar-colors";
import type { CalendarEntry, ApiResponse } from "@/types";
import { CalendarToolbar } from "@/components/calendar/calendar-toolbar";
import { CalendarLegend } from "@/components/calendar/calendar-legend";
import { EventPopup } from "@/components/calendar/event-popup";
import { Spinner } from "@/components/ui/spinner";
import { AddEventModal } from "@/components/calendar/add-event-modal";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

function clampToSixPm(isoString: string): string {
  const d = new Date(isoString);
  const h = d.getHours();
  const m = d.getMinutes();
  if (h > 18 || (h === 18 && m > 0)) {
    d.setHours(18, 0, 0, 0);
  }
  return d.toISOString();
}

function toFullCalendarEvent(entry: CalendarEntry): EventInput {
  const colors = resolveEventColor(entry);
  const isCompleted = entry.source_meta.is_completed === true;

  let start = entry.start_at;
  if (entry.event_type === "assessment_deadline") {
    start = clampToSixPm(entry.start_at);
  }

  return {
    id: `${entry.id}_${entry.event_type}_${entry.start_at}`,
    title: entry.title,
    start,
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
  const calendarRef = useRef<FullCalendar>(null);
  const currentViewRef = useRef<"dayGridMonth" | "timeGridWeek">("dayGridMonth");
  const lastRangeRef = useRef<{ start: Date; end: Date } | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<CalendarEntry | null>(null);
  const [popupPos, setPopupPos] = useState<{ x: number; y: number } | null>(null);
  const [currentView, setCurrentView] = useState<"dayGridMonth" | "timeGridWeek">("dayGridMonth");
  const [calendarTitle, setCalendarTitle] = useState("");
  const [addEventOpen, setAddEventOpen] = useState(false);
  const [addModalDate, setAddModalDate] = useState<string | undefined>(undefined);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; title: string } | null>(null);
  const personalEventsRef = useRef<CalendarEntry[]>([]);

  const eventSource = useCallback(
    async (
      fetchInfo: EventSourceFuncArg,
      successCallback: (events: EventInput[]) => void,
      failureCallback: (error: Error) => void
    ) => {
      try {
        const res = await api.get<ApiResponse<CalendarEntry[]>>(
          `/calendar?from_dt=${fetchInfo.start.toISOString()}&to_dt=${fetchInfo.end.toISOString()}`
        );
        const entries = res.data ?? [];
        const view = currentViewRef.current;
        personalEventsRef.current = entries.filter((e) => e.event_type === "personal_event");
        const filtered = entries.filter((e) =>
          view === "timeGridWeek"
            ? true
            : e.event_type === "assessment_deadline"
        );
        successCallback(filtered.map(toFullCalendarEvent));
        setError(null);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to load calendar data";
        setError(msg);
        failureCallback(err instanceof Error ? err : new Error(msg));
      }
    },
    []
  );

  const handleDatesSet = useCallback((dateInfo: DatesSetArg) => {
    lastRangeRef.current = { start: dateInfo.start, end: dateInfo.end };
    setCalendarTitle(calendarRef.current?.getApi().view.title ?? "");
  }, []);

  const handleViewChange = useCallback((view: "dayGridMonth" | "timeGridWeek") => {
    currentViewRef.current = view;
    setCurrentView(view);
    // Refetch events so the new view's filter is applied
    calendarRef.current?.getApi().refetchEvents();
  }, []);

  const handleEventMouseEnter = (info: EventHoveringArg) => {
    const entry = info.event.extendedProps.entry as CalendarEntry;
    const rect = info.el.getBoundingClientRect();
    const POPUP_W = 320;
    const GAP = 10;
    const x =
      rect.right + GAP + POPUP_W <= window.innerWidth
        ? rect.right + GAP
        : rect.left - POPUP_W - GAP;
    const y = Math.min(rect.top, window.innerHeight - 320);
    setSelectedEntry(entry);
    setPopupPos({ x, y });
  };

  const handleEventMouseLeave = () => {
    setSelectedEntry(null);
    setPopupPos(null);
  };

  const handleRetry = () => {
    setError(null);
    calendarRef.current?.getApi().refetchEvents();
  };

  const handleEventClick = useCallback((info: EventClickArg) => {
    const entry = info.event.extendedProps.entry as CalendarEntry;
    if (entry.event_type === "personal_event") {
      setDeleteTarget({ id: entry.id, title: entry.title });
    }
  }, []);

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      await api.delete(`/events/${deleteTarget.id}`);
      calendarRef.current?.getApi().refetchEvents();
    } catch {
      // silently ignore — calendar will still refetch
    } finally {
      setDeleteTarget(null);
    }
  };

  return (
    <div className="flex flex-col gap-6 relative">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Calendar</h1>
        <button
          type="button"
          onClick={() => {
            setAddModalDate(new Date().toISOString().slice(0, 10));
            setAddEventOpen(true);
          }}
          className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold rounded-lg bg-accent-green text-bg-primary hover:opacity-90 transition-opacity"
        >
          <Plus size={15} />
          Add event
        </button>
      </div>

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
          onViewChange={handleViewChange}
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
              events={eventSource}
              loading={(loading) => setIsLoading(loading)}
              dayHeaderContent={(args) => {
                const d = args.date;
                const weekday = d.toLocaleDateString("en-US", { weekday: "short" }).toUpperCase();
                if (args.view.type === "dayGridMonth") return weekday;
                const day = String(d.getDate()).padStart(2, "0");
                const month = String(d.getMonth() + 1).padStart(2, "0");
                return `${weekday} ${day}.${month}`;
              }}
              eventMouseEnter={handleEventMouseEnter}
              eventMouseLeave={handleEventMouseLeave}
              eventClick={handleEventClick}
              datesSet={handleDatesSet}
              height="auto"
              dayMaxEvents={4}
              nowIndicator={true}
              eventDisplay="block"
              firstDay={1}
              slotMinTime="09:00:00"
              slotMaxTime="18:00:00"
              allDaySlot={false}
              slotDuration="01:00:00"
              slotLabelInterval="01:00:00"
              slotLabelFormat={{ hour: "2-digit", minute: "2-digit", hour12: false }}
              eventTimeFormat={{ hour: "2-digit", minute: "2-digit", hour12: false }}
            />
          </div>
        </div>
      </div>

      {/* Event popup */}
      {selectedEntry && popupPos && (
        <EventPopup entry={selectedEntry} position={popupPos} />
      )}

      <AddEventModal
        isOpen={addEventOpen}
        onClose={() => setAddEventOpen(false)}
        onCreated={() => {
          setAddEventOpen(false);
          calendarRef.current?.getApi().refetchEvents();
        }}
        existingPersonalEvents={personalEventsRef.current}
        initialDate={addModalDate}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        title="Delete event"
        message={`Delete "${deleteTarget?.title}"? This cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
