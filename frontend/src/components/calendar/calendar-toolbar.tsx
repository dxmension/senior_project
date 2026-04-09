"use client";

import type FullCalendar from "@fullcalendar/react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface CalendarToolbarProps {
  calendarRef: React.RefObject<FullCalendar | null>;
  currentView: "dayGridMonth" | "timeGridWeek";
  onViewChange: (view: "dayGridMonth" | "timeGridWeek") => void;
  title: string;
}

export function CalendarToolbar({
  calendarRef,
  currentView,
  onViewChange,
  title,
}: CalendarToolbarProps) {
  const api = () => calendarRef.current?.getApi();

  const handlePrev = () => api()?.prev();
  const handleNext = () => api()?.next();
  const handleToday = () => api()?.today();

  const handleViewChange = (view: "dayGridMonth" | "timeGridWeek") => {
    api()?.changeView(view);
    onViewChange(view);
  };

  const btnBase =
    "px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors";
  const activeView = `${btnBase} border-[#a3e635] text-[#a3e635]`;
  const inactiveView = `${btnBase} border-[#2a2a2a] text-[#a0a0a0] hover:border-[#3a3a3a] hover:text-[#f5f5f5]`;

  return (
    <div className="flex items-center justify-between gap-3 flex-wrap">
      <div className="flex items-center gap-2">
        <button
          onClick={handlePrev}
          className="p-1.5 rounded-lg border border-[#2a2a2a] text-[#a0a0a0] hover:border-[#3a3a3a] hover:text-[#f5f5f5] transition-colors"
          aria-label="Previous"
        >
          <ChevronLeft size={16} />
        </button>

        <span className="text-base font-semibold text-text-primary min-w-[160px] text-center">
          {title}
        </span>

        <button
          onClick={handleNext}
          className="p-1.5 rounded-lg border border-[#2a2a2a] text-[#a0a0a0] hover:border-[#3a3a3a] hover:text-[#f5f5f5] transition-colors"
          aria-label="Next"
        >
          <ChevronRight size={16} />
        </button>

        <button
          onClick={handleToday}
          className="px-3 py-1.5 rounded-lg text-sm border border-[#2a2a2a] text-[#a0a0a0] hover:border-[#3a3a3a] hover:text-[#f5f5f5] transition-colors ml-1"
        >
          Today
        </button>
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={() => handleViewChange("dayGridMonth")}
          className={currentView === "dayGridMonth" ? activeView : inactiveView}
        >
          Month
        </button>
        <button
          onClick={() => handleViewChange("timeGridWeek")}
          className={currentView === "timeGridWeek" ? activeView : inactiveView}
        >
          Week
        </button>
      </div>
    </div>
  );
}
