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
  is_admin: boolean;
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
  term: string;
  year: number;
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
  user_id: number;
  course_id: number;
  course_code: string;
  section: string | null;
  course_title: string;
  ects: number;
  grade: string | null;
  grade_points: number | null;
  term: string;
  year: number;
  status: string;
  meeting_time: string | null;
  room: string | null;
}

export interface CourseOption {
  id: number;
  code: string;
  level: string;
  section: string | null;
  title: string;
  ects: number;
  term: string;
  year: number;
  meeting_time: string | null;
  room: string | null;
}

export interface CreditsBySemester {
  semester: string;
  term: string;
  year: number;
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

export interface UserListItem {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  major: string | null;
  study_year: number | null;
  cgpa: number | null;
  is_onboarded: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface UserDetail extends UserListItem {
  google_id: string;
  total_credits_earned: number | null;
  total_credits_enrolled: number | null;
  avatar_url: string | null;
  updated_at: string;
  enrollment_count: number;
}

export interface DatabaseStats {
  total_users: number;
  total_courses: number;
  total_enrollments: number;
}

export interface AnalyticsOverview {
  total_users: number;
  active_users_last_30_days: number;
  total_courses: number;
  total_course_offerings: number;
  total_enrollments: number;
  users_by_study_year: Record<number, number>;
  users_by_major: Record<string, number>;
}

export interface DatabaseHealth {
  database_connected: boolean;
  redis_connected: boolean;
  database_size_mb: number | null;
}

export interface CourseListItem {
  id: number;
  code: string;
  level: string;
  title: string;
  ects: number;
  department: string | null;
  school: string | null;
}
