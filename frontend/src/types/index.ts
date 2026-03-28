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

export interface SectionGpaStats {
  section: string | null;
  term: string;
  year: number;
  faculty: string | null;
  avg_gpa: number | null;
  total_enrolled: number | null;
  grade_distribution: Record<string, number>;
}

export interface ProfessorStats {
  faculty: string;
  sections: SectionGpaStats[];
  avg_gpa: number | null;
  total_enrolled: number;
}

export interface CourseOfferingInfo {
  section: string | null;
  faculty: string | null;
  meeting_time: string | null;
  room: string | null;
  days: string | null;
  enrolled: number | null;
  capacity: number | null;
  term: string;
  year: number;
}

export interface CatalogCourse {
  id: number;
  code: string;
  level: string;
  title: string;
  ects: number;
  department: string | null;
  school: string | null;
  academic_level: string | null;
  description: string | null;
  prerequisites: string | null;
  corequisites: string | null;
  antirequisites: string | null;
  priority_1: string | null;
  priority_2: string | null;
  priority_3: string | null;
  priority_4: string | null;
  is_eligible: boolean | null;
  user_priority: number | null;
  credits_us: number | null;
  pass_grade: string | null;
  avg_gpa: number | null;
  total_enrolled: number | null;
  terms_available: string[];
  sections: SectionGpaStats[];
  professors: ProfessorStats[];
  offerings: CourseOfferingInfo[];
}

export interface PrerequisiteCheck {
  course_code: string;
  required_grade: string | null;
  met: boolean;
  your_grade: string | null;
}

export interface CorequisiteCheck {
  course_code: string;
  met: boolean;
  your_grade: string | null;
  your_status: string | null;
}

export interface AntirequisiteCheck {
  course_code: string;
  blocking: boolean;
  your_grade: string | null;
}

export interface EligibilityResponse {
  course_id: number;
  can_register: boolean;
  prerequisites_met: boolean;
  corequisites_met: boolean;
  antirequisites_blocking: boolean;
  prerequisite_checks: PrerequisiteCheck[];
  corequisite_checks: CorequisiteCheck[];
  antirequisite_checks: AntirequisiteCheck[];
}

export interface ReviewAuthor {
  id: number;
  first_name: string;
  last_name: string;
}

export interface CourseReview {
  id: number;
  course_id: number;
  user_id: number;
  author: ReviewAuthor;
  comment: string | null;
  overall_rating: number;
  difficulty: number | null;
  informativeness: number | null;
  gpa_boost: number | null;
  workload: number | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewStats {
  total: number;
  avg_overall_rating: number | null;
  avg_difficulty: number | null;
  avg_informativeness: number | null;
  avg_gpa_boost: number | null;
  avg_workload: number | null;
}

export interface ReviewsPage {
  stats: ReviewStats;
  reviews: CourseReview[];
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
