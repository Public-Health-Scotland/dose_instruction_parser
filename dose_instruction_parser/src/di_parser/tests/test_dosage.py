import pytest
from di_parser import di_dosage
from di_parser.tests.conftest import DIS_SMALL


@pytest.mark.parametrize("before, after", [
    ("2 tablets", "tablets"),
    ("30ml spoonful", "spoonful"),
    ("1 puff", "puff")
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
    ("10 - 20 mg", (10.0, 20.0, "mg"))
])
def test_get_continuous_dose(before, after):
    assert di_dosage._get_continuous_dose(before) == after, \
        f"get_continuous_dose failed: {before} should correct to {after}"

@pytest.mark.parametrize("before, after", [
    ("2 x 10 ml", (20.0, 20.0, "ml")),
    ("2 - 3", (2.0, 3.0, None)),
    ("max 4", (0.0, 4.0, None))
])

def test_dosage_info(before, after):
    assert di_dosage.get_dosage_info(before) == after, \
        f"dosage_info failed: {before} should correct to {after}"        