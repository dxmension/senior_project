from datetime import date, datetime

from pydantic import BaseModel


class WorkloadAssessmentItem(BaseModel):
    assessment_id: int
    title: str
    assessment_type: str
    deadline: datetime
    course_code: str
    is_completed: bool


class WeeklyWorkloadItem(BaseModel):
    week_start: date
    week_label: str
    assessment_count: int
    assessments: list[WorkloadAssessmentItem]


class CourseProgressItem(BaseModel):
    course_id: int
    course_code: str
    course_title: str
    term: str
    year: int
    ects: int
    total_assessments: int
    completed_assessments: int
    progress_pct: float
    upcoming_deadline: datetime | None


class UpcomingDeadlineItem(BaseModel):
    assessment_id: int
    title: str
    assessment_type: str
    deadline: datetime
    course_code: str
    course_title: str
    is_completed: bool
    days_until: int


class DashboardResponse(BaseModel):
    current_gpa: float | None
    semester_gpa: float | None
    total_credits_earned: int
    total_credits_enrolled: int
    active_courses_count: int
    completed_courses_count: int
    upcoming_deadlines_count: int
    overdue_count: int
    course_progress: list[CourseProgressItem]
    upcoming_deadlines: list[UpcomingDeadlineItem]
    weekly_workload: list[WeeklyWorkloadItem]


class AISummaryResponse(BaseModel):
    summary: str
    recommendations: list[str]
    motivation: str
    generated_at: datetime
