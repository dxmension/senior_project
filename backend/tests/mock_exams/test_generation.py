from nutrack.mock_exams.generation import GenerationResult


def test_generation_result_accepts_structured_coverage_summary() -> None:
    result = GenerationResult.model_validate(
        {
            "created_mock_exam_id": 12,
            "reused_question_ids": [1, 2],
            "created_question_ids": [3, 4],
            "coverage_summary": {
                "topics_covered": ["Regularization", "LDA", "Nested CV"],
                "gaps": ["Bias-variance tradeoff"],
                "notes": "Balanced across theory and application.",
            },
            "warnings": [],
        }
    )

    assert result.created_mock_exam_id == 12
    assert "Topics covered:" in result.coverage_summary
    assert "Regularization" in result.coverage_summary
    assert "Gaps:" in result.coverage_summary
