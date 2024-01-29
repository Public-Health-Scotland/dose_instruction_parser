from spacy import load

from di_parser import parser
from di_parser.tests.conftest import DEFAULT_MODEL, DIS_SMALL, OUTPUT_DIS_SMALL

def test_parser():
    p = parser.DIParser(DEFAULT_MODEL)
    parsed_dis = p.parse_many(DIS_SMALL)
    assert len(parsed_dis) == len(DIS_SMALL), \
        "Length of input dose instructions doesn't match output"
    assert parsed_dis == OUTPUT_DIS_SMALL, \
        "Test output doesn't match expected"

def test_parse_di():
    model = load(DEFAULT_MODEL)
    for di, expected in zip(DIS_SMALL, OUTPUT_DIS_SMALL):
        assert parser._parse_di(di, model) == [expected], \
            "Parse single dose instruction doesn't match expected"


