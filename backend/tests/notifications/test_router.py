from nutrack.notifications.router import router


def test_notifications_router_keeps_prefix_and_tags() -> None:
    assert router.prefix == "/notifications"
    assert router.tags == ["notifications"]
