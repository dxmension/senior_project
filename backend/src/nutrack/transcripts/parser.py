import io
import re

import pdfplumber

from nutrack.enrollments.models import EnrollmentStatus
from nutrack.semester import normalize_term


def parse_term_year(text: str | None) -> tuple[str, int] | None:
    match = re.search(r"((?:Fall|Spring|Summer)\s+(\d{4}))", text or "")
    if not match:
        return None
    term = normalize_term(match.group(1).split()[0])
    return (term, int(match.group(2)))


def extract_text_from_bytes(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def parse_transcript(text: str) -> dict:
    result: dict = {}

    match = re.search(r"Student Name:\s*(.+)", text)
    result["student_name"] = match.group(1).strip() if match else None

    match = re.search(r"Primary major:\s*(.+)", text)
    result["major"] = match.group(1).strip() if match else None

    match = re.search(r"Admission semester:\s*(.+)", text)
    enrollment_term_year = parse_term_year(match.group(1) if match else None)
    result["enrollment_term"] = (
        enrollment_term_year[0] if enrollment_term_year else None
    )
    result["enrollment_year"] = (
        enrollment_term_year[1] if enrollment_term_year else None
    )

    overall_section = text
    if "Overall" in text:
        overall_section = text[text.rfind("Overall") :]

    match = re.search(
        r"GPA:\s*([\d.]+)\s+"
        r"Credits\s+Enrolled:\s*(\d+)\s+"
        r"Credits\s+Earned:\s*(\d+)",
        overall_section,
    )
    if match:
        result["overall_gpa"] = float(match.group(1))
        result["credits_enrolled"] = int(match.group(2))
        result["credits_earned"] = int(match.group(3))

    semester_pattern = re.compile(r"((?:Fall|Spring|Summer)\s+\d{4})")
    semester_matches = list(semester_pattern.finditer(text))

    course_pattern = re.compile(
        r"([A-Z]{2,4}\s+\d{3})\s+"
        r"(.+?)\s+"
        r"([ABCDFPW][+-]?\*{0,2})\s+"
        r"(\d+)\s+"
        r"([\d.]+|n/a)"
    )

    courses = []
    for match in course_pattern.finditer(text):
        course_pos = match.start()
        current_semester = None
        for semester_match in semester_matches:
            if semester_match.start() < course_pos:
                current_semester = semester_match.group(1)
            else:
                break
        term_year = parse_term_year(current_semester)

        courses.append(
            {
                "term": term_year[0] if term_year else "",
                "year": term_year[1] if term_year else 0,
                "course_code": match.group(1).strip(),
                "course_title": match.group(2).strip(),
                "grade": match.group(3).strip(),
                "ects": int(match.group(4)),
                "grade_points": (
                    None
                    if match.group(5) == "n/a"
                    else float(match.group(5))
                ),
            }
        )

    result["courses"] = courses
    return result


def parse_transcript_from_bytes(file_bytes: bytes) -> dict:
    text = extract_text_from_bytes(file_bytes)
    return parse_transcript(text)


def get_enrollment_status(grade: str | None) -> EnrollmentStatus:
    if not grade:
        return EnrollmentStatus.IN_PROGRESS
    g = grade.strip().upper()
    if g.startswith("W"):
        return EnrollmentStatus.WITHDRAWN
    if g == "NP":  # No Pass (fail in P/F system)
        return EnrollmentStatus.FAILED
    if g.startswith("P"):  # P or PASS
        return EnrollmentStatus.PASSED
    if g.startswith("F"):
        return EnrollmentStatus.FAILED
    if g.startswith("AU"):
        return EnrollmentStatus.AUDIT
    if g.startswith("I"):
        return EnrollmentStatus.INCOMPLETE
    return EnrollmentStatus.PASSED
