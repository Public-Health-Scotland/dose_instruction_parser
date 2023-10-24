import sys
import spacy
from dataclasses import dataclass
import re
from spacy import Language
import copy
import os
import warnings

# Local import of postprocess functions
import di_parser.parserfuncs.prepare as pprepare
import di_parser.parserfuncs.dosage as pdosage
import di_parser.parserfuncs.frequency as pfrequency
import di_parser.parserfuncs.duration as pduration

@dataclass
class StructuredDI:
    """
    A structured dose instruction
    Attributes:
    -----------
    form: str
        The form of drug (e.g. "tablet", "patch", "injection")
    dosageMin: float
        The minimum dosage 
    dosageMax: floata
        The maximum dosage 
    frequencyMin: float
        The minimum frequency 
    frequencyMax: float
        The maximum frequency 
    frequencyType : str
        The type of frequency for the dosage (e.g. Hour, Day, Week, Month).
    durationMin: float
        The minimum duration of treatment 
    durationMax: float
        The maximum duration of treatment
    durationType: str
        The type of duration for dosage (e.g. Day, Week, Month)
    asRequired : bool
        Whether to take as required / as needed
    asDirected: bool
        Whether to take as directed
    """
    form: str
    dosageMin: float
    dosageMax: float
    frequencyMin: float
    frequencyMax: float
    frequencyType: str
    durationMin: float
    durationMax: float
    durationType: str
    asRequired: bool
    asDirected: bool

def _get_model_entities(model_output):
    """
    Retrieve the entities from model output.
    Create model output by:
        model = spacy.load_model("my_model")
        model_output = model("my dose instruction")
    """
    entities = model_output.ents
    return entities

def _parse_di(di: str, model: Language):
    """
    1. Preprocesses dose instruction
    2. Applies model to retrieve entities
    3. Creates structured dose instruction from entities using static rules
    """
    di_preprocessed = pprepare._pre_process(di)
    model_output = model(di_preprocessed)
    return _create_structured_dis(model_output)

def _parse_dis(di_lst, model: Language):
    """
    Parses multiple dose instructions at once
    """
    return pprepare._flatmap(lambda di: _parse_di(di, model), di_lst)

#TODO: Improve splitting
def _split_entities_for_multiple_instructions(model_entities):
    """
    Automatically determines if multiple dose instructions are included
    within one input dose instruction. If so, splits up the dose instruction.
    """
    result = []
    seen_labels = set()
    current_sublist = []
    for entity in model_entities:
        # Ignore some entities 
        if entity.label_ in ["DRUG", "STRENGTH", "ROUTE"]:
            continue
        elif entity.label_ in seen_labels:
            result.append(current_sublist)
            current_sublist = []
            seen_labels.clear()
        current_sublist.append(entity)
        seen_labels.add(entity.label_)
    result.append(current_sublist)
    return result


def _create_structured_di(model_entities, form=None, asRequired=False, asDirected=False):
    """
    Creates a StructuredDI from model entities.
    """
    structured_di = StructuredDI(form, None, None, None, None, 
                                    None, None, None, None, asRequired, asDirected)
    for entity in model_entities:
        text = entity.text
        label = entity.label_
        if label == 'FORM':
            print("FORM: " + text)
            if structured_di.form is None:
                form = pdosage._to_singular(text)
                if form is not None:
                    structured_di.form = form
        elif label == 'DOSAGE':
            print("DOSAGE: " + text)
            min, max, form, = pdosage._get_dosage_info(text)
            structured_di.dosageMin = min
            structured_di.dosageMax = max
            if form is not None:
                structured_di.form = form
        elif label == 'FREQUENCY':
            print("FREQUENCY: " + text)
            min, max, freqtype = pfrequency._get_frequency_info(text)
            structured_di.frequencyMin = min
            structured_di.frequencyMax = max
            if freqtype is not None:
                structured_di.frequencyType = freqtype
        elif label == 'DURATION':
            print("DURATION: " + text)
            min, max, durtype = pduration._get_duration_info(text)
            structured_di.durationMin = min
            structured_di.durationMax = max
            structured_di.durationType = durtype
        elif label == "AS_REQUIRED":
            print("AS_REQUIRED: " + text)
            structured_di.asRequired = True
        elif label == "AS_DIRECTED":
            print("AS_DIRECTED: " + text)
            structured_di.asDirected = True
        else:
            continue
    return structured_di

def _create_structured_dis(model_output):
    """
    Creates StructuredDIs from a model output.
    1. Gets entities
    2. Determines whether multiple instructions present 
    3. Creates a StructuredDI for each instruction
    """
    entities = _get_model_entities(model_output)
    multiple_instructions = _split_entities_for_multiple_instructions(entities)
    first_di = _create_structured_di(multiple_instructions[0])
    # incase multiple instructions exist, they apply to the same drug and form
    other_dis = [_create_structured_di(instruction_entities, 
                                         first_di.form, first_di.asRequired,
                                         first_di.asDirected)
                  for instruction_entities in multiple_instructions[1:]]
    return [first_di] + other_dis


class DIParser:
    """
    Dose instruction parser class 

    Example
    -------
    >>> model_path = "***REMOVED***models/"
    >>> di_parser = DIParser(model_name=f"{model_path}/original/model-best")

    >>> di = "take 2 3ml spoonfuls with meals for 5-6 weeks as discussed"
    >>> parsed_di = di_parser.parse(di)
    >>> parsed_di
    [StructuredDI(form='ml', dosageMin=6.0, dosageMax=6.0, 
        frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day',
         durationMin=5.0, durationMax=6.0, durationType='Week', 
         asRequired=False, asDirected=True)]
    """
    def __init__(self, model_name):
        self.__language = spacy.load(model_name)
    def parse(self, di: str):
        return _parse_di(di, self.__language)
    def parse_many(self, dis: list):
        return _parse_dis(dis, self.__language)


model_path = "***REMOVED***models/"
di_parser = DIParser(model_name=f"{model_path}/original/model-best")
