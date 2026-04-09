import { create } from "zustand";
import { api } from "@/lib/api";
import type { ApiResponse, CalendarEntry } from "@/types";

interface CalendarState {
  entries: CalendarEntry[];
  isLoading: boolean;
  error: string | null;
  fetchEntries: (fromDt: Date, toDt: Date) => Promise<void>;
}

export const useCalendarStore = create<CalendarState>((set) => ({
  entries: [],
  isLoading: false,
  error: null,

  fetchEntries: async (fromDt, toDt) => {
    set({ isLoading: true, error: null });
    try {
      const res = await api.get<ApiResponse<CalendarEntry[]>>(
        `/calendar?from_dt=${fromDt.toISOString()}&to_dt=${toDt.toISOString()}`
      );
      set({ entries: res.data ?? [], isLoading: false });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load calendar data";
      set({ error: message, isLoading: false });
    }
  },
}));
