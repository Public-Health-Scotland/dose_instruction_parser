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
    ("fortnightly", "2 Week"),
    ("every 3 days", "3 Day"),
    ("wk", "Week"),
    ("with breakfast", "Day"),
    ("on mon", None)
])
def test_get_frequency_type(before, after):
    assert di_frequency.get_frequency_type(before) == after, \
        f"get_frequency_type failed: {before} should retun {after}"

# test _add_frequency_multiple_units (line 95)
# called from get_frequency_type (line 89)
# will not be called on (None, None) as per line 65
@pytest.mark.parametrize("before_1, before_2, after", [
    ("every 6 hours", "Hour", "6 Hour"), 
    ("alternate days", "Day", "2 Day"),
    ("every hr", "Hour", "Hour"),
    ("every other week", "Week", "2 Week")
])
def test_add_frequency_multiple_units(before_1, before_2, after):
    assert di_frequency._add_frequency_multiple_units(before_1, before_2) == after, \
        f"get_frequency_type failed: {before_1} should retun {after}"


# test _get_number_of_times (line 130)
# called from _check_range_from_list (line 327)
# called from get_frequency_info (line 466)
@pytest.mark.parametrize("before, after", [
    ("daily", 1.0), 
    ("food", 3.0),
    ("qid", 4.0),
    ("lunch", 1.0),
    ("nocte", 1.0)
])
def test_get_number_of_times(before, after):
    assert di_frequency._get_number_of_times(before) == after, \
        f"_get_number_of_times failed: {before} should retun {after}"

# test _get_bounding_num (line 169)
# called from _check_min_max_amount (line 204)
@pytest.mark.parametrize("before_1, before_2, after", [
    ([], "max", (None, None)), 
    (["2"], "min", (float(2), None)),
    (["2"], "max", (0.0, float(2))),
    (["1"], "min", (float(1), None)),
    (["6"], "max", (0.0, float(6)))
])
def test_get_bounding_num(before_1, before_2, after):
    assert di_frequency._get_bounding_num(before_1, before_2) == after, \
        f"_get_bounding_num failed: {before_1, before_2} should retun {after}"

# test _check_min_max_amount (line 204)
# called from _get_range (line 343)
@pytest.mark.parametrize("before_1, before_2, after", [
    ("up to 4", ["4"], (0.0, 4.0, True)), 
    ("at least 2", ["2"], (2.0, None, True))
])
def test_check_min_max_amount(before_1, before_2, after):
    assert di_frequency._check_min_max_amount(before_1, before_2) == after, \
        f"_check_min_max_amount: {before_1, before_2} should retun {after}"

@pytest.mark.parametrize("before, after", [
    ("2 to 4", (2.0, 4.0, True)), 
    ("3-4 tablets", (3.0, 4.0, True))
])
def test_check_explicit_range(before, after):
    assert di_frequency._check_explicit_range(before) == after, \
        f"check_explicit_range failed: {before} should retun {after}"


@pytest.mark.parametrize("before, after", [
    ("6 hourly", (1.0, 1.0, "6 Hour"), 
    ("3 hrly", (3.0, 3.0, "3 Hour"))
])
def test_get_hourly_adjusted_frequency(before, after):
    assert di_frequency._get_hourly_adjusted_frequency(before) == after, \
        f"_get_hourly_adjusted_frequency failed: {before} should retun {after}"

        