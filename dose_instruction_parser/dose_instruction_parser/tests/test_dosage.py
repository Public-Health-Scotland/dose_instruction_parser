import pytest
from dose_instruction_parser import di_dosage
from dose_instruction_parser.tests.conftest import DIS_SMALL

@pytest.mark.parametrize("before, after", [
    ("3", True),
    ("2.012", True),
    ("1 puff", False)
])
def test_is_str_float(before, after):
    assert di_dosage._is_str_float(before) == after, \
        f"_is_str_float failed: {before} should yield {after}"

@pytest.mark.parametrize("before, after", [
    ("2 tablets", "tablets"),
    ("30ml spoonful", "spoonful"),
    ("1 puff", "puff"),
    ("1 8 tablets", None)
])
def test_get_form_from_dosage_tag(before, after):
    assert di_dosage._get_form_from_dosage_tag(before) == after, \
        f"get_form_from_dosage_tag failed: {before} should correct to {after}"

@pytest.mark.parametrize("before, after", [
    ("tablets", "tablet"),
    ("pill", "pill"),
    ("puffs", "puff"),
    ("octopodes", "octopus")
])
def test_to_singular(before, after):
    assert di_dosage._to_singular(before) == after, \
        f"to_singular failed: {before} should correct to {after}"


@pytest.mark.parametrize("before, after", [
    ("3 5 ml spoonfuls", (15.0, 15.0, "ml")),
    ("1 tablet", (None, None, None)),
    ("10 - 20 mg", (10.0, 20.0, "mg")),
    ("3 mg something ml", (3.0, 3.0, "mg")),
    ("ml spoonfuls", (None, None, "ml"))
])
def test_get_continuous_dose(before, after):
    assert di_dosage._get_continuous_dose(before) == after, \
        f"get_continuous_dose failed: {before} should correct to {after}"

@pytest.mark.parametrize("before, after", [
    ("2 x 10 ml", (20.0, 20.0, "ml")),
    ("2 - 3", (2.0, 3.0, None)),
    ("max 4", (0.0, 4.0, None)),
    ("2", (2.0, 2.0, None)),
    ("8 something 1", (1.0, 8.0, None)),
    ("no number", (None, None, None))
])
def test_dosage_info(before, after):
    assert di_dosage.get_dosage_info(before) == after, \
        f"dosage_info failed: {before} should correct to {after}"        