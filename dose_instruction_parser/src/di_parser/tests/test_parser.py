import pytest
from spacy import load

from di_parser import parser
from di_parser.tests.conftest import (
    DEFAULT_MODEL_NAME, DEFAULT_MODEL,
    DIS_SMALL, OUTPUT_DIS_SMALL
)

def test_parser():
    p = parser.DIParser(DEFAULT_MODEL_NAME)
    parsed_dis = p.parse_many(DIS_SMALL)
    assert len(parsed_dis) == len(DIS_SMALL), \
        "Length of input dose instructions doesn't match output"
    assert parsed_dis == OUTPUT_DIS_SMALL, \
        "Test output doesn't match expected"
    assert p.parse_many_async(DIS_SMALL) == parsed_dis, \
        "Asynchronous parsing yields different result"

def test_parse_di():
    for di, expected in zip(DIS_SMALL, OUTPUT_DIS_SMALL):
        assert parser._parse_di(di, DEFAULT_MODEL) == [expected], \
            "Parse single dose instruction doesn't match expected"

def test_parse_dis():
    assert parser._parse_dis(DIS_SMALL, DEFAULT_MODEL) == OUTPUT_DIS_SMALL, \
        "_parse_dis doesn't match expected"
    assert parser._parse_dis_mp(DIS_SMALL, DEFAULT_MODEL) == OUTPUT_DIS_SMALL, \
        "_parse_dis_mp doesn't match expected"

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

def test_combine_split_dis():
    di_1 = {"DOSAGE": "1", "FREQUENCY": "in the morning", "FORM": "tablet", 
            "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None}
    di_2 = {"DOSAGE": "1", "FREQUENCY": "in the evening", "FORM": None, 
            "DURATION": "for 3 weeks", "AS_REQUIRED": None, "AS_DIRECTED": None}
    combined = {"DOSAGE": "1", "FREQUENCY": "in the morning and in the evening", "FORM": "tablet", 
            "DURATION": "for 3 weeks", "AS_REQUIRED": None, "AS_DIRECTED": None}

    assert parser._combine_split_dis([di_1, di_2]) == [combined], \
        "Split dose instructions not combined correctly"