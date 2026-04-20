import { create } from "zustand";
import { api } from "@/lib/api";
import type {
  ApiResponse,
  Assessment,
  CreateAssessmentPayload,
  MockExamGenerationQueued,
  UpdateAssessmentPayload,
} from "@/types";

interface AssessmentsState {
  byCourse: Record<number, Assessment[]>;
  loadingCourseIds: Set<number>;
  fetchForCourse: (courseId: number) => Promise<void>;
  addAssessment: (payload: CreateAssessmentPayload) => Promise<Assessment>;
  updateAssessment: (
    id: number,
    payload: UpdateAssessmentPayload
  ) => Promise<Assessment>;
  generateMockExam: (assessmentId: number) => Promise<MockExamGenerationQueued>;
  deleteAssessment: (id: number, courseId: number) => Promise<void>;
  toggleComplete: (id: number, courseId: number) => Promise<void>;
}

export const useAssessmentsStore = create<AssessmentsState>((set, get) => ({
  byCourse: {},
  loadingCourseIds: new Set(),

  fetchForCourse: async (courseId) => {
    set((s) => ({
      loadingCourseIds: new Set([...s.loadingCourseIds, courseId]),
    }));
    try {
      const res = await api.get<ApiResponse<Assessment[]>>(
        `/assessments?course_id=${courseId}`
      );
      set((s) => ({
        byCourse: { ...s.byCourse, [courseId]: res.data ?? [] },
      }));
    } finally {
      set((s) => {
        const next = new Set(s.loadingCourseIds);
        next.delete(courseId);
        return { loadingCourseIds: next };
      });
    }
  },

  addAssessment: async (payload) => {
    const res = await api.post<ApiResponse<Assessment>>(
      "/assessments",
      payload
    );
    const assessment = res.data;
    set((s) => ({
      byCourse: {
        ...s.byCourse,
        [payload.course_id]: [
          ...(s.byCourse[payload.course_id] ?? []),
          assessment,
        ],
      },
    }));
    return assessment;
  },

  updateAssessment: async (id, payload) => {
    const res = await api.patch<ApiResponse<Assessment>>(
      `/assessments/${id}`,
      payload
    );
    const updated = res.data;
    set((s) => {
      const courseId = updated.course_id;
      return {
        byCourse: {
          ...s.byCourse,
          [courseId]: (s.byCourse[courseId] ?? []).map((a) =>
            a.id === id ? updated : a
          ),
        },
      };
    });
    return updated;
  },

  generateMockExam: async (assessmentId) => {
    const res = await api.post<ApiResponse<MockExamGenerationQueued>>(
      `/assessments/${assessmentId}/generate-mock-exam`
    );
    return res.data;
  },

  deleteAssessment: async (id, courseId) => {
    await api.delete<ApiResponse<null>>(`/assessments/${id}`);
    set((s) => ({
      byCourse: {
        ...s.byCourse,
        [courseId]: (s.byCourse[courseId] ?? []).filter((a) => a.id !== id),
      },
    }));
  },

  toggleComplete: async (id, courseId) => {
    const current = get().byCourse[courseId]?.find((a) => a.id === id);
    if (!current) return;

    // Optimistic update
    set((s) => ({
      byCourse: {
        ...s.byCourse,
        [courseId]: (s.byCourse[courseId] ?? []).map((a) =>
          a.id === id ? { ...a, is_completed: !a.is_completed } : a
        ),
      },
    }));

    try {
      const res = await api.patch<ApiResponse<Assessment>>(
        `/assessments/${id}`,
        { is_completed: !current.is_completed }
      );
      set((s) => ({
        byCourse: {
          ...s.byCourse,
          [courseId]: (s.byCourse[courseId] ?? []).map((a) =>
            a.id === id ? res.data : a
          ),
        },
      }));
    } catch {
      // Revert on error
      set((s) => ({
        byCourse: {
          ...s.byCourse,
          [courseId]: (s.byCourse[courseId] ?? []).map((a) =>
            a.id === id ? current : a
          ),
        },
      }));
    }
  },
}));
