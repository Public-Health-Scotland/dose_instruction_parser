import pytest
from dose_instruction_parser import di_duration

@pytest.mark.parametrize("before, after", [
    ("for 5 weeks", (5.0, 5.0, "Week")),
    ("for up to a year", (0.0, 1.0, "Year")),
    ("for 2 - 3 months", (2.0, 3.0, "Month")),
    ("for week", (1.0, 1.0, "Week")),
    ("month 6", (6.0, 6.0, "Month")),
])
def test_get_duration_info(before, after):
    assert di_duration.get_duration_info(before) == after, \
        f"get_duration_info failed: {before} should return {after}"
