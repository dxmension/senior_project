from typing import Dict, Any
import fitz
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def parse_transcript_text(text: str) -> Dict[str, Any]:
    student_info = {
        "student_id": "",
        "name": "",
        "major": "",
        "year_of_study": 1
    }

    courses = []

    major_match = re.search(r'Major:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
    if major_match:
        student_info["major"] = major_match.group(1).strip()

    course_pattern = r'([A-Z]{4})\s+(\d{3})\s+([^\t]+)\s+(Fall|Spring|Summer)\s+(\d{4})\s+([A-F][+-]?)\s+([\d.]+)\s+(\d+)'

    for match in re.finditer(course_pattern, text):
        courses.append({
            "code": f"{match.group(1)} {match.group(2)}",
            "title": match.group(3).strip(),
            "semester": match.group(4),
            "term": f"{match.group(4)} {match.group(5)}",
            "grade": match.group(6),
            "grade_points": float(match.group(7)),
            "ects": int(match.group(8))
        })

    return {
        "success": True,
        "student_info": student_info,
        "courses": courses
    }

def process_transcript_file(file_path: str, file_extension: str) -> Dict[str, Any]:
    try:
        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
            return parse_transcript_text(text)
        else:
            return {
                "success": False,
                "error": "Unsupported file format"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }