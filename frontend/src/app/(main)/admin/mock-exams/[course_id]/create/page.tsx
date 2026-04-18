"use client";

import { use } from "react";
import { useSearchParams } from "next/navigation";
import { AlertCircle, Shield } from "lucide-react";

import { MockExamCourseManagement } from "@/components/admin/mock-exam-course-management";
import { useAuthStore } from "@/stores/auth";

type PageParams = Promise<{ course_id: string }>;

export default function AdminMockExamBuilderPage({
  params,
}: {
  params: PageParams;
}) {
  const { course_id } = use(params);
  const searchParams = useSearchParams();
  const courseId = Number(course_id);
  const examIdParam = searchParams.get("exam_id");
  const editExamId = examIdParam ? Number(examIdParam) : null;
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-text-secondary">Loading...</p>
      </div>
    );
  }

  if (!user.is_admin) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4">
        <Shield className="text-red-500" size={48} />
        <h1 className="text-2xl font-bold text-text-primary">Access Denied</h1>
        <p className="text-text-secondary">
          You do not have permission to access this page.
        </p>
      </div>
    );
  }

  if (!Number.isInteger(courseId) || courseId <= 0) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4">
        <AlertCircle className="text-red-500" size={48} />
        <h1 className="text-xl font-bold text-text-primary">Invalid Course</h1>
        <p className="text-text-secondary">
          The requested mock exam builder could not be opened.
        </p>
      </div>
    );
  }

  if (editExamId != null && (!Number.isInteger(editExamId) || editExamId <= 0)) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4">
        <AlertCircle className="text-red-500" size={48} />
        <h1 className="text-xl font-bold text-text-primary">Invalid Mock Exam</h1>
        <p className="text-text-secondary">
          The requested mock exam version could not be opened.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1600px] overflow-x-hidden">
      <MockExamCourseManagement
        courseId={courseId}
        view="builder"
        editExamId={editExamId}
      />
    </div>
  );
}
