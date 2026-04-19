def predicted_grade_letter(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 95:
        return "A"
    if score >= 90:
        return "A-"
    if score >= 85:
        return "B+"
    if score >= 80:
        return "B"
    if score >= 75:
        return "B-"
    if score >= 70:
        return "C+"
    if score >= 65:
        return "C"
    if score >= 60:
        return "C-"
    if score >= 55:
        return "D+"
    if score >= 50:
        return "D"
    return "F"


def predicted_score_average(scores: list[float]) -> float | None:
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)
