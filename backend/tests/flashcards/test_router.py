from nutrack.flashcards.router import router


def test_flashcards_router_keeps_prefix_and_tags() -> None:
    assert router.prefix == "/flashcards"
    assert router.tags == ["flashcards"]

