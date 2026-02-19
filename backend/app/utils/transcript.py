import io
import re
import pdfplumber

from app.models.enrollment import EnrollmentStatus


def extract_text_from_bytes(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def parse_transcript(text: str) -> dict:
    result = {}

    # name
    m = re.search(r"Student Name:\s*(.+)", text)
    result["student_name"] = m.group(1).strip() if m else None

    # Major
    m = re.search(r"Primary major:\s*(.+)", text)
    result["major"] = m.group(1).strip() if m else None

    # Enrollment semester
    m = re.search(r"Admission semester:\s*(.+)", text)
    result["enrollment_semester"] = m.group(1).strip() if m else None

    # Overall GPA, credits enrolled, credits earned (from the "Overall" section at the end)
    overall_section = text[text.rfind("Overall") :] if "Overall" in text else text
    m = re.search(
        r"GPA:\s*([\d.]+)\s+Credits\s+Enrolled:\s*(\d+)\s+Credits\s+Earned:\s*(\d+)",
        overall_section,
    )
    if m:
        result["overall_gpa"] = float(m.group(1))
        result["credits_enrolled"] = int(m.group(2))
        result["credits_earned"] = int(m.group(3))

    # Find all semester headers and their positions
    semester_pattern = re.compile(r"((?:Fall|Spring|Summer)\s+\d{4})")
    semester_matches = list(semester_pattern.finditer(text))

    # Course pattern
    # Matches patterns like: CSCI 151 Programming for Scientists and Engineers B+ 8 3.33
    # Grade can be: A/A-/B+/B/B-/C+/C/C-/D+/D/D**/F/P/W/W*
    course_pattern = re.compile(
        r"([A-Z]{2,4}\s+\d{3})\s+"  # course code (e.g. CSCI 151)
        r"(.+?)\s+"  # course title (non-greedy)
        r"([ABCDFPW][+-]?\*{0,2})\s+"  # grade
        r"(\d+)\s+"  # credits (ECTS)
        r"([\d.]+|n/a)"  # grade points
    )

    courses = []
    for match in course_pattern.finditer(text):
        # Determine which semester this course belongs to by finding
        # the last semester header that appears before this course
        course_pos = match.start()
        current_semester = None
        for sem_match in semester_matches:
            if sem_match.start() < course_pos:
                current_semester = sem_match.group(1)
            else:
                break

        courses.append(
            {
                "semester": current_semester,
                "course_code": match.group(1).strip(),
                "course_title": match.group(2).strip(),
                "grade": match.group(3).strip(),
                "credits_ects": int(match.group(4)),
                "grade_points": None
                if match.group(5) == "n/a"
                else float(match.group(5)),
            }
        )

    result["courses"] = courses
    return result


def parse_transcript_from_bytes(file_bytes: bytes) -> dict:
    text = extract_text_from_bytes(file_bytes)
    return parse_transcript(text)


def get_enrollment_status(grade: str) -> EnrollmentStatus:
    if grade.startswith("W"):
        return EnrollmentStatus.WITHDRAWN
    elif grade.startswith("P"):
        return EnrollmentStatus.PASSED
    elif grade.startswith("F"):
        return EnrollmentStatus.FAILED
    elif grade.startswith("AU"):
        return EnrollmentStatus.AUDIT
    elif grade.startswith("I"):
        return EnrollmentStatus.INCOMPLETE
    # TODO:  come up with proper implementeation of pass grades (e.g course can have two pass grades based on major, prerequisites)
    elif grade[0] not in ["W", "F", "AU", "I", "IP", "AW"]:
        return EnrollmentStatus.PASSED
