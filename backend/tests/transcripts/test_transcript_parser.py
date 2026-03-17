from nutrack.transcripts.parser import parse_term_year, parse_transcript


def test_parse_term_year_reads_term_and_year() -> None:
    assert parse_term_year("Fall 2025") == ("Fall", 2025)


def test_parse_transcript_returns_structured_term_year() -> None:
    text = """
    Student Name: Doe John
    Primary major: Computer Science
    Admission semester: Fall 2022
    Fall 2025
    CSCI 151 Programming A 6 4.0
    Overall GPA: 3.5 Credits Enrolled: 30 Credits Earned: 24
    """

    result = parse_transcript(text)

    assert result["enrollment_term"] == "Fall"
    assert result["enrollment_year"] == 2022
    assert result["courses"][0]["term"] == "Fall"
    assert result["courses"][0]["year"] == 2025
