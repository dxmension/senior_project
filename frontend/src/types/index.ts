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

export type AssessmentType =
  | "homework"
  | "quiz"
  | "midterm"
  | "final"
  | "project"
  | "lab"
  | "presentation"
  | "other";

export interface Assessment {
  id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  assessment_type: AssessmentType;
  title: string;
  description: string | null;
  deadline: string;
  weight: number | null;
  score: number | null;
  max_score: number | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateAssessmentPayload {
  course_id: number;
  assessment_type: AssessmentType;
  title: string;
  description?: string;
  deadline: string;
  weight?: number;
  max_score?: number;
}

export interface CourseProgressItem {
  course_id: number;
  course_code: string;
  course_title: string;
  term: string;
  year: number;
  ects: number;
  total_assessments: number;
  completed_assessments: number;
  progress_pct: number;
  upcoming_deadline: string | null;
}

export interface UpcomingDeadlineItem {
  assessment_id: number;
  title: string;
  assessment_type: string;
  deadline: string;
  course_code: string;
  course_title: string;
  is_completed: boolean;
  days_until: number;
}

export interface WorkloadAssessmentItem {
  assessment_id: number;
  title: string;
  assessment_type: string;
  deadline: string;
  course_code: string;
  is_completed: boolean;
}

export interface WeeklyWorkloadItem {
  week_start: string;
  week_label: string;
  assessment_count: number;
  assessments: WorkloadAssessmentItem[];
}

export interface DashboardData {
  current_gpa: number | null;
  semester_gpa: number | null;
  total_credits_earned: number;
  total_credits_enrolled: number;
  active_courses_count: number;
  completed_courses_count: number;
  upcoming_deadlines_count: number;
  overdue_count: number;
  course_progress: CourseProgressItem[];
  upcoming_deadlines: UpcomingDeadlineItem[];
  weekly_workload: WeeklyWorkloadItem[];
}

export interface AISummaryData {
  summary: string;
  recommendations: string[];
  motivation: string;
  generated_at: string;
}

export interface UpdateAssessmentPayload {
  assessment_type?: AssessmentType;
  title?: string;
  description?: string;
  deadline?: string;
  weight?: number;
  score?: number;
  max_score?: number;
  is_completed?: boolean;
}

export type CalendarEventType =
  | "personal_event"
  | "assessment_deadline"
  | "course_session";

export interface CalendarEntry {
  id: number;
  event_type: CalendarEventType;
  title: string;
  description: string | null;
  start_at: string;
  end_at: string | null;
  is_all_day: boolean;
  location: string | null;
  color: string | null;
  category_name: string | null;
  source_meta: Record<string, unknown>;
}
