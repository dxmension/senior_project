import pytest
from nutrack.enrollments.schedule import offerings_clash


@pytest.mark.parametrize(
    "a_days,a_time,b_days,b_time,expected",
    [
        ("MWF", "10:00 AM - 10:50 AM", "MWF", "10:00 AM - 10:50 AM", True),
        ("MWF", "10:00 AM - 10:50 AM", "TR", "10:00 AM - 10:50 AM", False),
        ("MWF", "09:00 AM - 10:00 AM", "MWF", "10:00 AM - 11:00 AM", False),
        ("MWF", "09:00 AM - 10:30 AM", "MWF", "10:00 AM - 11:00 AM", True),
        ("M", "14:00 - 15:00", "M", "14:30 - 16:00", True),
        ("M", "14:00 - 15:00", "M", "15:00 - 16:00", False),
        (None, "10:00 - 11:00", "MWF", "10:00 - 11:00", False),
        ("MWF", None, "MWF", "10:00 - 11:00", False),
        ("MWF", "10:00 - 11:00", "MWF", None, False),
    ],
)
def test_offerings_clash(a_days, a_time, b_days, b_time, expected):
    assert offerings_clash(a_days, a_time, b_days, b_time) is expected
