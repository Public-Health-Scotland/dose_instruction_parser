import pytest
from spacy import load

from dose_instruction_parser import parser
from dose_instruction_parser.tests.conftest import (
    DIS_SMALL, OUTPUT_DIS_SMALL
)

# NB requires en_edris9 model to be loaded so these tests
# aren't deployed in GitHub actions
DEFAULT_MODEL_NAME = "en_edris9"
DEFAULT_MODEL = load(DEFAULT_MODEL_NAME)

def test_parser():
    p = parser.DIParser(DEFAULT_MODEL_NAME)
    parsed_dis = p.parse_many(DIS_SMALL)
    assert len(parsed_dis) == len(DIS_SMALL), \
        "Length of input dose instructions doesn't match output"
    assert parsed_dis == OUTPUT_DIS_SMALL, \
        "Test output doesn't match expected"

def test_get_model_entities():
    model_output = DEFAULT_MODEL("take 2 tablets daily")
    ents = parser._get_model_entities(model_output)
    assert ents[0].text == "2" \
        and ents[1].text == "tablets" \
            and ents[2].text == "daily", \
        "Model entities not as expected"

def test_get_model_entities_from_text():
    ents = parser._get_model_entities_from_text(
        "take 2 tablets daily", DEFAULT_MODEL
        )
    assert ents[0].text == "2" \
        and ents[1].text == "tablets" \
            and ents[2].text == "daily", \
        "Model entities not as expected"

def test_parse_di():
    for di, expected in zip(DIS_SMALL, OUTPUT_DIS_SMALL):
        expected.inputID = None
        assert parser._parse_di(di, DEFAULT_MODEL) == [expected], \
            "Parse single dose instruction doesn't match expected"

@pytest.mark.parametrize("text, instr_num", [
    ("take 1 tablet daily for 3 days then 2 daily for 4 weeks", 2),
    ("3 puffs bd for 1 week followed by 2 puffs for 2 weeks then 1 puff thereafter", 3),
    ("take morning, noon and night, max 8 in 24h", 1),
#    ("2 5ml spoonfuls daily total daily dose 10ml", 1)
])
def test_split_entities_for_multiple_instructions(text, instr_num):
    ents = parser._get_model_entities_from_text(
        text,
        DEFAULT_MODEL
    )
    out = parser._split_entities_for_multiple_instructions(ents)
    assert len(out) == instr_num, \
        f"Should be {instr_num} separate instructions detected"

@pytest.mark.parametrize("di_1, di_2, combined", [
    # Adding frequency types
    ({"DOSAGE": "1", "FREQUENCY": "in the morning", "FORM": "tablet", 
            "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None},
    {"DOSAGE": "1", "FREQUENCY": "in the evening", "FORM": None, 
            "DURATION": "for 3 weeks", "AS_REQUIRED": None, "AS_DIRECTED": None},
    {"DOSAGE": "1", "FREQUENCY": "in the morning and in the evening", "FORM": "tablet", 
            "DURATION": "for 3 weeks", "AS_REQUIRED": None, "AS_DIRECTED": None}
    ),
    # Adding dosages
    ({"DOSAGE": "1", "FREQUENCY": "day", "FORM": "tablet", 
            "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None},
    {"DOSAGE": "3", "FREQUENCY": "day", "FORM": None, 
            "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None},
    {"DOSAGE": "1 and 3", "FREQUENCY": "day", "FORM": "tablet", 
            "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None}
    )
])
def test_combine_split_dis(di_1, di_2, combined):
    assert parser._combine_split_dis([di_1, di_2]) == [combined], \
        "Split dose instructions not combined correctly"

def test_create_structured_di():
    free_text = "1 tablet a day and 3 tablets a day prn for 1 month"
    model_entities = {"DOSAGE": "1 and 3", "FREQUENCY": "day", "FORM": "tablet", 
            "DURATION": "1 month", "AS_REQUIRED": "prn", "AS_DIRECTED": None}
    expected_di = parser.StructuredDI(None, free_text, "tablet", 4.0, 4.0, 1.0, 1.0,
                        "Day", 1.0, 1.0, "Month", True, False)
    str_di = parser._create_structured_di(free_text, model_entities)
    assert str_di == expected_di, \
        "Structured di not created as expected"

def test_create_structured_dis():
    free_text = "2 - 3 5 ml spoonfuls with meals and at bedtime for 3 weeks as dir, \
        then reduce down to 1 5 ml spoonful bd"
    model_output = DEFAULT_MODEL(free_text)
    exp_dis = [
        parser.StructuredDI(None, free_text, "ml", 10.0, 15.0, 4.0, 4.0, "Day",
            3.0, 3.0, "Week", False, True),
        parser.StructuredDI(None, free_text, "ml", 5.0, 5.0, 2.0, 2.0, "Day",
            None, None, None, False, True)
    ]
    assert parser._create_structured_dis(free_text, model_output) == exp_dis, \
        "Structured dis don't match expected"

