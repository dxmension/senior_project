export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  major: string | null;
  study_year: number | null;
  cgpa: number | null;
  total_credits_earned: number | null;
  total_credits_enrolled: number | null;
  is_onboarded: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  is_onboarded: boolean;
}

export interface CourseRecord {
  code: string;
  title: string;
  semester: string;
  grade: string;
  grade_points: number;
  ects: number;
}

export interface ParsedTranscriptData {
  major: string | null;
  gpa: number | null;
  total_credits_earned: number | null;
  total_credits_enrolled: number | null;
  courses: CourseRecord[];
}

export interface TranscriptStatus {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  major: string | null;
  gpa: number | null;
  total_credits_earned: number | null;
  total_credits_enrolled: number | null;
  parsed_data: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string | null;
}

export interface EnrollmentItem {
  id: number;
  course_code: string;
  course_title: string;
  ects: number;
  grade: string | null;
  grade_points: number | null;
  semester: string;
  status: string;
}

export interface CreditsBySemester {
  semester: string;
  term: number;
  credits: number;
}

export interface UserStats {
  total_credits: number;
  completed_courses: number;
  current_gpa: number | null;
  semesters_completed: number;
  credits_by_semester: CreditsBySemester[];
}

export interface ApiResponse<T = null> {
  ok: boolean;
  data: T;
  meta: Record<string, unknown> | null;
}

export interface ApiError {
  ok: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown> | null;
  };
}
