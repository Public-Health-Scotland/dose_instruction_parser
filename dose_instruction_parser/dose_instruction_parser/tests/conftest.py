import pytest
from spacy import load

from dose_instruction_parser.parser import StructuredDI

DIS_SMALL = ("take 2 tablets twice daily",
            "one puff morning and night",
            "take half after meals and at night time for three weeks",
            "1 bd as required")

OUTPUT_DIS_SMALL = [
    StructuredDI(
        inputID=0,
        text="take 2 tablets twice daily",
        form="tablet",
        dosageMin=2.0, dosageMax=2.0,
        frequencyMin=2.0, frequencyMax=2.0,
        frequencyType="Day",
        durationMin=None, durationMax=None,
        durationType=None,
        asRequired=False, asDirected=False
    ),
    StructuredDI(
        inputID=1,
        text="one puff morning and night",
        form="puff",
        dosageMin=1.0, dosageMax=1.0,
        frequencyMin=2.0, frequencyMax=2.0,
        frequencyType="Day",
        durationMin=None, durationMax=None,
        durationType=None,
        asRequired=False, asDirected=False
    ),
    StructuredDI(
        inputID=2,
        text="take half after meals and at night time for three weeks",
        form=None,
        dosageMin=0.5, dosageMax=0.5,
        frequencyMin=4.0, frequencyMax=4.0,
        frequencyType="Day",
        durationMin=3.0, durationMax=3.0,
        durationType="Week",
        asRequired=False, asDirected=False
    ),
    StructuredDI(
        inputID=3,
        text="1 bd as required",
        form=None,
        dosageMin=1.0, dosageMax=1.0,
        frequencyMin=2.0, frequencyMax=2.0,
        frequencyType="Day",
        durationMin=None, durationMax=None,
        durationType=None,
        asRequired=True, asDirected=False
    ),
]
