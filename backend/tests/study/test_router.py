from nutrack.study.router import router


def test_study_router_keeps_prefix_and_tags() -> None:
    assert router.prefix == "/study"
    assert router.tags == ["study"]

