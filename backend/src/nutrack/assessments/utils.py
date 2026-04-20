from nutrack.assessments.models import AssessmentType


def assessment_label(
    assessment_type: AssessmentType | str,
    assessment_number: int,
) -> str:
    value = assessment_type.value if hasattr(assessment_type, "value") else str(assessment_type)
    labels = {
        "quiz": "Quiz",
        "midterm": "Midterm",
        "final": "Final",
        "homework": "Homework",
        "project": "Project",
        "lab": "Lab",
        "presentation": "Presentation",
        "other": "Assessment",
    }
    prefix = labels.get(value, value.replace("_", " ").title())
    return f"{prefix} {assessment_number}"


def mock_exam_title(
    assessment_type: AssessmentType | str,
    assessment_number: int,
    version: int,
) -> str:
    return f"{assessment_label(assessment_type, assessment_number)} Mock {version}"
