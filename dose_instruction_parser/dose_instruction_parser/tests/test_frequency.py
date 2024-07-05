import pytest
from dose_instruction_parser import di_frequency
from dose_instruction_parser.tests.conftest import DIS_SMALL

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
    ("on mon", None),
    ("qid", "Day")
])
def test_get_frequency_type(before, after):
    assert di_frequency.get_frequency_type(before) == after, \
        f"get_frequency_type failed: {before} should retun {after}"

@pytest.mark.parametrize("before_1, before_2, after", [
    ("every 6 hours", "Hour", "6 Hour"), 
    ("alternate days", "Day", "2 Day"),
    ("every hr", "Hour", "Hour"),
    ("every other week", "Week", "2 Week"),
    ("every sixth day", "Day", "6 Day"),
    ("every 2 - 3 days", "Day", "2 Day")
])
def test_add_frequency_multiple_units(before_1, before_2, after):
    assert di_frequency._add_frequency_multiple_units(before_1, before_2) == after, \
        f"get_frequency_type failed: {before_1} should retun {after}"


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

@pytest.mark.parametrize("before_1, before_2, after", [
    ([], "max", (None, None)), 
    (["2"], "min", (float(2), None)),
    (["2"], "max", (0.0, float(2))),
    (["1"], "min", (float(1), None)),
    (["6"], "max", (0.0, float(6))),
    (["2", "3"], "min", (float(2), None))
])
def test_get_bounding_num(before_1, before_2, after):
    assert di_frequency._get_bounding_num(before_1, before_2) == after, \
        f"_get_bounding_num failed: {before_1, before_2} should retun {after}"

@pytest.mark.parametrize("before_1, before_2, after", [
    ("up to 4", ["4"], (0.0, 4.0, True)), 
    ("at least 2", ["2"], (2.0, None, True)),
    ("at least", [], (None, None, True)),
    ("at least a", [], (1.0, None, True))
])
def test_check_min_max_amount(before_1, before_2, after):
    assert di_frequency._check_min_max_amount(before_1, before_2) == after, \
        f"_check_min_max_amount: {before_1, before_2} should retun {after}"

@pytest.mark.parametrize("text, nums, after", [
    ("2 to 4", [2.0 , 4.0], (2.0, 4.0, True)), 
    ("3 - 4 tablets", [3.0, 4.0], (3.0, 4.0, True)),
    ("1 - 2 to 3 tablets", [1.0, 2.0, 3.0], (1.0, 3.0, True)),
    ("1 or 2 5 ml spoons /mg", [1.0, 2.0, 5.0], (5.0, 10.0, True)),
    ("4 or 5 word mg", [4.0, 5.0], (4.0, 5.0, True))
])
def test_check_explicit_range(text, nums, after):
    assert di_frequency._check_explicit_range(text, nums) == after, \
        f"check_explicit_range failed: {text, nums} should retun {after}"


@pytest.mark.parametrize("before, after", [
    ("6 hourly", (1.0, 1.0, "6 Hour")), 
    ("3 hrly", (1.0, 1.0, "3 Hour")),
    ("4 hrly or 5 hrly", (1.0, 1.0, "4 Hour"))
])      
def test_get_hourly_adjusted_frequency(before, after):
    assert di_frequency._get_hourly_adjusted_frequency(before) == after, \
        f"_get_hourly_adjusted_frequency failed: {before} should retun {after}"

@pytest.mark.parametrize("before, after", [
    ("daily", (1.0, 1.0, "Day")), 
    ("with meals and at bedtime", (4.0, 4.0, "Day")),
    ("2 to 5 times a week", (2.0, 5.0, "Week")),
    ("1 or 2 times every 4 weeks", (1.0, 2.0, "Month")),
    ("6 hrly", (1.0, 1.0, "6 Hour")),
    ("3 times", (3.0, 3.0, None)),
    ("3 4 5 times", (3.0, 5.0, None)),
    ("hello", (1.0, 1.0, None)),
])      
def test_get_frequency_info(before, after):
    assert di_frequency.get_frequency_info(before) == after, \
        f"get_frequency_info failed: {before} should retun {after}"        

@pytest.mark.parametrize("before, after", [
    ("8 am and 6pm", (2.0, 2.0, True)), 
    ("1am and 7 pm and midnight", (3.0, 3.0, True)),
    ("4 / d", (4.0, 4.0, True)),
    ("14 times daily", (None, None, False))
])      
def test_check_range_from_list(before, after):
    assert di_frequency._check_range_from_list(before) == after, \
        f"_check_range_from_list failed: {before} should return {after}"