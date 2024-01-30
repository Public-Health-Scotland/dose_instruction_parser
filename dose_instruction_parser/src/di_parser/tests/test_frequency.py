import pytest
from di_parser import di_frequency
from di_parser.tests.conftest import DIS_SMALL

@pytest.mark.parametrize("before, after", [
    ("five tabletts", None),
    ("twice a day", None), 
    ("b/d", di_frequency._Frequency("Day", 2.0)), 
    ("qid", di_frequency._Frequency("Day", 4.0))
])
def test_get_latin_frequency(before, after):
    assert di_frequency._get_latin_frequency(before) == after, \
        f"_get_latin_frequency failed: {before} should retun {after}"

@pytest.mark.parametrize("before, after", [
    (None, None), 
    ("daily", "Day"), 
    ("nocte", "Day"),
    ("every hr", "Hour"),
    ("fortnight", "2 Week"),
    ("wk", "Week"),
    ("on mon", "Week")
])
def test_get_frequency_type(before, after):
    assert di_frequency.get_frequency_type(before) == after, \
        f"get_frequency_type failed: {before} should retun {after}"

