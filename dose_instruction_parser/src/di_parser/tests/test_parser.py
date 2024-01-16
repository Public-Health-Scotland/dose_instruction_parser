from di_parser import parser
from di_parser.tests.conftest import DEFAULT_MODEL, DIS_SMALL

def test_parser():
    p = parser.DIParser(DEFAULT_MODEL)
    parsed_dis = p.parse_many(DIS_SMALL)
    assert len(parsed_dis) == len(DIS_SMALL), \
        "Length of input dose instructions doesn't match output"

