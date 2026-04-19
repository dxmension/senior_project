export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  major: string | null;
  kazakh_level: string | null;
  study_year: number | null;
  enrollment_year: number | null;
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
  catalog_course_id: number;
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
  ineligibility_reason: string | null;
  user_priority: number | null;
  credits_us: number | null;
  pass_grade: string | null;
  avg_gpa: number | null;
  avg_review_rating: number | null;
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

export interface HandbookUploadResult {
  id: number;
  enrollment_year: number;
  filename: string;
  status: "processing" | "completed" | "failed";
  created_at: string;
}

export interface HandbookStatus {
  id: number;
  enrollment_year: number;
  filename: string;
  status: "processing" | "completed" | "failed";
  majors_parsed: string[];
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface MatchedCourse {
  code: string;
  status: "passed" | "in_progress";
}

export interface AuditRequirement {
  name: string;
  required_count: number;
  completed_count: number;
  in_progress_count: number;
  status: "completed" | "in_progress" | "missing";
  matched_courses: MatchedCourse[];
  ects_per_course: number;
  note: string;
  terms_available: string[];
}

export interface AuditCategory {
  name: string;
  requirements: AuditRequirement[];
  total_ects: number;
  completed_ects: number;
}

export interface AuditResult {
  major: string;
  supported: boolean;
  total_ects: number;
  completed_ects: number;
  in_progress_ects: number;
  actual_credits_earned: number;
  categories: AuditCategory[];
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

export type MockExamOrigin = "manual" | "ai";

export interface Assessment {
  id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  assessment_type: AssessmentType;
  assessment_number: number;
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
  assessment_number: number;
  description?: string;
  deadline: string;
  weight?: number;
  max_score?: number;
}

export interface DeadlineDotItem {
  assessment_id: number;
  title: string;
  assessment_type: string;
  deadline: string;
  is_completed: boolean;
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
  deadline_dots: DeadlineDotItem[];
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

export interface UpdateAssessmentPayload {
  assessment_type?: AssessmentType;
  assessment_number?: number;
  description?: string;
  deadline?: string;
  weight?: number;
  score?: number;
  max_score?: number;
  is_completed?: boolean;
}

export interface MockExamGenerationQueued {
  job_id: number;
  status: string;
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

export type MaterialUploadStatus =
  | "queued"
  | "uploading"
  | "completed"
  | "failed";

export type MaterialCurationStatus =
  | "not_requested"
  | "pending"
  | "published"
  | "rejected";

export interface StudyMaterialUpload {
  id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  week: number;
  original_filename: string;
  content_type: string;
  file_size_bytes: number;
  upload_status: MaterialUploadStatus;
  curation_status: MaterialCurationStatus;
  publish_requested: boolean;
  error_message: string | null;
  is_published: boolean;
  download_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface SharedCourseMaterial {
  id: number;
  upload_id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  week: number;
  title: string;
  original_filename: string;
  content_type: string;
  file_size_bytes: number;
  download_url: string | null;
  is_owned_by_current_user: boolean;
  published_at: string;
}

export interface MindmapNode {
  id: string;
  label: string;
  description?: string;
  children: MindmapNode[];
}

export interface SavedMindmap {
  id: number;
  course_id: number;
  week: number;
  topic: string;
  root: MindmapNode;
  created_at: string;
}

export interface MindmapGenerationQueued {
  task_id: string;
  status: "queued";
}

export interface MindmapGenerationStatus {
  task_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  mindmap: SavedMindmap | null;
  error_message: string | null;
}

export interface AdminMaterialUpload {
  id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  uploader_id: number;
  uploader_name: string;
  uploader_email: string;
  user_week: number;
  shared_week: number | null;
  shared_title: string | null;
  original_filename: string;
  content_type: string;
  file_size_bytes: number;
  upload_status: MaterialUploadStatus;
  curation_status: MaterialCurationStatus;
  error_message: string | null;
  download_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface MockExamListItem {
  id: number;
  assessment_number: number;
  title: string;
  assessment_type: AssessmentType;
  origin: MockExamOrigin;
  version: number;
  question_count: number;
  time_limit_minutes: number | null;
  created_at: string;
  sources: MockExamSourceSummary[];
  best_score_pct: number | null;
  average_score_pct: number | null;
  latest_score_pct: number | null;
  predicted_score_pct: number | null;
  predicted_grade_letter: string | null;
  attempts_count: number;
  completed_attempts: number;
  has_active_attempt: boolean;
  active_attempt: MockExamAttemptSummary | null;
}

export interface MockExamAssessmentPrediction {
  assessment_type: AssessmentType;
  predicted_score_pct: number | null;
  predicted_grade_letter: string | null;
}

export interface MockExamCourseGroup {
  course_id: number;
  course_code: string;
  course_title: string;
  predicted_score_pct: number | null;
  predicted_grade_letter: string | null;
  assessment_predictions: MockExamAssessmentPrediction[];
  exams: MockExamListItem[];
}

export interface MockExamAttempt {
  id: number;
  status: "in_progress" | "completed" | "abandoned";
  started_at: string;
  submitted_at: string | null;
  expires_at: string | null;
  remaining_seconds: number | null;
  last_active_at: string;
  current_position: number;
  answered_count: number;
  correct_count: number;
  score_pct: number | null;
}

export interface MockExamAttemptAnswer {
  id: number;
  mock_exam_question_link_id: number;
  selected_option_index: number | null;
  is_correct: boolean | null;
  answered_at: string | null;
}

export interface MockExamTrendPoint {
  date_label: string;
  best_score_pct: number;
}

export type MockExamQuestionSource =
  | "ai"
  | "historic"
  | "rumored"
  | "tutor_made";

export interface MockExamSourceSummary {
  source: MockExamQuestionSource;
  label: string;
}

export interface MockExamQuestionItem {
  id: number;
  course_id: number;
  source: MockExamQuestionSource;
  source_label: string;
  historical_course_offering_id: number | null;
  historical_course_offering_label: string | null;
  question_text: string;
  answer_variant_1: string;
  answer_variant_2: string;
  answer_variant_3: string | null;
  answer_variant_4: string | null;
  answer_variant_5: string | null;
  answer_variant_6: string | null;
  correct_option_index: number;
  explanation: string | null;
  created_at: string;
  updated_at: string;
}

export interface MockExamQuestionLink {
  id: number;
  position: number;
  points: number;
  question: MockExamQuestionItem;
}

export interface MockExamQuestionStudentItem {
  id: number;
  course_id: number;
  source: MockExamQuestionSource;
  source_label: string;
  historical_course_offering_id: number | null;
  historical_course_offering_label: string | null;
  question_text: string;
  answer_variant_1: string;
  answer_variant_2: string;
  answer_variant_3: string | null;
  answer_variant_4: string | null;
  answer_variant_5: string | null;
  answer_variant_6: string | null;
}

export interface MockExamQuestionStudentLink {
  id: number;
  position: number;
  points: number;
  question: MockExamQuestionStudentItem;
}

export interface MockExamReviewQuestion {
  id: number;
  position: number;
  points: number;
  selected_option_index: number | null;
  is_correct: boolean | null;
  question: MockExamQuestionItem;
}

export interface MockExamAttemptSummary {
  id: number;
  status: "in_progress" | "completed" | "abandoned";
  score_pct: number | null;
  started_at: string;
  submitted_at: string | null;
  expires_at: string | null;
  remaining_seconds: number | null;
}

export interface MockExamDashboard {
  id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  assessment_type: AssessmentType;
  assessment_number: number;
  title: string;
  version: number;
  question_count: number;
  time_limit_minutes: number | null;
  instructions: string | null;
  created_at: string;
  sources: MockExamSourceSummary[];
  attempts_count: number;
  best_score_pct: number | null;
  average_score_pct: number | null;
  latest_score_pct: number | null;
  predicted_score_pct: number | null;
  predicted_grade_letter: string | null;
  improvement_pct: number | null;
  active_attempt: MockExamAttempt | null;
  attempts: MockExamAttemptSummary[];
  trend: MockExamTrendPoint[];
}

export interface MockExamAttemptSession extends MockExamAttempt {
  mock_exam_id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  assessment_type: AssessmentType;
  assessment_number: number;
  title: string;
  question_count: number;
  time_limit_minutes: number | null;
  instructions: string | null;
  questions: MockExamQuestionStudentLink[];
  answers: MockExamAttemptAnswer[];
}

export interface MockExamAttemptReview extends MockExamAttempt {
  mock_exam_id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  assessment_type: AssessmentType;
  assessment_number: number;
  title: string;
  question_count: number;
  time_limit_minutes: number | null;
  instructions: string | null;
  review_questions: MockExamReviewQuestion[];
}

export interface AdminCourseOffering {
  id: number;
  course_id: number;
  term: string;
  year: number;
  section: string | null;
  meeting_time: string | null;
  room: string | null;
}

export interface AdminMockExamItem {
  id: number;
  course_id: number;
  course_code: string;
  course_title: string;
  assessment_type: AssessmentType;
  assessment_number: number;
  title: string;
  version: number;
  is_active: boolean;
  question_count: number;
  time_limit_minutes: number | null;
  instructions: string | null;
  total_attempts: number;
  completed_attempts: number;
  average_score_pct: number | null;
  best_score_pct: number | null;
  active_attempts: number;
  created_at: string;
  updated_at: string;
}

export interface MockExamAdminDetail {
  exam: AdminMockExamItem;
  questions: MockExamQuestionLink[];
}

export interface AdminMockExamQuestion extends MockExamQuestionItem {
  usage_count: number;
}
