from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from nutrack.assessments.models import AssessmentType
from nutrack.mock_exams.models import (
    MockExamAttemptStatus,
    MockExamGenerationStatus,
    MockExamGenerationTrigger,
    MockExamOrigin,
    MockExamQuestionSource,
)


class MockExamQuestionBase(BaseModel):
    course_id: int
    source: MockExamQuestionSource = MockExamQuestionSource.AI
    historical_course_offering_id: int | None = None
    question_text: str = Field(min_length=1)
    answer_variant_1: str = Field(min_length=1)
    answer_variant_2: str = Field(min_length=1)
    answer_variant_3: str | None = None
    answer_variant_4: str | None = None
    answer_variant_5: str | None = None
    answer_variant_6: str | None = None
    correct_option_index: int = Field(ge=1, le=6)
    explanation: str | None = None

    @field_validator("correct_option_index")
    @classmethod
    def validate_option_index(cls, value: int, info) -> int:
        option = info.data.get(f"answer_variant_{value}")
        if option is None:
            raise ValueError("correct option must point to a non-null answer")
        return value

    @model_validator(mode="after")
    def validate_source(self):
        if self.source != MockExamQuestionSource.HISTORIC:
            if self.historical_course_offering_id is not None:
                raise ValueError("Only historic questions can include an offering")
            return self
        return self


class CreateMockExamQuestionRequest(MockExamQuestionBase):
    pass


class UpdateMockExamQuestionRequest(BaseModel):
    source: MockExamQuestionSource | None = None
    historical_course_offering_id: int | None = None
    question_text: str | None = None
    answer_variant_1: str | None = None
    answer_variant_2: str | None = None
    answer_variant_3: str | None = None
    answer_variant_4: str | None = None
    answer_variant_5: str | None = None
    answer_variant_6: str | None = None
    correct_option_index: int | None = Field(default=None, ge=1, le=6)
    explanation: str | None = None


class MockExamQuestionResponse(MockExamQuestionBase):
    id: int
    source_label: str
    historical_course_offering_label: str | None = None
    created_at: datetime
    updated_at: datetime


class MockExamQuestionAdminResponse(MockExamQuestionResponse):
    usage_count: int


class MockExamSourceSummary(BaseModel):
    source: MockExamQuestionSource
    label: str


class MockExamQuestionStudentResponse(BaseModel):
    id: int
    course_id: int
    source: MockExamQuestionSource
    source_label: str
    historical_course_offering_id: int | None = None
    historical_course_offering_label: str | None = None
    question_text: str
    answer_variant_1: str
    answer_variant_2: str
    answer_variant_3: str | None = None
    answer_variant_4: str | None = None
    answer_variant_5: str | None = None
    answer_variant_6: str | None = None


class MockExamQuestionReviewResponse(MockExamQuestionStudentResponse):
    correct_option_index: int
    explanation: str | None = None


class MockExamQuestionLinkRequest(BaseModel):
    question_id: int
    position: int = Field(ge=1)
    points: int = Field(default=1, ge=1)


class MockExamQuestionLinkResponse(BaseModel):
    id: int
    position: int
    points: int
    question: MockExamQuestionResponse


class MockExamQuestionLinkStudentResponse(BaseModel):
    id: int
    position: int
    points: int
    question: MockExamQuestionStudentResponse


class MockExamReviewQuestionResponse(BaseModel):
    id: int
    position: int
    points: int
    selected_option_index: int | None
    is_correct: bool | None
    question: MockExamQuestionReviewResponse


class CreateMockExamRequest(BaseModel):
    course_id: int
    assessment_type: AssessmentType
    assessment_number: int = Field(ge=1)
    time_limit_minutes: int | None = Field(default=None, ge=1)
    instructions: str | None = None
    is_active: bool = True
    questions: list[MockExamQuestionLinkRequest] = Field(min_length=1)


class UpdateMockExamRequest(BaseModel):
    assessment_number: int | None = Field(default=None, ge=1)
    time_limit_minutes: int | None = Field(default=None, ge=1)
    instructions: str | None = None
    is_active: bool | None = None
    questions: list[MockExamQuestionLinkRequest] | None = None


class MockExamAttemptAnswerResponse(BaseModel):
    id: int
    mock_exam_question_link_id: int
    selected_option_index: int | None
    is_correct: bool | None
    answered_at: datetime | None


class MockExamAttemptResponse(BaseModel):
    id: int
    status: MockExamAttemptStatus
    started_at: datetime
    submitted_at: datetime | None
    expires_at: datetime | None = None
    remaining_seconds: int | None = None
    last_active_at: datetime
    current_position: int
    answered_count: int
    correct_count: int
    score_pct: float | None


class MockExamAttemptDetailResponse(MockExamAttemptResponse):
    mock_exam_id: int
    answers: list[MockExamAttemptAnswerResponse]


class MockExamTrendPoint(BaseModel):
    date_label: str
    best_score_pct: float


class MockExamAttemptSummary(BaseModel):
    id: int
    status: MockExamAttemptStatus
    score_pct: float | None
    started_at: datetime
    submitted_at: datetime | None
    expires_at: datetime | None = None
    remaining_seconds: int | None = None


class MockExamListItem(BaseModel):
    id: int
    assessment_number: int
    title: str
    assessment_type: AssessmentType
    origin: MockExamOrigin
    version: int
    question_count: int
    time_limit_minutes: int | None
    created_at: datetime
    sources: list[MockExamSourceSummary]
    best_score_pct: float | None
    average_score_pct: float | None
    latest_score_pct: float | None
    predicted_score_pct: float | None
    predicted_grade_letter: str | None
    attempts_count: int
    completed_attempts: int
    has_active_attempt: bool
    active_attempt: MockExamAttemptSummary | None = None


class MockExamAssessmentPrediction(BaseModel):
    assessment_type: AssessmentType
    predicted_score_pct: float | None
    predicted_grade_letter: str | None


class MockExamCourseGroup(BaseModel):
    course_id: int
    course_code: str
    course_title: str
    predicted_score_pct: float | None
    predicted_grade_letter: str | None
    assessment_predictions: list[MockExamAssessmentPrediction]
    exams: list[MockExamListItem]


class MockExamDashboardResponse(BaseModel):
    id: int
    course_id: int
    course_code: str
    course_title: str
    assessment_type: AssessmentType
    assessment_number: int
    title: str
    version: int
    question_count: int
    time_limit_minutes: int | None
    instructions: str | None
    created_at: datetime
    sources: list[MockExamSourceSummary]
    attempts_count: int
    best_score_pct: float | None
    average_score_pct: float | None
    latest_score_pct: float | None
    predicted_score_pct: float | None
    predicted_grade_letter: str | None
    improvement_pct: float | None
    active_attempt: MockExamAttemptResponse | None
    attempts: list[MockExamAttemptSummary]
    trend: list[MockExamTrendPoint]


class MockExamAttemptSessionResponse(MockExamAttemptResponse):
    mock_exam_id: int
    course_id: int
    course_code: str
    course_title: str
    assessment_type: AssessmentType
    assessment_number: int
    title: str
    question_count: int
    time_limit_minutes: int | None
    instructions: str | None
    questions: list[MockExamQuestionLinkStudentResponse]
    answers: list[MockExamAttemptAnswerResponse]


class MockExamAttemptReviewResponse(MockExamAttemptResponse):
    mock_exam_id: int
    course_id: int
    course_code: str
    course_title: str
    assessment_type: AssessmentType
    assessment_number: int
    title: str
    question_count: int
    time_limit_minutes: int | None
    instructions: str | None
    review_questions: list[MockExamReviewQuestionResponse]


class FlashcardItem(BaseModel):
    id: int
    question: str
    answer: str


class SaveMockExamAnswerRequest(BaseModel):
    selected_option_index: int | None = Field(default=None, ge=1, le=6)


class AdminMockExamListItem(BaseModel):
    id: int
    course_id: int
    course_code: str
    course_title: str
    assessment_type: AssessmentType
    assessment_number: int
    title: str
    version: int
    is_active: bool
    question_count: int
    time_limit_minutes: int | None
    instructions: str | None
    total_attempts: int
    completed_attempts: int
    average_score_pct: float | None
    best_score_pct: float | None
    active_attempts: int
    created_at: datetime
    updated_at: datetime


class MockExamAdminDetailResponse(BaseModel):
    exam: AdminMockExamListItem
    questions: list[MockExamQuestionLinkResponse]


class AdminCourseOfferingResponse(BaseModel):
    id: int
    course_id: int
    term: str
    year: int
    section: str | None
    meeting_time: str | None
    room: str | None


class MockExamGenerationSettingsInput(BaseModel):
    enabled: bool
    model: str = Field(min_length=1, max_length=64)
    temperature: float = Field(ge=0, le=2)
    question_count: int = Field(ge=1, le=60)
    time_limit_minutes: int | None = Field(default=None, ge=1, le=240)
    max_source_files: int = Field(ge=1, le=20)
    max_source_chars: int = Field(ge=1000, le=200000)
    regeneration_offset_hours: int = Field(ge=1, le=168)
    new_question_ratio: float = Field(ge=0, le=1)
    tricky_question_ratio: float = Field(ge=0, le=1)


class MockExamGenerationSettingsItem(MockExamGenerationSettingsInput):
    id: int
    setting_key: str
    assessment_type: AssessmentType | None
    created_at: datetime
    updated_at: datetime


class MockExamGenerationSettingsResponse(BaseModel):
    default: MockExamGenerationSettingsItem
    quiz: MockExamGenerationSettingsItem
    midterm: MockExamGenerationSettingsItem
    final: MockExamGenerationSettingsItem


class UpdateMockExamGenerationSettingsRequest(BaseModel):
    default: MockExamGenerationSettingsInput
    quiz: MockExamGenerationSettingsInput
    midterm: MockExamGenerationSettingsInput
    final: MockExamGenerationSettingsInput


class MockExamGenerationJobResponse(BaseModel):
    id: int
    assessment_id: int
    user_id: int
    course_offering_id: int
    course_id: int
    assessment_type: AssessmentType
    assessment_number: int
    trigger: MockExamGenerationTrigger
    status: MockExamGenerationStatus
    run_at: datetime
    attempts: int
    celery_task_id: str | None
    error_message: str | None
    generated_mock_exam_id: int | None
    created_at: datetime
    updated_at: datetime
