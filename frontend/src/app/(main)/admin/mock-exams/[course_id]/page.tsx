"use client";

import { use } from "react";
import { AlertCircle, Shield } from "lucide-react";

import { MockExamCourseManagement } from "@/components/admin/mock-exam-course-management";
import { useAuthStore } from "@/stores/auth";

type PageParams = Promise<{ course_id: string }>;

export default function AdminMockExamCoursePage({
  params,
}: {
  params: PageParams;
}) {
  const { course_id } = use(params);
  const courseId = Number(course_id);
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-text-secondary">Loading...</p>
      </div>
    );
  }

  if (!user.is_admin) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
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
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <AlertCircle className="text-red-500" size={48} />
        <h1 className="text-xl font-bold text-text-primary">Invalid Course</h1>
        <p className="text-text-secondary">
          The requested course mock exam page could not be opened.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1600px] overflow-x-hidden">
      <MockExamCourseManagement courseId={courseId} view="overview" />
    </div>
  );
}
