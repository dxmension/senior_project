from types import SimpleNamespace

import pytest

from nutrack.study_helper.exceptions import StudyGuideNoMaterialsError
from nutrack.study_helper import service as study_helper_service


@pytest.mark.asyncio
async def test_generate_overview_requires_materials() -> None:
    with pytest.raises(StudyGuideNoMaterialsError):
        await study_helper_service._generate_overview("Pointers", "")  # noqa: SLF001


@pytest.mark.asyncio
async def test_generate_week_summary_requires_materials() -> None:
    with pytest.raises(StudyGuideNoMaterialsError):
        await study_helper_service._generate_week_summary(1, "")  # noqa: SLF001


@pytest.mark.asyncio
async def test_generate_overview_prompt_uses_only_materials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    async def fake_parse_structured_response(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(summary="Summary", key_points=[])

    monkeypatch.setattr(
        study_helper_service,
        "parse_structured_response",
        fake_parse_structured_response,
    )

    response = await study_helper_service._generate_overview(  # noqa: SLF001
        "Pointers",
        "Slides about pointers and memory.",
    )

    assert response.summary == "Summary"
    assert "course" not in str(captured["user_prompt"]).lower()
    assert "only the provided course materials" in str(captured["system_prompt"]).lower()
    assert "using only these materials" in str(captured["user_prompt"]).lower()

