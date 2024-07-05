import pytest
from dose_instruction_parser import di_prepare

@pytest.mark.parametrize("misspelt, corrected", [
    ("five tabletts", "five tablets"),
    ("twice a dya", "twice a day")
])
def test_autocorrect(misspelt, corrected):
    assert di_prepare._autocorrect(misspelt) == corrected, \
        f"Autocorrect failed: {misspelt} should correct to {corrected}"

@pytest.mark.parametrize("start, end", [
    ("tablet(s)", "tablet s "),
    ("((test))", "  test  ")
])
def test_remove_parentheses(start, end):
    assert di_prepare._remove_parentheses(start) == end, \
        "Remove parentheses failed"

@pytest.mark.parametrize("start, end", [
    ("four-six", "four - six"),
    ("caplet/s", "caplet / s"),
    ("te-st//-h", "te - st /  /  - h")
])
def test_pad_hyphens_and_slashes(start, end):
    assert di_prepare._pad_hyphens_and_slashes(start) == end, \
        "Hyphen and slash padding failed"

@pytest.mark.parametrize("start, end", [
    ("2x20ml or 3 tablets at 8am", " 2 x 20 ml or  3  tablets at  8 am"),
    ("0.5 caplet", " 0.5  caplet"),
])
def test_pad_numbers(start, end):
    assert di_prepare._pad_numbers(start) == end, \
        "Number padding failed"

@pytest.mark.parametrize("start, end", [
    ("take half a tablet every two days", "take 0.5 a tablet every 2 days"),
    ("one or two puffs", "1 or 2 puffs"),
    ("twenty in pack", "20 in pack"),
])
def test_convert_words_to_numbers(start, end):
    assert di_prepare._convert_words_to_numbers(start) == end, \
        "Converting words to numbers failed"

@pytest.mark.parametrize("start, end", [
    ("half", "0.5"),
    ("quarter", "0.25"),
    ("1/8", "0.125"),
    ("1/3", "0.333")
])
def test_convert_fract_to_num(start, end):
    assert di_prepare._convert_fract_to_num(start) == end, \
        "Converting fractions to numbers failed"

@pytest.mark.parametrize("start, end", [
    ("take two tabs MORNING and nghit", "take 2 tablets morning and night"),
    ("half cap qh", "0.5 capsule every hour"),
    ("two puff(s)", "2 puff"),
    ("one/two with meals", "1 / 2 with meals")
])
def test_pre_process(start, end):
    assert di_prepare.pre_process(start) == end, \
        "Pre-processing yields incorrect result"